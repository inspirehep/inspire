# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2013, 2014, 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Synchronize record IDs between the CERN Document Server (CDS) and Inspire."""

import sys
import os
import shutil

from tempfile import mkstemp

from invenio.intbitset import intbitset
from invenio.config import CFG_CERN_SITE, CFG_INSPIRE_SITE, CFG_SITE_NAME, CFG_TMPSHAREDDIR
from invenio.search_engine import get_collection_reclist, search_pattern
from invenio.search_engine import get_record
from invenio.bibrecord import record_get_field_instances, record_get_field_values, field_get_subfield_instances, record_add_field, record_xml_output
from invenio.bibtask import write_message, task_update_progress, task_low_level_submission, task_sleep_now_if_required


if CFG_INSPIRE_SITE:
    CFG_THIS_SITE = "Inspire"
    CFG_OTHER_SITE = "CDS"
    CFG_THIS_URL = "https://inspirehep.net/record"
    CFG_OTHER_URL = "https://cds.cern.ch/record"
    CERN_RELEVANT_PAPER = get_collection_reclist("CERN")
elif CFG_CERN_SITE:
    CFG_THIS_SITE = "CDS"
    CFG_OTHER_SITE = "Inspire"
    CFG_THIS_URL = "https://cds.cern.ch/record"
    CFG_OTHER_URL = "https://inspirehep.net/record"

CFG_SHARED_PATH = '/afs/cern.ch/project/inspire/cds-synchro'
CFG_EXPORT_FILE = os.path.join(CFG_SHARED_PATH, '%s2%s.ids' % (CFG_THIS_SITE, CFG_OTHER_SITE))
CFG_IMPORT_FILE = os.path.join(CFG_SHARED_PATH, '%s2%s.ids' % (CFG_OTHER_SITE, CFG_THIS_SITE))


def get_temporary_file(prefix="cds_inspire_synchro_",
                       suffix=".xml",
                       directory=CFG_TMPSHAREDDIR):
    """Generate a safe and closed filepath."""
    try:
        file_fd, filepath = mkstemp(prefix=prefix,
                                    suffix=suffix,
                                    dir=directory)
        os.close(file_fd)
    except IOError, e:
        try:
            os.remove(filepath)
        except Exception:
            pass
        raise e
    return filepath


def get_all_recids():
    """Return all relevant record IDs."""
    if CFG_INSPIRE_SITE:
        all_recids = get_collection_reclist(CFG_SITE_NAME) | get_collection_reclist("Conferences")
    elif CFG_CERN_SITE:
        all_recids = get_collection_reclist(CFG_SITE_NAME) | get_collection_reclist("CERN Articles & Preprints") | get_collection_reclist("CERN Series") | get_collection_reclist("CERN Departments") | get_collection_reclist("CERN Experiments") | get_collection_reclist("CERN R&D Projects")
        # We exclude all records that is not relevant for CERN/CDS
        # all_recids = all_recids & search_pattern(p='690c:CERN or 595:cds')
        # We exclude all records with an existing INSPIRE ID.
        # all_recids = all_recids - search_pattern(p='035:INSPIRE')
    else:
        all_recids = intbitset()
    return all_recids


def get_record_ids_to_export(unmatched_only=False):
    """Return all records with identifiers to sync."""
    all_recids = get_all_recids()
    recids_with_other_id = search_pattern(p='035__9:%s' % CFG_OTHER_SITE)
    recids_with_a_doi = search_pattern(p='doi:"**"')
    recids_with_an_arxiv_id = search_pattern(p='035__9:"arXiv"')
    if unmatched_only:
        all_recids = all_recids - recids_with_other_id
        return (recids_with_a_doi | recids_with_an_arxiv_id) & all_recids
    else:
        return (recids_with_a_doi | recids_with_an_arxiv_id | recids_with_other_id) & all_recids


