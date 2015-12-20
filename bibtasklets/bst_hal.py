# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
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

"""
This script harvest from HAL all the possible arXiv IDs and DOIs and
try to match them to record in INSPIRE.
"""

import requests
import sys

from invenio.jsonutils import json_unicode_to_utf8
from invenio.search_engine import search_pattern
from invenio.search_engine_utils import get_fieldvalues
from invenio.bibsched_tasklets.bst_inspire_cds_synchro import get_record_ids_to_export
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.bibtask import write_message, task_sleep_now_if_required
from invenio.bibtaskutils import ChunkedBibUpload

CFG_HAL_API_URL = "http://api.archives-ouvertes.fr/search"
CFG_HAL_ROWS = 10000

def hal_record_iterator():
    start = 0
    while True:
        res = requests.get(CFG_HAL_API_URL, params={'start': start,
                                             'q': '(arxivId_s:* OR doiId_s:*)',
                                             'fl': 'arxivId_s,halId_s,doiId_s',
                                             'rows': CFG_HAL_ROWS,
                                             'sort': 'docid asc'}).json()
        if res['response']['docs']:
            for row in res['response']['docs']:
                yield json_unicode_to_utf8(row)
            start += CFG_HAL_ROWS
            write_message("%s out of %s" % (start, res['response']['numFound']))
        else:
            return

def get_hal_records():
    return search_pattern(p='035__9:"HAL"')


def get_hal_maps():
    write_message("Getting HAL records...")
    doi_map = {}
    arxiv_map = {}
    for row in hal_record_iterator():
        if 'arxivId_s' in row:
            if row['arxivId_s'][0].isdigit():
                # we patch 1234.1234 -> arXiv:1234.1234
                row['arxivId_s'] = 'arXiv:%s' % row['arxivId_s']
            arxiv_map[row['arxivId_s']] = row
        if 'doiId_s' in row:
            doi_map[row['doiId_s']] = row
    write_message("... DONE")
    return doi_map, arxiv_map

def bst_hal():
    doi_map, arxiv_map = get_hal_maps()
    matchable_records = get_record_ids_to_export()
    write_message("Total matchable records: %s" % len(matchable_records))
    hal_records = get_hal_records()
    write_message("Already matched records: %s" % len(hal_records))
    bibupload = ChunkedBibUpload(mode='a', notimechange=True, user='bst_hal')
    tot_records = matchable_records - hal_records
    write_message("Records to be checked: %s" % len(tot_records))
    for i, recid in enumerate(tot_records):
        if i % 1000 == 0:
            write_message("%s records done out of %s" % (i, len(tot_records)))
            task_sleep_now_if_required()
        dois = get_fieldvalues(recid, tag='0247__a', sort=False)
        arxivs = get_fieldvalues(recid, tag='037__a', sort=False)
        matched_hal = [doi_map[doi] for doi in dois if doi in doi_map]
        matched_hal += [arxiv_map[arxiv] for arxiv in arxivs if arxiv in arxiv_map]

        # Let's assert that we matched only one single hal document at most
        matched_hal_id = set(id(entry) for entry in matched_hal)
        if len(matched_hal) > 1:
            write_message("WARNING: record %s matches more than 1 HAL record: %s" % (recid, matched_hal), stream=sys.stderr)
            continue
        elif not matched_hal:
            continue
        hal_id = matched_hal[0]['halId_s']

        rec = {}
        record_add_field(rec, '001', controlfield_value=str(recid))
        record_add_field(rec, '035', subfields=[('a', hal_id), ('9', 'HAL')])

        write_message("Record %s matched HAL record %s" % (recid, hal_id))

        bibupload.add(record_xml_output(rec))

    return True
