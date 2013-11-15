# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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
"""
Synchronize record IDs between the CERN Document Server (CDS) and Inspire.

This BibTasklet is intended to be a general purpose replacement for
'bst_inspire_cds_synchro' and 'bst_update_cds_inspire_id', it should be
executable on both CDS and Inspire.

Methodology:
 1. Get IDs from the remote instance (ie CDS) that map to records in Inspire
 2. Search those IDs locally (ie "035:<ID>")
 3a. If the local record exists, check that it's 035 field matches remote IDs
     -> Update or append locally as needed to correct the record.
 3b. If not, get the remote record and extract other identifiers. Do local
     searches by eprint, doi.
     -> If they can be found, append the remote ID to local record.
"""

import os
import time

from cStringIO import StringIO
from urllib2 import HTTPError

from invenio.config import (CFG_TMPSHAREDDIR,
                            CFG_CERN_SITE, CFG_INSPIRE_SITE)
from invenio.search_engine import perform_request_search
from invenio.bibtask import (write_message,
                             task_update_progress)
from invenio.bibrecord import (record_add_field, record_add_subfield_into,
                               record_xml_output, create_record,
                               record_get_field_values)
from invenio.invenio_connector import InvenioConnector
from invenio.filedownloadutils import download_url, InvenioFileDownloadError
from invenio.bibtaskutils import ChunkedBibUpload

# LOOK AT ALL THE LOVELY VARIABLES!
SCRIPT_NAME = "bst_sync_cds_inspire_recids"
NOW = time.strftime('%Y-%m-%d_%Hh%Mm%Ss')
LOG_DIR = CFG_TMPSHAREDDIR
LOG_FILE = "%s_%s.log" % (SCRIPT_NAME, NOW)
BATCH_SIZE = 200

if CFG_INSPIRE_SITE:
    LOCAL_INSTANCE = "Inspire"
    REMOTE_INSTANCE = "CDS"
    REMOTE_URL = "http://cds.cern.ch"
    REMOTE_URL_TEST = "http://cdstest.cern.ch"
    SEARCH_TERMS = "035:inspire"
    COLLECTION = ""
    FILTER_VALUE = "^(CDS|cds)$"
elif CFG_CERN_SITE:
    LOCAL_INSTANCE = "CDS"
    REMOTE_INSTANCE = "Inspire"
    REMOTE_URL = "http://www.inspire.net"
    REMOTE_URL_TEST = "http://inspireheptest.cern.ch"
    SEARCH_TERMS = "035:cds"
    COLLECTION = ""
    FILTER_VALUE = "^(Inspire|INSPIRE|inspire)$"


# Begin!
def bst_sync_cds_inspire_recids(search_terms=SEARCH_TERMS, log_dir=None,
                                collection=COLLECTION, batch_size=BATCH_SIZE,
                                debug=False):
    """Synchronize record IDs between the CERN Document Server (CDS) and Inspire.

This BibTasklet is intended to be a general purpose replacement for
'bst_inspire_cds_synchro' and 'bst_update_cds_inspire_id', it should
be executable on both CDS and Inspire.

Generally there should be no need to modify these parameters, the
script uses CFG_INSPIRE_SITE and CFG_CERN_SITE from invenio.conf
to determine what type of Invenio instance we're running on. These
parameters will be set by default to the correct values to
synchronise all IDs, though you may want to limit records manually.

Parameters:
 search_terms - The term to use to get record IDs
                (Default "035:<LOCAL>)
 log_dir - The directory to store the log file in
           (Defaults to CFG_TMPSHAREDDIR)
 collection - What collection to take from
              (Default is no collection)
 batch_size - How many records to try and ammend at once
              (Default 200)
 debug - If True, this script will run against the TEST instances
         (Default false)
    """
    configure_globals(search_terms, log_dir, debug)
    _print("All messages will be logged to %s/%s" % (LOG_DIR, LOG_FILE))

    task_update_progress("Finding remote records on %s with %s IDs"
                         % (REMOTE_INSTANCE, LOCAL_INSTANCE))
    remote_ids = get_remote_ids(search_terms, collection)

    task_update_progress("Matching remote IDs to local records")
    missing_ids = match_remote_ids(remote_ids)

    count_appends, count_problems = match_missing_ids(missing_ids, batch_size)

    _print("======================== FINAL SCORE ========================", 1)
    _print(" Records matched: %d" % (len(remote_ids)-len(missing_ids)), 1)
    _print(" Records appended: %d" % count_appends, 1)
    _print(" IDs not matched: %d" % count_problems, 1)
    _print("=============================================================", 1)

    _print("Finishing, messages logged to: %s/%s" % (LOG_DIR, LOG_FILE))

    return True