def get_ids_from_recid(recid):
    """Get all relevant identifiers from metadata of local record."""
    record = get_record(recid)

    # Retrieving DOI
    doi = ""
    dois = record_get_field_values(record, '024', '7', code='a')
    dois = [doi for doi in dois if doi.startswith('10.')]
    if len(dois) > 1:
        print >> sys.stderr, "WARNING: record %s have more than one DOI: %s" % (recid, dois)
        doi = dois[0]
    elif len(dois) == 1:
        doi = dois[0]

    # Retrieving arXiv eprint
    eprint = ""
    eprints = record_get_field_values(record, '035', code='a')
    eprints = [an_eprint[len('oai:arXiv.org:'):] for an_eprint in eprints if an_eprint.lower().startswith('oai:arxiv.org:')]
    if len(eprints) > 1:
        print >> sys.stderr, "WARNING: record %s have more than one arXiv eprint: %s" % (recid, eprints)
        eprint = eprints[0]
    elif len(eprints) == 1:
        eprint = eprints[0]

    # Retrieving Other service ID
    other_id = ''
    for field in record_get_field_instances(record, '035'):
        subfields = dict(field_get_subfield_instances(field))
        if subfields.get('9', '').upper() == CFG_OTHER_SITE.upper() and subfields.get('a'):
            other_id = subfields['a']
    if CFG_INSPIRE_SITE and not other_id:
        for field in record_get_field_instances(record, '595'):
            subfields = dict(field_get_subfield_instances(field))
            if "CDS" in subfields.get('a', '').upper():
                other_id = subfields.get('a', 0).split("-")[-1]
                try:
                    int(other_id)
                except ValueError:
                    # Not an integer, we move on
                    other_id = ''
    reportnumbers = record_get_field_values(record, '037', code='a')

    system_number = ""
    if CFG_INSPIRE_SITE:
        for value in record_get_field_values(record, '970',
                                             filter_subfield_code="a",
                                             filter_subfield_value="SPIRES",
                                             filter_subfield_mode="s"):
            system_number = value.split("-")[-1]
            break  # There is typically only one

    out = [str(recid), doi, eprint, other_id, system_number] + reportnumbers
    return [val.replace('\n', ' ').replace('\r', '') for val in out]


def iter_export_rows(recids=None):
    """Yield IDs to file."""
    if recids is None:
        recids = get_record_ids_to_export()
    for recid in recids:
        ids = get_ids_from_recid(recid)
        yield '|'.join(ids)


