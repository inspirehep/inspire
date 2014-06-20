# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2012, 2013, 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""APS harvester.

Gets full-text documents from APS via DOI or recid and creates
MARCXML upload of references and attached fulltext and metadata XML for records
the ALREADY exists in the repository.
"""

import sys
import re
import datetime

from invenio.jsonutils import json
from invenio.bibtask import (write_message,
                             task_update_progress,
                             task_set_task_param)
from invenio.shellutils import split_cli_ids_arg
from invenio.bibdocfile import open_url
from invenio.search_engine import (perform_request_search,)
from invenio.apsharvest_dblayer import (fetch_last_updated,
                                        get_all_new_records,
                                        get_all_modified_records,
                                        store_last_updated)
from invenio.apsharvest_utils import (validate_date,
                                      get_record_from_doi,
                                      )
from invenio.apsharvest_config import (CFG_APSHARVEST_SEARCH_COLLECTION,
                                       CFG_APSHARVEST_BUNCH_SIZE)
from invenio.apsharvest_engine import (APSHarvestJob,
                                       APSRecordList,
                                       APSRecord,
                                       )
from invenio.apsharvest_errors import (APSHarvesterSearchError,
                                       APSHarvesterConnectionError,
                                       )


try:
    from invenio.config import CFG_APSHARVEST_DIR
except ImportError:
    CFG_APSHARVEST_DIR = "/afs/cern.ch/project/inspire/uploads/aps"


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

    # Unify all parameters into a dict using locals
    parameters = locals()

    # 1: We analyze parameters and fetch all requested records from APS
    final_record_list, new_harvest_date = get_records_to_harvest(parameters)
    write_message("Found %d record(s) to download." % (len(final_record_list),))

    if reportonly:
        write_message("'Report-only' mode. We exit now.")
        return

    if not final_record_list:
        # No records to harvest, quit.
        write_message("Nothing to harvest.")
        return

    # 2: Extract fulltext/metadata XML and upload bunches of
    #    records as configured
    job = APSHarvestJob(CFG_APSHARVEST_DIR)
    count = process_records(job,
                            parameters,
                            final_record_list)

    if parameters.get("from_date") == "last":
        # Harvest of new records from APS successful
        # we update last harvested date
        store_last_updated(None,
                           new_harvest_date,
                           name="apsharvest_api_download")
    # We are done
    write_message("Harvested %d records. (%d failed)"
                  % (count, len(job.records_failed)))


def get_records_to_harvest(parameters):
    """ Get APSRecord to harvest.

    Using the given parameters dict (from bst_apsharvest), we check how
    to get the list of records to process.

    Returns a tuple of (record_list, date_checked) where record_list is
    the list of APSRecord instances and date_checked is the datetime when
    checking was done.
    """
    # This is the list of APSRecord objects to be harvested.
    final_record_list = APSRecordList()
    new_harvest_date = None

    if parameters.get("threshold_date"):
        # Input from user. Validate date
        try:
            harvest_from_date = validate_date(parameters.get("threshold_date"))
        except ValueError, e:
            write_message("Error parsing from_date, use (YYYY-MM-DD): %s" %
                          (str(e),),
                          stream=sys.stderr)
            raise

    if parameters.get("from_date"):
        # We get records from APS directly
        perpage = 100

        # Are we harvesting from last time or a specific date?
        if parameters.get("from_date") == "last":
            dummy, harvest_from_date = fetch_last_updated(name="apsharvest_api_download")

            # Keeping current time until completed harvest.
            new_harvest_date = datetime.datetime.now()
        else:
            # Input from user. Validate date
            try:
                harvest_from_date = validate_date(parameters.get("from_date"))
            except ValueError, e:
                write_message("Error parsing from_date, use (YYYY-MM-DD): %s" %
                              (str(e),),
                              stream=sys.stderr)
                raise

        # Turn harvest_from_date back into a string (away from datetime object)
        harvest_from_date = harvest_from_date.strftime("%Y-%m-%d")

        status_message = "Checking for new records from APS from %s" % \
                         (harvest_from_date,)
        if parameters.get("until_date"):
            # Input from user. Validate date
            try:
                validate_date(parameters.get("until_date"))
            except ValueError, e:
                write_message("Error parsing until_date, use (YYYY-MM-DD): %s" %
                              (str(e),),
                              stream=sys.stderr)
                raise
            status_message += " until %s" % (parameters.get("until_date"),)
        else:
            status_message += " until today"
        write_message(status_message)

        final_record_list = harvest_aps(harvest_from_date,
                                        parameters.get("until_date"),
                                        perpage)
    else:
        # We use any given IDs or records from the local Invenio instance.
        if len(parameters.get("dois")) > 0:
            write_message("Parsing DOIs...")

            # We are doing DOIs, we need to get record ids
            for doi in parameters.get("dois").split(','):
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

        if len(parameters.get("recids")) > 0:
            write_message("Parsing record IDs...")

            # We are doing rec ids
            recids = split_cli_ids_arg(parameters.get("recids"))
            for recid in recids:
                final_record_list.append(APSRecord(recid))

        if parameters.get("query"):
            write_message("Performing a search query...")

            # We are doing a search query, rg=0 allows the return of all results.
            result = perform_request_search(p=parameters.get("query"),
                                            cc=CFG_APSHARVEST_SEARCH_COLLECTION,
                                            of='id',
                                            rg=0,
                                            wl=0)
            for recid in result:
                final_record_list.append(APSRecord(recid))

        if parameters.get("records") in ("new", "modified", "both"):
            write_message("Fetching records to update...")

            # We fetch records from the database
            last_recid, last_date = fetch_last_updated(name="apsharvest")
            records_found = []
            if parameters.get("records") == "new":
                records_found = get_all_new_records(since=last_date,
                                                    last_recid=last_recid)
            elif parameters.get("records") == "modified":
                records_found = get_all_modified_records(since=last_date,
                                                         last_recid=last_recid)
            elif parameters.get("records") == "both":
                records_found.extend(get_all_new_records(since=last_date,
                                                         last_recid=last_recid))
                records_found.extend(get_all_modified_records(since=last_date,
                                                              last_recid=last_recid))

            for recid, date in records_found:
                final_record_list.append(APSRecord(recid, date=date))

    return final_record_list, new_harvest_date


def process_records(job, parameters, final_record_list):
    """ Process given records with parameters.

    Process records by using the perform_fulltext_harvest generator which
    downloads the article packages, unzip's them and returns a record
    object.

    For every record object, we assign it to a list of new records or,
    if matching is done, to a list of records to update. These records are
    also written to a result file and submitted via e-mail and/or FTP.
    """
    # Create working directory if not exists
    count = 0
    bunch = "email" not in [parameters.get("new_mode"),
                            parameters.get("update_mode")]

    for record, error_message in job.perform_fulltext_harvest(final_record_list,
                                                              parameters):
        if error_message:
            job.records_failed.append((record, error_message))
            continue
        job.records_harvested.append(record)
        count += 1

        # Depending on the bunch size, we start submitting or just continue
        # to harvest next record.
        if bunch and len(job.records_harvested) != CFG_APSHARVEST_BUNCH_SIZE:
            # Go over next bunch and add to totals
            job.process_record_submission(parameters, bunch=True)
            job.reset_bunch()

    # Are there any remaining records to submit?
    if job.check_for_records():
        job.process_record_submission(parameters)

    return count


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


if __name__ == '__main__':
    bst_apsharvest(from_date="2014-05-05",
                   until_date="2014-05-06",
                   threshold_date='2014-05-04')