# =========================| Helper Functions |=========================

def _print(message, verbose=3):
    """ Register program output """
    msg = "%s: %s" % (SCRIPT_NAME, message)
    write_message(msg, verbose=verbose)
    # Indent messages to the log file for ease of reading
    log_msg = message.rjust(len(message) + (verbose-3)) + "\n"
    with open("%s/%s" % (LOG_DIR, LOG_FILE), 'a') as log:
        log.write(log_msg)


def write_to_file(filename, data, output_dir=LOG_DIR, message=None,
                  append=False):
    """ Writes output to a file, can accept a string as input or a list of
    strings.
    Example file path:
     /tmp/dir/bst_sync_cds_inspire_recids_2013-10-31_15h25m09s_errors.log
    Parameters:
     (string) output_dir: Directory to write the file to.
     (string) filename: Name of the file, including extension.
     (string -or- list) data: the data to be written to the file.
    """
    if data:
        if type(data) is list:
            buf = StringIO()
            for line in data:
                buf.write("%s\n" % line)
            data_string = buf.getvalue()
        elif type(data) is str:
            data_string = data
        else:
            raise TypeError("%s is not a valid data type for" % type(data)
                            + " function write_to_file()")
        path = "%s/%s_%s_%s" % (output_dir, SCRIPT_NAME, NOW, filename)
        if append:
            mode = 'a'
        else:
            mode = 'w'
        try:
            with open(path, mode) as handle:
                if message:
                    _print(message)
                    handle.write("# %s\n" % message)
                handle.write(data_string)
            _print("Wrote %d lines to file %s" % (data_string.count('\n'),
                                                  qpath))
        except IOError:
            _print("ERROR: Could not write output to %s" % path, 1)
    else:
        _print("Nothing to write to file %s" % filename)


def configure_globals(search_terms, log_dir, debug):
    """ Sets global config variables used by this script """
    try:
        if LOCAL_INSTANCE:
            pass
    except NameError:
        raise StandardError("""Could not determine local Invenio instance.
This means neither CFG_INSPIRE_SITE or CFG_CERN_SITE are set in the Invenio
config, or the config hasn't been updated with $ inveniocfg --update-all""")

    if not search_terms:
        raise ValueError("No search terms defined")

    global LOG_DIR
    if log_dir:
        if os.path.isdir(log_dir):
            LOG_DIR = log_dir
        else:
            LOG_DIR = CFG_TMPSHAREDDIR
            _print("Error: Could not set log dir to: '%s', defaulting to: '%s'"
                   % (log_dir, LOG_DIR), 1)

    if debug:
        global REMOTE_URL
        REMOTE_URL = REMOTE_URL_TEST


def generate_marc_to_append(local, remote):
    """ Generates MarcXML to append an 035 remote ID to a record """
    newrec = {}
    record_add_field(newrec, '001', controlfield_value=str(local))
    field_pos = record_add_field(newrec, '035')
    record_add_subfield_into(newrec, '035', '9', REMOTE_INSTANCE,
                             field_position_global=field_pos)
    record_add_subfield_into(newrec, '035', 'a', str(remote),
                             field_position_global=field_pos)
    return record_xml_output(newrec)


# =========================| Minor Functions |=========================

def get_remote_record(recid):
    """ For a given remote record ID, we download the record XML and return
    the record in a BibRecord structure
    Parameter:
    (int) recid - record ID for remote record
    Returns: BibRecord
    """
    url = "%s/record/%d/export/xm?ot=001,035" % (REMOTE_URL, recid)
    tmp_file = ''
    try:
        bibrec = None
        tmp_file = download_url(url, retry_count=10, timeout=61.0)
        with open(tmp_file, 'r') as temp:
            bibrec, code, errors = create_record(temp.read())
            if code != 1 or errors:
                _print("Warning: There were errors creating BibRec structure " +
                       "from remote record #%d" % recid, 4)
        os.remove(tmp_file)
        return bibrec
    except (StandardError, InvenioFileDownloadError, HTTPError) as err:
        _print("Error: Could not download remote record #%d" % recid, 4)
        _print(err.message, 5)


def extract_035_id(record):
    """ Gets the value of the 035__a field
    Parameters:
     (BibRecord) record - the record to look at
    Return: the ID's remote mapping"""
    try:
        field_vals = record_get_field_values(record, "035", code="a",
                                             filter_subfield_code="9",
                                             filter_subfield_value=FILTER_VALUE,
                                             filter_subfield_mode="r")
        field_vals = set(field_vals)
        if not field_vals:
            return None
        if len(field_vals) == 1 and field_vals[0].isdigit():
            return field_vals[0].isdigit()
        elif len(field_vals) > 1:
            _print("Warning: Multiple recids found in 035 for record", 6)
            for val in field_vals:
                if val.isdigit():
                    _print("Assuming local recid is %s" % val, 6)
                    return val
    except (KeyError, ValueError, IndexError) as exc:
        _print(exc.message, 5)


