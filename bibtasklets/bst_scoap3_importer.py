# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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

"""SCOAP3 importer."""

import sys
import requests

from os import fdopen, remove
from tempfile import mkstemp
from requests.exceptions import HTTPError, ConnectionError, Timeout

from invenio.errorlib import register_exception
from invenio.search_engine import perform_request_search
from invenio.bibdocfile import BibRecDocs
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibtask import task_low_level_submission, write_message, task_sleep_now_if_required


def bst_scoap3_importer():
    """Import from SCOAP3."""
    try:
        request = requests.get('http://repo.scoap3.org/ffts_for_inspire.py/csv')
    except (HTTPError, ConnectionError, Timeout):
        register_exception()
        return
    task_sleep_now_if_required(can_stop_too=True)

    fd_update, name_update = mkstemp(
        suffix='.xml',
        prefix='bibupload_scoap3_',
        dir=CFG_TMPSHAREDDIR
    )

    out_update = fdopen(fd_update, 'w')
    fd_new, name_new = mkstemp(
        suffix='.xml',
        prefix='bibupload_scoap3_',
        dir=CFG_TMPSHAREDDIR
    )
    out_new = fdopen(fd_new, 'w')

    print >> out_update, "<collection>"
    print >> out_new, "<collection>"

    line_count_new = 0  # to avoid empty bibupload
    line_count_update = 0  # to avoid empty bibupload

    # We strip the first line.
    for line in request.text.split("\n")[1:]:
        task_sleep_now_if_required(can_stop_too=True)
        recid, arxiv_id, cr_date, checksum, link, type, doi = [x.strip() for x in line.split(',')]
        write_message(line.strip())
        if checksum == "None":
            write_message("... no PDF. Skipping")
            continue
        if arxiv_id == "None":
            inspire_record = perform_request_search(p="doi:%s" % (doi, ), cc="HEP")
        else:
            inspire_record = perform_request_search(p="037:%s or doi:%s" % (arxiv_id, doi), cc="HEP")
        if len(inspire_record) > 1:
            write_message("ERROR: more than one INSPIRE record matched %s and %s for SCOAP3 record %s: %s" % (arxiv_id, doi, recid, list(inspire_record)), stream=sys.stderr)
            continue
        elif not inspire_record:
            write_message("WARNING: no INSPIRE record matched %s or %s for SCOAP3 record %s" % (arxiv_id, doi, recid), stream=sys.stderr)
            continue
        action = None  # do nothing
        rec = {}
        inspire_record = inspire_record[0]
        record = BibRecDocs(inspire_record)
        for doc in record.list_latest_files():
            if doc.format in ('.pdf', '.pdf;pdfa'):
                if doc.bibdoc.doctype == 'SCOAP3':
                    if doc.checksum == checksum:
                        write_message("... OK: file alredy attached to INSPIRE record %s (doc.checksum=%s, checksum=%s)" % (inspire_record, doc.checksum, checksum))
                    else:
                        write_message("... OK: new revision available for INSPIRE record %s (doc.checksum=%s, checksum=%s)" % (inspire_record, doc.checksum, checksum))
                        action = "UPDATE"
                    break
        else:
            write_message("... OK: need to add new file to INSPIRE record %s" % inspire_record)
            action = "APPEND"
        if action:
            if type == '.pdf;pdfa':
                record_add_field(rec, 'FFT', subfields=[('a', link), ('n', 'scoap3-fulltext'), ('f', '.pdf;pdfa'), ('t', 'SCOAP3'), ('d', 'Article from SCOAP3')])
            else:
                record_add_field(rec, 'FFT', subfields=[('a', link), ('n', 'scoap3-fulltext'), ('t', 'SCOAP3'), ('d', 'Article from SCOAP3')])

            record_add_field(rec, '001', controlfield_value=str(inspire_record))
        if action == "UPDATE":
            line_count_update += 1
            print >> out_update, record_xml_output(rec)
        elif action == "APPEND":
            line_count_new += 1
            print >> out_new, record_xml_output(rec)
    print >> out_update, "</collection>"
    print >> out_new, "</collection>"
    out_new.close()
    out_update.close()

    if line_count_new:
        id = task_low_level_submission("bibupload", "admin", "-N", "SCOAP3-import", "-a", name_new)
        write_message("Scheduled bibupload --append %s with ID #%s" % (name_new, id))
    else:
        remove(name_new)
    if line_count_update:
        id = task_low_level_submission("bibupload", "admin", "-N", "SCOAP3-import", "-c", name_update)
        write_message("Scheduled bibupload --correct %s with ID #%s" % (name_new, id))
    else:
        remove(name_update)
