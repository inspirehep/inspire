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
MARCXML upload of references and attached fulltext XML for records
the ALREADY exists in the repository.
"""

import sys
import time
import traceback
from invenio.shellutils import split_cli_ids_arg
from invenio.bibtask import task_update_status, \
                            write_message, \
                            task_update_progress, \
                            task_low_level_submission
from invenio.config import CFG_TMPDIR
from invenio.bibdocfile import download_url
from invenio.bibdocfilecli import ffts_to_xml
from invenio.search_engine import perform_request_search, \
                                  search_pattern
from invenio.bibformat_engine import BibFormatObject

from invenio.apsharvest_dblayer import fetch_last_updated, \
                                       get_all_new_records, \
                                       get_all_modified_records, \
                                       store_last_updated
from invenio.apsharvest_utils import unzip, \
                                     find_and_validate_md5_checksums, \
                                     get_temporary_file, \
                                     InvenioFileChecksumError

from invenio.apsharvest_config import CFG_APSHARVEST_FULLTEXT_URL, \
                                      CFG_APSHARVEST_SEARCH_COLLECTION, \
                                      CFG_APSHARVEST_RECORD_DOI_TAG, \
                                      CFG_APSHARVEST_MD5_FILE, \
                                      CFG_APSHARVEST_FFT_DOCTYPE, \
                                      CFG_APSHARVEST_REQUEST_TIMEOUT


class APSHarvesterSearchError(Exception):
    """Exception raised when more then one record is found while DOI matching.
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
    def __init__(self, recid, doi=None, date=None):
        self.recid = recid
        self.doi = doi or get_doi_from_record(self.recid)
        self.date = date

    def get_data(self):
        """
        Return data as a tuple of recid, dois, date.
        """
        return self.recid, self.doi, self.date


def bst_apsharvest(dois="", recids="", query="", records="", mode="correct"):
    """
    Main function to download APS fulltext given a list of arguments:

    @param dois: comma-separated list of DOIs to download fulltext for.
    @type dois: string

    @param recids: comma-separated list of recids of record containing
                   a DOI to download fulltext for.
    @type recids: string

    @param query: an Invenio search query of records to download fulltext for.
    @type query: string

    @param records: which records to collect since last harvest, can be either:
                    "new" - fetches all new records added
                    "modified" - fetches all modified records added
                    "both" - both of the above

    @param mode: which mode should the fulltext files be uploaded in:
                    "append" - adds the fulltext to the existing attached files
                    "correct" - corrects existing attached fulltext files, or adds new
                    "replace" - replaces all attached files with new fulltext file

    @type records: string
    """
    # This is the list of APSRecord objects to be harvested.
    final_record_list = APSRecordList()

    task_update_progress("Parsing input parameters")

    ## Figure out which mode we are doing
    if mode not in ("append", "a", "correct", "c", "replace", "r"):
        write_message("Warning: given mode is not valid. Using append.")
        mode = "append"

    if len(mode) == 1:
        mode = "-" + mode
    else:
        mode = "--" + mode

    # Gather IDs (if any)
    if len(dois) > 0:
        write_message("Parsing DOIs")

        # We are doing DOIs, we need to get record ids
        for doi in dois.split(','):
            doi = doi.strip()
            try:
                recid = get_record_from_doi(doi)
            except APSHarvesterSearchError, e:
                write_message("Error while getting recid from %s: %s" % \
                              (doi, str(e)))
                continue
            if not recid:
                write_message("Error while getting recid from %s: No recid found" % \
                              (doi,))
                continue
            final_record_list.append(APSRecord(recid, [doi]))

    if len(recids) > 0:
        write_message("Parsing record IDs")

        # We are doing rec ids
        recids = split_cli_ids_arg(recids)
        for recid in recids:
            final_record_list.append(APSRecord(recid))

    if query:
        write_message("Performing a search query")

        # We are doing a search query, rg=0 allows the return of all results.
        result = perform_request_search(p=query, \
                                        cc=CFG_APSHARVEST_SEARCH_COLLECTION, \
                                        of='id', \
                                        rg=0, \
                                        wl=0)
        for recid in result:
            final_record_list.append(APSRecord(recid))

    if records in ("new", "modified", "both"):
        write_message("Fetching records to update")

        # We fetch records from the database
        last_id, last_date = fetch_last_updated(name="apsharvest")
        records_found = []
        if records == "new":
            records_found = get_all_new_records(since=last_date, last_id=last_id)
        elif records == "modified":
            records_found = get_all_modified_records(since=last_date, last_id=last_id)
        elif records == "both":
            records_found.extend(get_all_new_records(since=last_date, last_id=last_id))
            records_found.extend(get_all_modified_records(since=last_date, last_id=last_id))

        for recid, date in records_found:
            final_record_list.append(APSRecord(recid, date=date))

    write_message("Found %d record(s) to download fulltext for." % (len(final_record_list),))

    if not final_record_list:
        # No records to harvest, quit.
        write_message("Nothing to harvest.")
        return

    #2: Fetch fulltext
    count = 0
    task_update_progress("Fetching fulltext-records")
    for recid, fft_record in perform_fulltext_harvest(final_record_list):
        generated_fft_xml = ffts_to_xml({recid: [fft_record]})
        new_filename = get_temporary_file(prefix="apsharvest_result_", \
                                          suffix=".xml", \
                                          dir=CFG_TMPDIR)
        try:
            fd = open(new_filename, 'w')
            fd.write(generated_fft_xml)
            fd.close()
        except IOError, e:
            write_message("\nException caught: %s" % e, sys.stderr)
            write_message(traceback.format_exc()[:-1])
            task_update_status("CERROR")
            return

        # Submit a BibUpload task
        # NB: we do not change the modified date of the record as we otherwise would be caught by ourselves again.
        # We rather run the bibindex of the fulltext afterwards as post-process.
        task_arguments = ["--notimechange", \
                          '--post-process', 'bst_run_bibtask[taskname="bibindex", user="apsharvest", w="fulltext", i="%s"]' % (recid,), \
                          mode, \
                          new_filename]
        taskid = task_low_level_submission("bibupload", "apsharvest", *tuple(task_arguments))
        write_message("Submitted BibUpload task #%s with mode %s (%s)" % (str(taskid), mode, new_filename))
        count += 1
    # We are done
    write_message("Uploaded %d fulltext documents." % (count,))