def local_record_exists(recid):
    """ Checks if the given record exists locally """
    if perform_request_search(p="001:%s" % recid, of='id'):
        return True
    else:
        return False


# =========================| Major Functions |=========================

def get_remote_ids(search_terms, collection=''):
    """ Retreives IDs from the remote instance of records which have a
    corresponding ID in the 035 field to the local instance.

    Parameters:
     (string) search_terms - what to search for remotely
    Returns:
     A list of RecIDs
    """
    remote_connector = InvenioConnector(REMOTE_URL)
    _print("Getting records from: %s" % REMOTE_URL)
    recids = remote_connector.search(p=search_terms, cc=collection, of='id')
    _print("Found %d records on %s for search terms '%s' in collection '%s'"
           % (len(recids), REMOTE_INSTANCE, search_terms, collection))
    return recids


def match_remote_ids(remote_ids):
    """ Matches remote IDs to local records, IDs that cannot be matched
    are returned as a list."""
    per_last = -1

    def percent_update(index, percent_last):
        """ Calculates completion percentage, updates task progress """
        per = 100 * float(index)/float(len(remote_ids))
        if per > (percent_last + 0.5):
            percent_last = per
            task_update_progress("Local matching %.1f%% (%d/%d)"
                                 % (per, index, len(remote_ids)))
        return percent_last

    missing = []
    for i, recid in enumerate(remote_ids):
        per_last = percent_update(i, per_last)
        term = "035__9:%s and 035__a:%d" % (REMOTE_INSTANCE, recid)
        result = perform_request_search(p=term)
        if not result:
            missing.append(recid)
    _print("Of %d record IDs, %d were matched, %d are missing"
           % (len(remote_ids), (len(remote_ids) - len(missing)), len(missing)))
    return missing


def match_missing_ids(remote_ids, batch_size):
    """ For ID pairings that are missing, this function splits the missing
    IDs into batches. The records are pulled from remote, the 035 field read
    and then the remote ID appended to the local record.

    Parameters:
     remote_ids - a list of missing remote rec-ids
     batch_size - How many records to match at a time
    Returns:
     count_appends - number of records being appended
     count_problems - number of records which could not be matched at all
    """
    count_appends = 0
    count_problems = 0

    batches = [remote_ids[x:x+batch_size] for x in
               xrange(0, len(remote_ids), batch_size)]
    _print("Identified %d records which their remote IDs updating."
           % len(remote_ids))
    _print("Processing %d batches of size %d" % (len(batches), batch_size))
    for i, batch in enumerate(batches, 1):
        task_update_progress("Batch %d of %d" % (i, len(batches)))
        _print("Batch %d of %d" % (i, len(batches)))
        try:
            appends, problems = process_record_batch(batch)
            count_appends += len(appends)
            count_problems += len(problems)
            write_to_file('missing_ids.txt', problems, append=True)
            _print("Submitting batch #%d to BibUpload for appending..." % i, 4)
            start_bibupload_job(appends)
        except StandardError:
            _print("Error occured during match of batch %d" % i, 2)
    return count_appends, count_problems


def process_record_batch(batch):
    """ Splitting the matching remotely job into parts, function does the
    matching of remote records to local IDs """
    _print("Processing batch, recid #%d to #%d" % (batch[0], batch[-1]), 4)
    # Local ID: Remote ID
    appends = {}
    problems = []
    for recid in batch:
        _print("Processing recid %d" % recid, 5)
        record = get_remote_record(recid)
        if record is None:
            problems.append(recid)
            continue
        else:
            local_id = extract_035_id(record)
            if not local_record_exists(local_id):
                problems.append(recid)
                continue
            else:
                _print("Matching remote id %d to local record %s"
                       % (recid, local_id))
                appends[local_id] = recid
    _print("Batch matching done: %d IDs matched, %d IDs not matched"
           % (len(appends), len(problems)), 4)
    return appends, problems


def start_bibupload_job(id_pairs):
    """ Submits the append job to bibupload
    id_pairs - {local_recid: remote_recid} """
    bibupload = ChunkedBibUpload(mode='a', user=SCRIPT_NAME, notimechange=True)
    for local, remote in id_pairs.iteritems():
        bibupload.add(generate_marc_to_append(local, remote))
    bibupload.cleanup()  # This initiates the job
