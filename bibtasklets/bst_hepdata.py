# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017, 2020, 2021 CERN.
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

import os
import shelve
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from tempfile import mkstemp

from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibtaskutils import ChunkedTask, ChunkedBibUpload
from invenio.bibtask import task_low_level_submission
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.jsonutils import json_unicode_to_utf8
from invenio.intbitset import intbitset
from invenio.search_engine import perform_request_search


HEPDATA_DUMP = os.path.join(CFG_TMPSHAREDDIR, 'hepdata_dump.bin')


def bst_hepdata():
    uploader = ChunkedHepDataUpload()
    dumper = HepDataDumper()
    for record in dumper:
        marcxml_record = hepdata2marcxml(record)
        uploader.add(marcxml_record)
    inspire_ids = dumper.inspire_ids
    current_inspire_ids = intbitset(perform_request_search(p='035__9:HEPDATA'))
    records_to_amend = inspire_ids - current_inspire_ids
    id_appender = ChunkedBibUpload(mode='a', user='hepdata')
    for recid in records_to_amend:
        rec = {}
        record_add_field(rec, tag="001", controlfield_value=str(recid))
        record_add_field(rec, tag="035", subfields=[('a', 'ins%s' % recid), ('9', 'HEPDATA')])
        id_appender.add(record_xml_output(rec))


class ChunkedHepDataUpload(ChunkedTask):
    @staticmethod
    def submitter(to_submit):
        # Save new record to file
        (temp_fd, temp_path) = mkstemp(prefix='hepdata',
                                       dir=CFG_TMPSHAREDDIR)
        temp_file = os.fdopen(temp_fd, 'w')
        temp_file.write('<?xml version="1.0" encoding="UTF-8"?>')
        temp_file.write('<collection>')
        for el in to_submit:
            temp_file.write(el)
        temp_file.write('</collection>')
        temp_file.close()

        args = ['bibupload', 'hepdata',
                '-P', str(3), '--insert', '--replace', '-N', 'hepdata',
                temp_path]

        return task_low_level_submission(*args)

class HepDataDumper(object):
    def __init__(self):
        self.old_dump = shelve.open(HEPDATA_DUMP, 'c', protocol=-1)
        self.new_dump = shelve.open(HEPDATA_DUMP + '.new', 'n', protocol=-1)
        self.inspire_ids = intbitset()

    def __iter__(self):
        chunk_size = 100
        page = 0

        retry_strategy = Retry(total=5,
                               backoff_factor=2,
                               status_forcelist=[429, 500, 502, 503, 504],
                               method_whitelist=["GET", "POST"])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        s = requests.Session()
        s.mount("https://", adapter)
        s.headers.update({'Accept': 'application/json'})

        while True:
            page += 1
            resp = s.get("https://hepdata.net/search/", params=dict(size=chunk_size, page=page), timeout=60)
            resp.raise_for_status()
            results = resp.json()['results']
            if not results:
                break
            for result in results:
                result = json_unicode_to_utf8(result)
                paper_title = result['title']
                inspire_id = result['inspire_id']
                self.inspire_ids.add(int(inspire_id))
                for position, data in enumerate(result['data'], 1):
                    data['paper_title'] = paper_title
                    data['inspire_id'] = inspire_id
                    data['position'] = position
                    if data['doi']:
                        self._store_record_in_dump(data)
                        if self._is_hepdata_record_new_or_updated(data):
                            yield data
        self._close_hepdata_dump()
        self._swap_hepdata_dump()

    def _store_record_in_dump(self, record):
        self.new_dump[record['doi']] = record

    def _is_hepdata_record_new_or_updated(self, record):
        return self.old_dump.get(record['doi'], {}) != record

    def _close_hepdata_dump(self):
        self.old_dump.close()
        self.new_dump.close()

    def _swap_hepdata_dump(self):
        os.rename(HEPDATA_DUMP + '.new', HEPDATA_DUMP)


def hepdata2marcxml(record):
    out = {}
    record_add_field(out, '024', '7', subfields=[('a', record['doi']), ('2', 'DOI')])
    if record.get('title'):
        title = 'Data from {title} from: {paper_title}'
    else:
        title = 'Additional data from: {paper_title}'
    record_add_field(out, '245', subfields=[('a', title.format(title=record.get('title'), paper_title=record['paper_title'])), ('9', 'HEPDATA')])
    record_add_field(out, '336', subfields=[('t', 'DATASET')])
    record_add_field(out, '520', subfields=[('h', record['abstract']), ('9', 'HEPDATA')])
    for keyword in record['keywords']:
        name = keyword['name']
        value = keyword['value']
        if name in ('observables', 'cmenergies'):
            value = '%s: %s' % (name, value)
        record_add_field(out, '695', subfields=[('a', value), ('9', 'HEPDATA')])
    for collaboration in record['collaborations']:
        record_add_field(out, '710', subfields=[('g', collaboration)])
    record_add_field(out, '786', subfields=[('q', str(record['position'])), ('w', str(record['inspire_id']))])
    record_add_field(out, '980', subfields=[('a', 'DATA')])
    return record_xml_output(out)
