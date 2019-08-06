#! /usr/bin/env python
# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014, 2018, 2019 CERN.
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
from datetime import datetime, timedelta
from glob import glob
from os import fdopen, remove, stat
from tempfile import mkstemp

from invenio.bibdocfile import BibRecDocs
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.bibtask import (task_low_level_submission,
                             task_sleep_now_if_required, write_message)
from invenio.config import CFG_TMPSHAREDDIR
from invenio.errorlib import register_exception
from invenio.search_engine import perform_request_search

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from sickle import Sickle

BASEURL = 'https://repo.scoap3.org/oai2d'
APIURL = 'https://repo.scoap3.org/api'


def bst_scoap3_importer():
    """Import from SCOAP3."""
    last_updated = '1970-01-01'
    recent_uploads = glob(CFG_TMPSHAREDDIR + '/bibupload_scoap3_*.xml')
    timestamp = 0
    try:
        timestamp = max([stat(f).st_mtime for f in recent_uploads])
    except OSError:
        pass
    if timestamp and timestamp > 0:
        last_updated = datetime.strftime(
            datetime.fromtimestamp(timestamp) - timedelta(days=7),
            "%Y-%m-%d")

    newids = set()
    try:
        sickle = Sickle(BASEURL)
        identifiers = sickle.ListIdentifiers(**{'metadataPrefix': 'oai_dc',
                                                'from': last_updated,
                                                'ignore_deleted': True})
        for sid in identifiers:
            scoaprecid = sid.identifier
            scoaprecid = scoaprecid.replace('oai:repo.scoap3.org:', '')
            newids.add(scoaprecid)
    except (HTTPError, ConnectionError, Timeout):
        register_exception()
        return
    if len(newids) == 0:
        write_message('No new records since last update %s' % last_updated)
        return

    task_sleep_now_if_required(can_stop_too=True)

    def _get_record_metadata(recid=None):
        if recid is None:
            return
        res = s.get('/'.join((APIURL, 'records', str(recid))))
        if res.status_code != 200:
            return
        try:
            recjson = res.json()
        except ValueError:
            write_message('Failed to retrieve json for recid %s' % recid)
            return
        metadata = recjson.get(u'metadata')
        if not metadata:
            write_message('No metadata for recid %s' % recid)
            return

        cr_date = recjson.get(u'created')
        dois = metadata.get(u'dois')
        arxiv = metadata.get(u'arxiv_eprints')
        files = metadata.get(u'_files')

        if arxiv and len(arxiv) > 1:
            write_message('More than one arXiv id for record %s' % recid)
            return
        elif arxiv:
            arxiv_id = arxiv[0].get(u'value')
        else:
            arxiv_id = None
        if dois and len(dois) > 1:
            write_message('More than one DOI for record %s' % recid)
        elif dois:
            doi = dois[0].get(u'value')
        else:
            doi = None

        if not files:
            return

        link = filefmt = ''
        checksum = None
        for f in files:
            if f.get(u'filetype') in (u'pdf/a', u'pdf'):
                filefmt = f.get(u'filetype').replace(u'/a', u';pdfa')
                filefmt = u'.' + filefmt
                checksum = f.get(u'checksum')
                if checksum.startswith(u'md5:'):
                    checksum = checksum[4:]
                bucket = f.get(u'bucket')
                key = f.get(u'key')
                if bucket and key:
                    link = '/'.join((APIURL, 'files', bucket, key))
                    break
        return recid, arxiv_id, cr_date, checksum, link, filefmt, doi

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

    s = requests.Session()
    for sid in newids:
        task_sleep_now_if_required(can_stop_too=True)
        values = _get_record_metadata(sid)
        if not values:
            write_message('No good metadata for recid %s' % sid)
            continue

        recid, arxiv_id, cr_date, checksum, link, file_format, doi = values

        write_message('processing %s' % ', '.join((recid, arxiv_id or 'None',
                                                   cr_date, checksum or 'None',
                                                   link, file_format, doi)))
        if checksum is None:
            write_message("... no PDF. Skipping")
            continue

        if arxiv_id is None:
            inspire_record = perform_request_search(p="doi:%s" % (doi, ),
                                                    cc="HEP")
        else:
            inspire_record = perform_request_search(p="037:%s or doi:%s" %
                                                    (arxiv_id, doi), cc="HEP")
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
        for doc in record.list_latest_files('SCOAP3'):
            if doc.format == file_format:
                if doc.checksum == checksum:
                    write_message("... OK: file alredy attached to INSPIRE record %s (doc.checksum=%s, checksum=%s)" % (inspire_record, doc.checksum, checksum))
                else:
                    # also check all previous version checksums
                    allchecksums = set()
                    for anydoc in record.list_bibdocs(doctype="SCOAP3"):
                        for filev in anydoc.list_all_files():
                            allchecksums.add(filev.checksum)
                    if checksum not in allchecksums:
                        write_message("... OK: new revision available for INSPIRE record %s (doc.checksum=%s, checksum=%s)" % (inspire_record, doc.checksum, checksum))
                        action = "UPDATE"
                break
        else:
            write_message("... OK: need to add new file to INSPIRE record %s" % inspire_record)
            action = "APPEND"
        if action:
            if file_format == '.pdf;pdfa':
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
        # We use correct here instead of append to deal with potential sync issues.
        # Basically BibUpload should handle "new" corrections as "append" if it is not there.
        tid = task_low_level_submission("bibupload", "admin", "-N", "SCOAP3-import", "-c", name_new)
        write_message("Scheduled bibupload --correct %s with ID #%s" % (name_new, tid))
    else:
        remove(name_new)
    if line_count_update:
        tid = task_low_level_submission("bibupload", "admin", "-N", "SCOAP3-import", "-c", name_update)
        write_message("Scheduled bibupload --correct %s with ID #%s" % (name_update, tid))
    else:
        remove(name_update)