def add_other_id(other_id=None, doi="", eprint="",
                 recid=None, system_number=None,
                 reportnumbers=None, all_recids=None):
    """Search and match using given identifiers."""
    query = ""
    if all_recids is None:
        all_recids = get_all_recids()
    if reportnumbers is None:
        reportnumbers = []
    if recid is not None:
        query = "existing recid"
        try:
            recid = int(recid)
        except ValueError:
            recid = None
        if recid and recid not in all_recids:
            write_message("WARNING: %s thought that their record %s had recid %s in %s but this seems wrong" %
                          (CFG_OTHER_SITE, other_id, recid, CFG_THIS_SITE),
                          stream=sys.stderr)
            recid = None
    if recid is None and eprint:
        query = 'oai:arXiv.org:%s' % (eprint,)
        arxiv_ids = search_pattern(p=query, f='035__a', m='e') & all_recids
        if len(arxiv_ids) > 1:
            write_message("ERROR: %s record %s matches more than one record in %s via %s: %s" %
                          (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, query, arxiv_ids),
                          stream=sys.stderr)
            return [other_id] + list(arxiv_ids)
        elif len(arxiv_ids) == 1:
            recid = arxiv_ids[0]
    if recid is None and doi:
        query = 'doi:"%s"' % doi
        doi_ids = search_pattern(p=query) & all_recids
        if len(doi_ids) > 1:
            write_message("ERROR: %s record %s matches more than one record in %s via %s: %s" %
                          (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, query, doi_ids),
                          stream=sys.stderr)
            return [other_id] + list(doi_ids)
        elif len(doi_ids) == 1:
            recid = doi_ids[0]
    if recid is None and reportnumbers:
        query = "037__a:" + " OR 037__a:".join(reportnumbers)
        reportnumbers_ids = intbitset()
        for rn in reportnumbers:
            reportnumbers_ids |= search_pattern(p=rn, f='037__a', m='e')
        reportnumbers_ids &= all_recids
        if len(reportnumbers_ids) > 1:
            write_message("ERROR: %s record %s matches more than one record in %s via %s: %s" %
                          (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, query, reportnumbers_ids),
                          stream=sys.stderr)
            return [other_id] + list(reportnumbers_ids)
        elif len(reportnumbers_ids) == 1:
            recid = reportnumbers_ids[0]
    if recid is None and system_number and CFG_CERN_SITE:
        query = "035:%s 035:SPIRES" % (system_number,)
        system_number_ids = search_pattern(p=query)
        system_number_ids &= all_recids
        if len(system_number_ids) > 1:
            write_message("ERROR: %s record %s matches more than one record in %s via %s: %s" %
                          (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, query, system_number_ids),
                          stream=sys.stderr)
            return [other_id] + list(system_number_ids)
        elif len(system_number_ids) == 1:
            recid = system_number_ids[0]
    if recid:
        recid = int(recid)
        record = get_record(recid)
        fields = record_get_field_instances(record, '035')
        for field in fields:
            subfields = dict(field_get_subfield_instances(field))
            if CFG_OTHER_SITE.upper() == subfields.get('9', '').upper():
                stored_recid = subfields.get('a', 0)
                try:
                    stored_recid = int(stored_recid)
                except ValueError:
                    # Not an integer, we move on and add the new ID.
                    continue
                if stored_recid and int(stored_recid) != int(other_id):
                    write_message("ERROR: %s record %s matches %s record %s which already points back to a different record %s in %s" % (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, recid, stored_recid, CFG_OTHER_SITE), stream=sys.stderr)
                return

        if CFG_INSPIRE_SITE:
            fields = record_get_field_instances(record, '595')
            for field in fields:
                subfields = dict(field_get_subfield_instances(field))
                if "CDS" in subfields.get('a', '').upper():
                    stored_recid = subfields.get('a', 0).split("-")[-1]
                    try:
                        stored_recid = int(stored_recid)
                    except ValueError:
                        # Not an integer, we move on and add the new ID.
                        continue
                    if stored_recid and int(stored_recid) != int(other_id):
                        write_message("ERROR: %s record %s matches %s record %s which already points back to a different record %s in %s" % (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, recid, stored_recid, CFG_OTHER_SITE), stream=sys.stderr)
                    return

        write_message("Matched {1}/{0} to {3}/{2} with {4}".format(
            other_id,
            CFG_OTHER_URL,
            recid,
            CFG_THIS_URL,
            query
        ))
        rec = {}
        record_add_field(rec, '001', controlfield_value='%s' % recid)
        if CFG_INSPIRE_SITE:
            if recid in CERN_RELEVANT_PAPER:
                write_message("CERN relevant paper: adding 035")
                record_add_field(rec, '035', ind1=' ', ind2=' ', subfields=(('9', CFG_OTHER_SITE), ('a', other_id)))
            else:
                write_message("Non-CERN relevant paper: adding 595")
                record_add_field(rec, '595', ind1=' ', ind2=' ', subfields=(('9', "CERN"), ('a', "CDS-{0}".format(other_id))))
        else:
            record_add_field(rec, '035', ind1=' ', ind2=' ', subfields=(('9', CFG_OTHER_SITE), ('a', other_id)))
        return record_xml_output(rec)


def write_results(current_batch):
    """Write the current batch to some temporary file."""
    output_file = get_temporary_file()
    write_message("Writing next batch to {0}".format(output_file))
    with open(output_file, "w") as fd:
        fd.write("<collection xmlns=\"http://www.loc.gov/MARC21/slim\">\n")
        fd.write("\n".join(current_batch))
        fd.write("</collection>\n")
    return output_file


