# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""APS harvester.

Gets full-text documents from APS via DOI or recid and creates
MARCXML upload of references and attached fulltext and metadata XML for records
the ALREADY exists in the repository.
"""

import sys
import os
import time
import traceback
import re
import datetime
import shutil

from bs4 import BeautifulSoup

from invenio.jsonutils import json
from invenio.shellutils import split_cli_ids_arg, \
    run_shell_command
from invenio.mailutils import send_email
from invenio.bibtask import task_update_status, \
    write_message, \
    task_update_progress, \
    task_low_level_submission, \
    task_sleep_now_if_required, \
    task_set_task_param
from invenio.config import CFG_SITE_SUPPORT_EMAIL
from invenio.bibdocfile import open_url
from invenio.search_engine import perform_request_search, search_pattern
from invenio.bibformat_engine import BibFormatObject
from invenio.filedownloadutils import download_url, InvenioFileDownloadError
from invenio.apsharvest_dblayer import fetch_last_updated, \
    get_all_new_records, \
    get_all_modified_records, \
    store_last_updated, \
    can_launch_bibupload

from invenio.apsharvest_utils import (unzip,
                                      find_and_validate_md5_checksums,
                                      get_temporary_file,
                                      InvenioFileChecksumError,
                                      remove_dtd_information,
                                      convert_xml_using_saxon,
                                      APSHarvesterConversionError,
                                      create_records_from_file,
                                      create_records_from_string,
                                      validate_date,
                                      get_file_modified_date,
                                      compare_datetime_to_iso8601_date,
                                      create_work_folder)

from invenio.apsharvest_config import CFG_APSHARVEST_FULLTEXT_URL, \
    CFG_APSHARVEST_SEARCH_COLLECTION, \
    CFG_APSHARVEST_RECORD_DOI_TAG, \
    CFG_APSHARVEST_MD5_FILE, \
    CFG_APSHARVEST_FFT_DOCTYPE, \
    CFG_APSHARVEST_REQUEST_TIMEOUT, \
    CFG_APSHARVEST_BUNCH_SIZE

from invenio.docextract_record import BibRecord, BibRecordControlField

try:
    from invenio.config import CFG_APSHARVEST_XSLT
except ImportError:
    CFG_APSHARVEST_XSLT = "/afs/cern.ch/project/inspire/xslt/aps.xsl"

try:
    from invenio.config import CFG_APSHARVEST_EMAIL
except ImportError:
    CFG_APSHARVEST_EMAIL = "desydoc@desy.de"

try:
    from invenio.config import CFG_APSHARVEST_DIR
except ImportError:
    CFG_APSHARVEST_DIR = "/afs/cern.ch/project/inspire/uploads/aps"


class APSHarvesterSearchError(Exception):
    """Exception raised when more then one record is found while DOI matching.
    """
    pass


class APSHarvesterConnectionError(Exception):
    """Exception raised when unable to connect to APS servers.
    """
    pass


class APSHarvesterSubmissionError(Exception):
    """Exception raised when unable to submit new/updated records.
    """
    pass


class APSHarvesterFileExits(Exception):
    """Exception raised when local file is the newest.
    """
    pass


class APSRecordList(list):
    """
    Class representing the list of records to harvest.
    """
    def __init__(self):
        super(APSRecordList, self).__init__()
        self.recids = []

    def append(self, record):
        """
        Append a APSRecord to the list if it is not already there.
        """
        if record.recid not in self.recids:
            super(APSRecordList, self).append(record)
            self.recids.append(record.recid)


class APSRecord(object):
    """
    Class representing a record to harvest.
    """
    def __init__(self, recid, doi=None, date=None, last_modified=None):
        self.recid = recid
        self.doi = doi or get_doi_from_record(self.recid)
        self.date = date
        self.record = BibRecord(recid or None)
        self.last_modified = last_modified

    def add_metadata(self, marcxml_file):
        """
        Adds metadata from given file. Removes any DTD definitions
        and translates the metadata to MARCXML using BibConvert.
        """
        if marcxml_file:
            self.record = create_records_from_file(marcxml_file)
            if self.recid:
                self.record['001'] = [BibRecordControlField(str(self.recid))]

    def add_metadata_by_string(self, marcxml_text):
        """
        Adds metadata from given text.
        """
        if marcxml_text:
            self.record = create_records_from_string(marcxml_text)
            if self.recid:
                self.record['001'] = [BibRecordControlField(str(self.recid))]

    def add_fft(self, fulltext_file, hidden=True):
        """
        Adds FFT information as required from given fulltext.
        """
        fft = self.record.add_field("FFT__")
        fft.add_subfield('a', fulltext_file)

        if hidden:
            fft.add_subfield('t', CFG_APSHARVEST_FFT_DOCTYPE)
            fft.add_subfield('o', "HIDDEN")
        else:
            fft.add_subfield('t', "INSPIRE-PUBLIC")

    def to_xml(self):
        return self.record.to_xml()


def bst_apsharvest(dois="", recids="", query="", records="", new_mode="email",
                   update_mode="email", from_date="", until_date=None,
                   metadata="yes", fulltext="yes", hidden="yes", match="no",
                   reportonly="no", threshold_date=None, devmode="no"):
    """
    Task to download APS metadata + fulltext given a list of arguments.

    Operates in two ways:

        1. Harvesting of new/updated metadata+fulltext from APS via REST API

           This means that new records are being looked for at APS servers.
           Active when from_date and until_date is given, in addition when
           a DOI not already in the system is given.

           If the value "last" is given to from_date the harvester will harvest
           any new records since last run.

           If match is set to "yes" the records harvested will be matched against
           the database and split into "new" and "updated" records.

        2. Attachment of fulltext only from APS for existing records

           When the records to be processed already exists in the system, the
           task only harvests the fulltext's themselves and attaches them
           to the records.


    Examples:

    Get full update for existing records via record identifier:
    >>> bst_apsharvest(recids="13,513,333")

    Get full update for existing records via a search query and unhide fulltext:
    >>> bst_apsharvest(query="find j prstab", hidden="no")

    Get metadata only update for an existing doi:
    >>> bst_apsharvest(dois="10.1103/PhysRevB.87.235401", fulltext="no")

    Get fulltext only update for a record and append to record:
    >>> bst_apsharvest(recids="11139", metadata="no", update_mode="append")

    Get new records from APS, send update to holding pen and email new records
    >>> bst_apsharvest(from_date="last", update_mode="o")

    Get records from APS updated between given dates, insert new and correct
    >>> bst_apsharvest(from_date="2013-06-03", until_date="2013-06-04",
                       new_mode="insert", update_mode="correct")


    @param dois: comma-separated list of DOIs to download fulltext/metadata for.
    @type dois: string

    @param recids: comma-separated list of recids of record containing
                   a DOI to download fulltext for.
    @type recids: string

    @param query: an Invenio search query of records to download fulltext for.
    @type query: string

    @param records: get any records modified, created or both since last time
                    in the database to download fulltext for, can be either:
                    "new" - fetches all new records added
                    "modified" - fetches all modified records added
                    "both" - both of the above
    @type records: string

    @param new_mode: which mode should the fulltext files be submitted in:
                "email" - does NOT run bibupload and sends an email instead. Default.
                "insert" - inserts the records into the database
                "append" - appends the fulltext to the existing attached files
                "correct" - corrects existing attached fulltext files, or adds new
                "replace" - replaces all attached files with new fulltext file

                The fulltext is appended by default to new records.
    @type mode: string


    @param update_mode: which mode should the fulltext files be submitted in:
                "email" - does NOT run bibupload and sends an email instead. Default.
                "insert" - inserts the records into the database
                "append" - appends the fulltext to the existing attached files
                "correct" - corrects existing attached fulltext files, or adds new
                "replace" - replaces all attached files with new fulltext file

                The fulltext is appended by default to new records.
    @type mode: string

    @param from_date: ISO date for when to harvest records from. Ex. 2013-01-01
                      If the value is "last" it means to get records since last
                      harvest.
    @type from_date: string

    @param until_date: ISO date for when to harvest records until. Ex. 2013-01-01
    @type until_date: string

    @param fulltext: should the record have fulltext attached? "yes" or "no"
    @type fulltext: string

    @param hidden: should the fulltext be hidden when attached? "yes" or "no"
    @type hidden: string

    @param match: should a simple match with the database be done? "yes" or "no"
    @type match: string

    @param reportonly: only report number of records to harvest, then exit? "yes" or "no"
    @type reportonly: string

    @param threshold_date: ISO date for when to harvest records since. Ex. 2013-01-01
    @type threshold_date: string

    @param devmode: Activate devmode. Full verbosity and no uploads/mails.
    @type devmode: string
    """
    # This is the list of APSRecord objects to be harvested.
    final_record_list = APSRecordList()

    task_update_progress("Parsing input parameters")

    # Validate modes
    for mode in [new_mode, update_mode]:
        if mode not in ("append", "a", "correct", "c", "o",
                        "replace", "r", "insert", "i", "email"):
            raise Exception("Warning: given upload mode '%s' is not valid."
                            % (mode,))

    # We hide fulltext by default
    if hidden.lower() == "no":
        hidden = False
    else:
        hidden = True

    # We attach fulltext by default
    if fulltext.lower() == "no":
        fulltext = False
    else:
        fulltext = True

    # We attach meta-data by default
    if metadata.lower() == "no":
        metadata = False
    else:
        metadata = True

    # We do not match records by default
    if match.lower() == "yes":
        match = True
    else:
        match = False

    # We do not reportonly by default
    if devmode.lower() == "yes":
        devmode = True
        task_set_task_param('verbose', 9)
    else:
        devmode = False

    # We do not reportonly by default
    if reportonly.lower() == "yes":
        reportonly = True
    else:
        reportonly = False

    if threshold_date:
        # Input from user. Validate date
        try:
            harvest_from_date = validate_date(threshold_date)
        except ValueError, e:
            write_message("Error parsing from_date, use (YYYY-MM-DD): %s" %
                          (str(e),),
                          stream=sys.stderr)
            return 1

    if from_date:
        # We get records from APS directly
        new_harvest_date = None
        perpage = 100

        # Are we harvesting from last time or a specific date?
        if from_date == "last":
            dummy, harvest_from_date = fetch_last_updated(name="apsharvest_api_download")

            # Keeping current time until completed harvest.
            new_harvest_date = datetime.datetime.now()
        else:
            # Input from user. Validate date
            try:
                harvest_from_date = validate_date(from_date)
            except ValueError, e:
                write_message("Error parsing from_date, use (YYYY-MM-DD): %s" %
                              (str(e),),
                              stream=sys.stderr)
                return 1

        # Turn harvest_from_date back into a string (away from datetime object)
        harvest_from_date = harvest_from_date.strftime("%Y-%m-%d")

        status_message = "Checking for new records from APS from %s" % \
                         (harvest_from_date,)
        if until_date:
            # Input from user. Validate date
            try:
                validate_date(until_date)
            except ValueError, e:
                write_message("Error parsing until_date, use (YYYY-MM-DD): %s" %
                              (str(e),),
                              stream=sys.stderr)
                return 1
            status_message += " until %s" % (until_date,)
        else:
            status_message += " until today"
        write_message(status_message)

        final_record_list = harvest_aps(harvest_from_date, until_date, perpage)
    else:
        # We use any given IDs or records from the system.

        # Gather IDs (if any)
        if len(dois) > 0:
            write_message("Parsing DOIs...")

            # We are doing DOIs, we need to get record ids
            for doi in dois.split(','):
                doi = doi.strip()
                try:
                    recid = get_record_from_doi(doi)
                except APSHarvesterSearchError, e:
                    write_message("Error while getting recid from %s: %s" %
                                  (doi, str(e)))
                    continue
                if not recid:
                    # Record not found on the system, we harvest from APS
                    write_message("No recid found, we get record from APS")
                    recid = None
                final_record_list.append(APSRecord(recid, doi))

        if len(recids) > 0:
            write_message("Parsing record IDs...")

            # We are doing rec ids
            recids = split_cli_ids_arg(recids)
            for recid in recids:
                final_record_list.append(APSRecord(recid))

        if query:
            write_message("Performing a search query...")

            # We are doing a search query, rg=0 allows the return of all results.
            result = perform_request_search(p=query,
                                            cc=CFG_APSHARVEST_SEARCH_COLLECTION,
                                            of='id',
                                            rg=0,
                                            wl=0)
            for recid in result:
                final_record_list.append(APSRecord(recid))

        if records in ("new", "modified", "both"):
            write_message("Fetching records to update...")

            # We fetch records from the database
            last_recid, last_date = fetch_last_updated(name="apsharvest")
            records_found = []
            if records == "new":
                records_found = get_all_new_records(since=last_date,
                                                    last_recid=last_recid)
            elif records == "modified":
                records_found = get_all_modified_records(since=last_date,
                                                         last_recid=last_recid)
            elif records == "both":
                records_found.extend(get_all_new_records(since=last_date,
                                                         last_recid=last_recid))
                records_found.extend(get_all_modified_records(since=last_date,
                                                              last_recid=last_recid))

            for recid, date in records_found:
                final_record_list.append(APSRecord(recid, date=date))

    write_message("Found %d record(s) to download." % (len(final_record_list),))

    if reportonly:
        write_message("'Report-only' mode. We exit now.")
        return

    if not final_record_list:
        # No records to harvest, quit.
        write_message("Nothing to harvest.")
        return

    #2: Fetch fulltext/metadata XML and upload bunches of records as configured

    # Create working directory if not exists
    out_folder = create_work_folder(CFG_APSHARVEST_DIR)

    from invenio.refextract_kbs import get_kbs
    journal_mappings = get_kbs()
    if journal_mappings and "journals" in journal_mappings:
        journal_mappings = journal_mappings['journals'][1]
    else:
        journal_mappings = None

    now = datetime.datetime.now()
    mail_subject = "APS harvest results: %s" % \
                   (now.strftime("%Y-%m-%d %H:%M:%S"),)

    count = 0
    taskid = 0
    records_harvested = []
    records_to_insert = []
    records_to_update = []
    records_failed = []
    for record, error_message in perform_fulltext_harvest(final_record_list,
                                                          metadata,
                                                          fulltext,
                                                          hidden,
                                                          out_folder,
                                                          threshold_date,
                                                          journal_mappings):
        if error_message:
            records_failed.append((record, error_message))
            continue
        records_harvested.append(record)
        count += 1
        # When in BibUpload mode, check if we are on the limit and ready to submit
        if len(records_harvested) == CFG_APSHARVEST_BUNCH_SIZE:

            # Go over next bunch and add to totals
            if match:
                new_records, existing_records = check_records(records_harvested,
                                                              out_folder)
                records_to_insert.extend(new_records)
                records_to_update.extend(existing_records)
            else:
                records_to_insert.extend(records_harvested)

            if new_mode != "email":
                # Submit new records
                record_filename = generate_xml_for_records(records_to_insert,
                                                           out_folder,
                                                           suffix="_insert.xml")
                taskid = submit_records(record_filename,
                                        records_to_insert,
                                        new_mode,
                                        out_folder,
                                        devmode=devmode,
                                        subject=mail_subject)
                if not taskid and not devmode:
                    # Something went wrong
                    err_string = "New records (%s)" \
                                 " were not submitted correctly" % \
                                 (record_filename,)
                    raise APSHarvesterSubmissionError(err_string)
                records_to_insert = []

            if update_mode != "email":
                # Submit records to be updated
                record_filename = generate_xml_for_records(records_to_update,
                                                           out_folder,
                                                           suffix="_update.xml")
                taskid = submit_records(record_filename,
                                        records_to_update,
                                        update_mode,
                                        out_folder,
                                        silent=records and True or False,
                                        devmode=devmode,
                                        subject=mail_subject)
                if not taskid and not devmode:
                    # Something went wrong
                    err_string = "Existing records (%s)" \
                                 " were not submitted correctly" % \
                                 (record_filename,)
                    raise APSHarvesterSubmissionError(err_string)
                records_to_update = []
            # Reset
            records_harvested = []

        task_sleep_now_if_required(can_stop_too=not records_harvested)

    # Check for any remains
    if records_harvested or records_to_update or records_to_insert:
        if match:
            new_records, existing_records = check_records(records_harvested,
                                                          out_folder)
            records_to_insert.extend(new_records)
            records_to_update.extend(existing_records)
        else:
            records_to_insert.extend(records_harvested)

        if records_to_insert:
            record_filename = generate_xml_for_records(records_to_insert,
                                                       out_folder,
                                                       suffix="_insert.xml")
            taskid = submit_records(record_filename,
                                    records_to_insert,
                                    new_mode,
                                    out_folder,
                                    taskid,
                                    silent=records and True or False,
                                    devmode=devmode,
                                    subject=mail_subject)
            if not taskid and not devmode:
                # Something went wrong
                write_message("Records were not submitted correctly")

        if records_to_update:
            record_filename = generate_xml_for_records(records_to_update,
                                                       out_folder,
                                                       suffix="_update.xml")
            taskid = submit_records(record_filename,
                                    records_to_update,
                                    update_mode,
                                    out_folder,
                                    taskid,
                                    silent=records and True or False,
                                    devmode=devmode,
                                    subject=mail_subject)
            if not taskid and not devmode:
                # Something went wrong
                write_message("Records were not submitted correctly")

    if records_failed:
        body = "\n".join(["%s failed with error: %s"
                          % (rec.doi or rec.recid, msg)
                          for rec, msg in records_failed])
        if not devmode:
            submit_records_via_mail(subject="%s (failed records)" % (mail_subject,),
                                    body=body)

    if from_date == "last":
        # Harvest of new records from APS successful
        # we update last harvested date
        store_last_updated(None,
                           new_harvest_date,
                           name="apsharvest_api_download")

    # We are done
    write_message("Harvested %d records. (%d failed)" % (count, len(records_failed)))


def APS_connect(from_param, until_param=None, page=1, perpage=100):
    """
    Manages connection to APS site and return connector.
    """
    host = 'http://harvest.aps.org'
    function = '/content/journals/articles'

    from_param = 'from=' + str(from_param)
    params = "?" + from_param
    if(until_param):
        until_param = 'until=' + str(until_param)
        params += "&"
        params += until_param

    params += "&page=" + str(page) + "&per_page=" + str(perpage)
    url_to_open = host + function + params
    retries = 0
    while retries < 5:
        retries += 1
        try:
            write_message("Tries to open URL: %s" % (url_to_open,), verbose=5)
            conn = open_url(url_to_open)
            write_message("Success!", verbose=5)
            return conn
        except StandardError, e:
            if 'urlopen' in str(e) or 'URL could not be opened' in str(e):
                write_message("Error: APS could not be reached")
                if retries < 5:
                    write_message("Retrying...")
                continue
            raise


def harvest_aps(from_param, until_param, perpage):
    """
    Performs a request to APS API servers retrieving JSON.
    """
    page = 1
    last_page = 1
    conn = APS_connect(from_param, until_param, page, perpage)
    if not conn:
        write_message("Fatal Error: Cannot reach APS servers. Aborting.")
        raise APSHarvesterConnectionError("Cannot connect to APS servers")
    if conn.headers['link']:
        links = conn.headers['link'].split(",")
        for l in links:
            if l.find('rel="next"') > 0:
                next_page = int(re.search(r'(?<=(page=))\w+', l).group(0))
            if l.find('rel="last"') > 0:
                last_page = int(re.search(r'(?<=(page=))\w+', l).group(0))

    # Fetch first page of data
    data = json.loads(conn.next())
    write_message("Data received from APS: \n%s" % (data,), verbose=5)
    records = []
    for d in data:
        records.append(APSRecord(None,
                                 d["doi"],
                                 last_modified=d['metadata_last_modified_at']))

    # Check for more pages
    if last_page > 1:
        for pagenum in range(next_page, last_page+1):
            conn = APS_connect(from_param, until_param, pagenum, perpage)
            data = json.loads(conn.next())
            write_message("Data received from APS: \n%s" % (data,), verbose=5)
            for d in data:
                records.append(APSRecord(None,
                                         d["doi"],
                                         last_modified=d['metadata_last_modified_at']))

    return records


def check_records(records, directory):
    """
    Checks if given records exists on the system and then returns
    a tuple of records that is new and records that exists:

    @return: a tuple of (new_records, existing_records)
    @rtype: tuple
    """
    # We check if any records already exists
    new_records = []
    existing_records = []
    for record in records:
        # Do we already have the record id perhaps?
        if not record.recid:
            try:
                record.recid = get_record_from_doi(record.doi)
            except APSHarvesterSearchError, e:
                write_message("Error while getting recid from %s: %s" %
                              (record.doi, str(e)))

                # Problem detected, send mail immediately:
                problem_rec = generate_xml_for_records(records=[record],
                                                       directory=directory,
                                                       suffix="problem.xml")
                now = datetime.datetime.now()
                subject = "APS harvest problem: %s" % \
                          (now.strftime("%Y-%m-%d %H:%M:%S"),)
                body = "There was a problem harvesting %s. \n %s \n Path: \n%s" % \
                       (record.doi, str(e), problem_rec)
                submit_records_via_mail(subject, body)
                continue

        # What about now?
        if record.recid:
            existing_records.append(record)
        else:
            new_records.append(record)
    return new_records, existing_records


def generate_xml_for_records(records, directory, prefix="apsharvest_result_",
                             suffix=".xml", pretty=True):
    """
    Given a list of APSRecord objects, generate a MARCXML containing Metadata
    and FFT for all of them.
    """
    new_filename = get_temporary_file(prefix=prefix,
                                      suffix=suffix,
                                      directory=directory)

    generated_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                    "<collection>\n%s\n</collection>" % \
                    ("\n".join([record.to_xml() for record in records]),)

    try:
        fd = open(new_filename, 'w')
        fd.write(generated_xml)
        fd.close()
    except IOError, e:
        write_message("\nException caught: %s" % e, sys.stderr)
        write_message(traceback.format_exc()[:-1])
        task_update_status("CERROR")
        return

    if pretty:
        return prettify_xml(new_filename)
    return new_filename


def prettify_xml(filepath):
    """
    Will prettify an XML file for better readability.

    Returns the new, pretty, file.
    """
    cmd = "xmllint --format %s" % (filepath,)
    exit_code, std_out, err_msg = run_shell_command(cmd=cmd)
    if exit_code:
        write_message("\nError caught: %s" % (err_msg,))
        task_update_status("CERROR")
        return

    new_filename = "%s.pretty" % (filepath,)
    try:
        fd = open(new_filename, 'w')
        fd.write(std_out)
        fd.close()
    except IOError, e:
        write_message("\nException caught: %s" % e, sys.stderr)
        write_message(traceback.format_exc()[:-1])
        task_update_status("CERROR")
        return

    return new_filename


def submit_bibupload_for_records(mode, new_filename, silent):
    """
    Given a list of APSRecord objects, generate a bibupload job.

    NB: we do not change the modified date of the record as we otherwise
    would be caught by ourselves again.
    """
    if len(mode) == 1:
        mode = "-" + mode
    else:
        mode = "--" + mode

    task_arguments = []
    if silent:
        task_arguments.append("--notimechange")
    task_arguments.append(mode)
    task_arguments.append(new_filename)
    return task_low_level_submission("bibupload", "apsharvest",
                                     *tuple(task_arguments))


def submit_records(records_filename, records_list, mode, directory,
                   taskid=0, silent=False, devmode=False, subject=None):
    """
    Performs the logic to submit given file (filepath) of records
    either by e-mail or using BibUpload with given mode.

    Taskid is given to indicate if the task submission should wait for any
    previously submitted tasks.

    The submission can also be made "silent" in the sense of not
    updating the modification date of the records.

    @param records_filename: filepath to XML file containing records.
    @type records_filename: string

    @param records_list: list of APSRecord objects for records
    @type records_list: list

    @param mode: which submission mode is it?
    @type mode: string

    @param taskid: bibsched taskid, wait for task to complete before submission
    @type taskid: int

    @param silent: do not update the modification date of the records
    @type silent: bool

    @return: returns the given taskid upon submission, or True/False from email.
    """
    if devmode:
        return None
    if not subject:
        now = datetime.datetime.now()
        subject = "APS harvest results: %s" % (now.strftime("%Y-%m-%d %H:%M:%S"),)

    # Check if we should create bibupload or e-mail
    if mode == "email":
        # Lets parse the records and find our IDs.
        list_of_dois = []
        for record in records_list:
            # We strip away the first part of the DOI for readability.
            list_of_dois.append('/'.join(record.doi.split('/')[1:]))
        # We send an e-mail to CFG_APSHARVEST_EMAIL and put file on AFS.
        body = "Harvested new records: %s" % (records_filename,)
        try:
            try:
                shutil.move(records_filename, directory)
                records_filename = os.path.join(directory,
                                                os.path.basename(records_filename))
                body = "Harvested new records on %s. They are located here:\n %s" % \
                       (now.strftime("%Y-%m-%d %H:%M:%S"), records_filename)
            except IOError, e:
                # Some IOError
                body = "Error while harvesting records: \nError saving %s - %s" % \
                       (records_filename, str(e))
                raise e
        finally:
            body = "%s\nRecords harvested (%s total):\n%s\n" % (body,
                                                                str(len(list_of_dois)),
                                                                "\n".join(list_of_dois))
            res = submit_records_via_mail(subject, body)
            write_message("Sent e-mail to %s with path to %s" %
                          (CFG_APSHARVEST_EMAIL, records_filename))
            return res
    else:
        # We submit a BibUpload task and wait for it to finish
        task_update_progress("Waiting for task to finish")

        if taskid != 0:
            write_message("Going to wait for %d to finish" % (taskid,))

        while not can_launch_bibupload(taskid):
            # Lets wait until the previously launched task exits.
            task_sleep_now_if_required(can_stop_too=False)
            time.sleep(5.0)

        taskid = submit_bibupload_for_records(mode, records_filename, silent)
        write_message("Submitted BibUpload task #%s with mode %s" %
                     (str(taskid), mode))
        return taskid


def submit_records_via_mail(subject, body, toaddr=CFG_APSHARVEST_EMAIL):
    """
    Performs the call to mailutils.send_email to attach XML and submit
    via e-mail to the desired receipient (CFG_APSHARVEST_EMAIL).

    @param subject: email subject.
    @type subject: string

    @param body: email contents.
    @type body: string

    @return: returns the given taskid upon submission.
    @rtype: int
    """
    return send_email(fromaddr=CFG_SITE_SUPPORT_EMAIL,
                      toaddr=toaddr,
                      subject=subject,
                      content=body)


def perform_fulltext_harvest(record_list, add_metadata, attach_fulltext,
                             hidden_fulltext, out_folder, threshold_date=None,
                             journal_mappings=None):
    """
    For every record in given list APSRecord(record ID, DOI, date last
    updated), yield a APSRecord with added FFT dictionary containing URL to
    fulltext/metadata XML downloaded locally.

    If a download is unsuccessful, an error message is given.

    @return: tuple of (APSRecord, error_message)
    """
    count = 0
    request_end = None
    request_start = None
    for record in record_list:
        task_sleep_now_if_required(can_stop_too=False)
        # Unless this is the first request, lets sleep a bit
        if request_end and request_start:
            request_dt = request_end-request_start
            write_message("Checking request time (%d)"
                          % (request_dt,), verbose=3)
            if count and request_dt > 0 and request_dt < CFG_APSHARVEST_REQUEST_TIMEOUT:
                write_message("Initiating sleep for %.1f seconds"
                              % (request_dt,), verbose=3)
                time.sleep(request_dt)

        count += 1
        task_update_progress("Harvesting record (%d/%d)" % (count,
                                                            len(record_list)))

        if not record.doi:
            msg = "No DOI found for record %d" % (record.recid or "",)
            write_message("Error: %s" % (msg,), stream=sys.stderr)
            yield record, msg
            continue

        url = CFG_APSHARVEST_FULLTEXT_URL % {'doi': record.doi}
        result_file = os.path.join(out_folder,
                                   "%s.zip" % (record.doi.replace('/', '_')))
        try:
            request_start = time.time()
            if os.path.exists(result_file):
                # File already downloaded recently, lets see if it is the same
                file_last_modified = get_file_modified_date(result_file)
                if not compare_datetime_to_iso8601_date(file_last_modified, record.last_modified):
                    # File is not older than APS version, we should not download.
                    raise APSHarvesterFileExits

            write_message("Trying to save to %s" % (result_file,), verbose=5)

            result_file = download_url(url=url,
                                       download_to_file=result_file,
                                       content_type="zip",
                                       retry_count=5,
                                       timeout=60.0)
            write_message("Downloaded %s to %s" % (url, result_file), verbose=2)
        except InvenioFileDownloadError, e:
            msg = "URL could not be opened: %s" % (url,)
            write_message("Error: %s" % (msg,),
                          stream=sys.stderr)
            yield record, msg
            continue

        except APSHarvesterFileExits:
            write_message("File exists at %s" % (result_file,), verbose=2)

        except StandardError, e:
            if 'urlopen' in str(e) or 'URL could not be opened' in str(e):
                msg = "URL could not be opened: %s" % (url,)
                write_message("Error: %s" % (msg,),
                              stream=sys.stderr)
                write_message("No fulltext found for %s" %
                             (record.recid or record.doi,))
                yield record, msg
                continue
            raise
        finally:
            request_end = time.time()

        # Unzip the compressed file
        unzipped_folder = unzip(result_file, base_directory=out_folder)

        # Validate the checksum of the compressed fulltext file.
        try:
            checksum_validated_files = find_and_validate_md5_checksums(
                in_folder=unzipped_folder,
                md5key_filename=CFG_APSHARVEST_MD5_FILE)
        except InvenioFileChecksumError, e:
            info_msg = "Skipping %s in %s" % \
                       (record.recid or record.doi, unzipped_folder)
            msg = "Error while validating checksum: %s\n%s\n%s" % \
                  (info_msg, str(e), traceback.format_exc()[:-1])
            write_message(msg)
            yield record, msg
            continue
        if not checksum_validated_files:
            write_message("Warning: No files found to perform checksum"
                          " validation on inside %s" % (unzipped_folder,))
        elif len(checksum_validated_files) != 1 or \
                not 'fulltext.xml' in checksum_validated_files[0]:
            msg = "Warning: No fulltext file found inside %s for %s" % \
                  (unzipped_folder, record.recid or record.doi)
            write_message(msg)
            yield record, msg
            continue

        # We have the fulltext file as fulltext.xml as expected.
        fulltext_file = checksum_validated_files[0]

        write_message("Harvested record %s (%s)" %
                     (record.recid or "new record", count))
        write_message("File: %s" % (fulltext_file,), verbose=2)

        # Check if published date is after treshold:
        if is_beyond_threshold_date(threshold_date, fulltext_file):
            # The published date is beyond the threshold, we continue
            msg = "Warning: Article published beyond threshold: %s" % \
                  (record.doi,)
            write_message(msg)
            yield record, msg
            continue
        else:
            write_message("OK. Record is below the threshold.", verbose=3)

        if add_metadata:
            from harvestingkit.aps_package import (ApsPackage,
                                                   ApsPackageXMLError)
            # Generate Metadata,FFT and yield it
            aps = ApsPackage(journal_mappings)
            try:
                xml = aps.get_record(fulltext_file)
                record.add_metadata_by_string(xml)
            except ApsPackageXMLError, e:
                # This must be old-format XML
                write_message("Warning: old-style metadata detected for %s" %
                              (fulltext_file))
                # Remove any DTD info in the file before converting
                cleaned_fulltext_file = remove_dtd_information(fulltext_file)
                try:
                    convert_xml_using_saxon(cleaned_fulltext_file,
                                            CFG_APSHARVEST_XSLT)

                    # Conversion is a success. Let's derive location of converted file
                    source_directory = os.path.dirname(cleaned_fulltext_file)
                    path_to_converted = "%s%s%s.xml" % \
                                        (source_directory,
                                         os.sep,
                                         record.doi.replace('/', '_'))
                    write_message("Converted meta-data for %s" %
                                 (record.recid or "new record"), verbose=2)
                    record.add_metadata(path_to_converted)
                except APSHarvesterConversionError, e:
                    msg = "Metadata conversion failed: %s\n%s" % \
                          (str(e), traceback.format_exc()[:-1])
                    write_message(msg, stream=sys.stderr)
                    yield record, msg

            write_message("Converted metadata for %s" %
                          (record.recid or "new record"), verbose=2)

        if attach_fulltext:
            record.add_fft(fulltext_file, hidden_fulltext)

        if record.date:
            store_last_updated(record.recid, record.date, name="apsharvest")

        yield record, ""


def is_beyond_threshold_date(threshold_date, fulltext_file):
    """
    Checks the given fulltext file to see if the published date is
    beyond the threshold or not. Returns True if it is beyond and
    False if not.
    """
    write_message("Checking the threshold...", verbose=3)
    with open(fulltext_file, "r") as fd:
        parsed_xml_tree = BeautifulSoup(fd, features="xml")
        # Looking for the published tag
        pub_element = parsed_xml_tree.find("pub-date", attrs={"pub-type": 'epub'})
        if not pub_element:
            # Is it old format?
            pub_element = parsed_xml_tree.find('published')
            if not pub_element:
                return False
            published_date = pub_element.get("date")
        else:
            # It is new format
            published_date = pub_element.get('iso-8601-date')
        return published_date < threshold_date
    # No published date found, impossible to check
    return False


def get_doi_from_record(recid):
    """
    Given a record ID we fetch it from the DB and return
    the first DOI found as specified by the config variable
    CFG_APSHARVEST_RECORD_DOI_TAG.

    @param recid:  record id record containing a DOI
    @type recid: string/int

    @return: first DOI found in record
    @rtype: string
    """
    record = BibFormatObject(int(recid))
    possible_dois = record.fields(CFG_APSHARVEST_RECORD_DOI_TAG[:-1])
    for doi in possible_dois:
        if '2' in doi and doi.get('2', "") == "DOI":
            # Valid DOI present, add it
            try:
                return doi['a']
            except KeyError:
                continue


def get_record_from_doi(doi):
    """
    Given a DOI we fetch the record from the DB and return
    tuple of record id and last record update.

    @param doi: DOI identifier to match a record against
    @type doi: string/int

    @return: record ID of record found
    @rtype: int
    """
    if not doi:
        return

    # Search pattern returns intbitset, lets make it a list instead
    recids = list(search_pattern(p=doi, f=CFG_APSHARVEST_RECORD_DOI_TAG, m='e'))
    if not recids:
        return
    elif len(recids) != 1:
        raise APSHarvesterSearchError("DOI mismatch: %s did not find only 1 record: %s" %
                                      ",".join(recids))
    return int(recids[0])