def perform_fulltext_harvest(record_list):
    """
    For every record in given list (record ID, DOI(s), date last updated), yield a FFT
    dictionary (recid, fft dict) containing URL to fulltext downloaded locally.
    """
    count = 0
    for record in record_list:
        recid, dois, date = record.get_data()

        if count != 0:
            time.sleep(CFG_APSHARVEST_REQUEST_TIMEOUT)
        count += 1
        task_update_progress("Harvesting fulltext (%d/%d)" % (count, \
                                                              len(record_list)))

        if date:
            store_last_updated(recid, date, name="apsharvest")

        if not dois:
            write_message("No DOI found for record %d" % (recid,))
            continue

        for doi in dois:
            url = CFG_APSHARVEST_FULLTEXT_URL % {'doi': doi}
            try:
                result_file = download_url(url, format="zip")
            except StandardError, e:
                if 'urlopen' in str(e) or 'URL could not be opened' in str(e):
                    write_message("ERROR: Fulltext XML not found for %s: %s" % (doi, url))
                    continue
                raise
            # This means we found something, we're done.
            write_message("Downloaded fulltext for %d (%s)" % (recid, result_file))
            break
        else:
            # No valid DOI->fulltext found.
            write_message("No fulltext found for %d" % (recid,))
            continue

        # Unzip the compressed file
        unzipped_folder = unzip(result_file)

        # Validate the checksum of the compressed fulltext file.
        try:
            checksum_validated_files = find_and_validate_md5_checksums(in_folder=unzipped_folder, \
                                                                       md5key_filename=CFG_APSHARVEST_MD5_FILE)
        except InvenioFileChecksumError, e:
            write_message("Error while validating checksum: %s" % (str(e),))
            write_message("Skipping record %d in %s" % (recid, unzipped_folder))
            continue
        if not checksum_validated_files:
            write_message("Warning: No files found to perform checksum"
                          " validation on inside %s" % (unzipped_folder,))
        elif len(checksum_validated_files) != 1 or not 'fulltext.xml' in checksum_validated_files[0]:
            write_message("Warning: No fulltext file found inside %s for %s" % (unzipped_folder, recid))
            continue

        # We have the fulltext file as fulltext.xml as expected.
        fulltext_file = checksum_validated_files[0]

        # Generate FFT and yield it
        fft = {}
        fft['url'] = fulltext_file
        fft['doctype'] = CFG_APSHARVEST_FFT_DOCTYPE
        fft['options'] = ["HIDDEN"]
        yield recid, fft




def get_doi_from_record(recid):
    """
    Given a record ID we fetch it from the DB and return
    a list of all found DOIs as specified by the config variable
    CFG_APSHARVEST_RECORD_DOI_TAG.

    @param recid:  record id record containing a DOI
    @type recid: string/int

    @return: list of DOIs found in record
    @rtype: list
    """
    doi_list = []
    record = BibFormatObject(int(recid))
    possible_dois = record.fields(CFG_APSHARVEST_RECORD_DOI_TAG[:-1])
    for doi in possible_dois:
        if '2' in doi and doi.get('2', "") == "DOI":
            # Valid DOI present, add it
            try:
                doi_list.append(doi['a'])
            except KeyError, e:
                write_message("Error occured while getting DOI from %s: %s" % \
                              (recid, str(e)))
                continue
    return doi_list


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
        raise APSHarvesterSearchError("DOI mismatch: %s did not find only 1 record: %s" % \
                                       ",".join(recids))
    return int(recids[0])