def import_recid_list(input_stream=sys.stdin, batch_limit=500, automatic_upload=False):
    """Import identifiers from file, match and generate output files."""
    all_recids = get_all_recids()
    output_files = []
    current_batch = []
    current_dupes = []
    i = 0
    for row in input_stream:
        if row.endswith('\n'):
            row = row[:-1]
        row = row.split('|')
        if row:
            try:
                other_id, doi, eprint, recid, system_number = row[0], row[1], row[2], row[3], row[4]
            except IndexError:
                # Something is up
                write_message("WARNING: {0} is invalid".format(row), stream=sys.stderr)
                continue
            if len(row) > 5:
                reportnumbers = row[5:]
            else:
                reportnumbers = None
            if not other_id:
                other_id = None
            if not recid:
                recid = None
            result = add_other_id(other_id, doi, eprint,
                                  recid, system_number,
                                  reportnumbers, all_recids)
            if result:
                if isinstance(result, list):
                    # Duplications found
                    current_dupes.append(result)
                    continue
                current_batch.append(result)
                i += 1
                if i % batch_limit == 0:
                    output_file = write_results(current_batch)
                    output_files.append(output_file)
                    if automatic_upload:
                        task_low_level_submission(
                            'bibupload',
                            'bst_inspire_cds_synchro',
                            '-a', output_file, '-n')
                        write_message("Scheduled bibupload --append %s" % output_file)
                    task_sleep_now_if_required()
                    current_batch = []
    if len(current_batch) > 0:
        output_file = write_results(current_batch)
        output_files.append(output_file)
        if automatic_upload:
            task_low_level_submission('bibupload', 'bst_inspire_cds_synchro', '-a', output_file, '-n')
            write_message("Scheduled bibupload --append %s" % output_file)
    write_message("Matched in total {0} records.".format(i))

    if len(current_dupes) > 0:
        # We have duplications
        dupes_output_file = get_temporary_file("cds_duplicates_",
                                               ".txt")
        with open(dupes_output_file, "w") as fd:
            fd.write(
                "\n".join(["{0}: {1}".format(dupe[0], dupe[1:])
                           for dupe in current_dupes])
            )
        write_message("Found {0} possible duplicates which are available here: {1}".format(
            len(current_dupes),
            dupes_output_file
        ))
    return output_files


def bst_inspire_cds_synchro(unmatched_only=True,
                            skip_extraction=False,
                            batch_limit=500,
                            automatic_upload=False):
    """Synchronize recids between CDS and INSPIRE.

    1. Run this script to create an export of all records relevant for synchronization
       in a common place (e.g. AFS).

    2. Check for export file then match and import relevant IDs to the correct records.
    """
    if not skip_extraction:
        task_update_progress("Phase 1: extracting IDs for %s" % CFG_OTHER_SITE)
        if unmatched_only:
            # We expose only those that are unmatched
            recids = get_record_ids_to_export(unmatched_only=True)
        else:
            recids = get_record_ids_to_export()
        write_message("Going to export {0} records.".format(len(recids)))
        export_file = open(CFG_EXPORT_FILE + '.part', "w")
        for i, row in enumerate(iter_export_rows(recids)):
            print >> export_file, row
            if i % 100 == 0:
                task_sleep_now_if_required(can_stop_too=True)
        export_file.close()
        shutil.move(CFG_EXPORT_FILE + '.part', CFG_EXPORT_FILE)
        task_sleep_now_if_required(can_stop_too=True)
    else:
        write_message("Skipping extraction.")
    if os.path.isfile(CFG_IMPORT_FILE):
        task_update_progress("Phase 2: importing IDs from %s" % CFG_OTHER_SITE)
        output_files = import_recid_list(open(CFG_IMPORT_FILE),
                                         batch_limit=batch_limit,
                                         automatic_upload=automatic_upload)
        write_message("Generated upload files:\n {0}".format("\n".join(output_files)))
    else:
        write_message("WARNING: Cannot find {0}.".format(CFG_IMPORT_FILE),
                      stream=sys.stderr)
