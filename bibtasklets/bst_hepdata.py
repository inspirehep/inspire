# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

from tempfile import mkstemp

from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibtaskutils import ChunkedTask
from invenio.bibtask import task_low_level_submission
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.jsonutils import json_unicode_to_utf8


HEPDATA_DUMP = os.path.join(CFG_TMPSHAREDDIR, 'hepdata_dump.bin')


def bst_hepdata():
    uploader = ChunkedHepDataUpload()
    for record in HepDataDumper():
        marcxml_record = hepdata2marcxml(record)
        uploader.add(marcxml_record)


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

    def __iter__(self):
        chunk_size = 200
        page = 0
        while True:
            page += 1
            results = requests.get("https://hepdata.net/search/", params=dict(size=chunk_size, page=page), headers={'Accept': 'application/json'}).json()['results']
            if not results:
                break
            for i, result in enumerate(results):
                result = json_unicode_to_utf8(result)
                paper_title = result['title']
                inspire_id = result['inspire_id']
                for data in result['data']:
                    data['paper_title'] = paper_title
                    data['inspire_id'] = inspire_id
                    data['position'] = i+1
                    if data['doi']:
                        self._store_record_in_dump(data)
                        if self._is_hepdata_record_new_or_updated(data):
                            yield data
        self._close_hepdata_dump()
        self._swap_hepdata_dump()

    def _store_record_in_dump(self, record):
        self.new_dump[record['doi']] = record

    def _is_hepdata_record_new_or_updated(self, record):
        newrec = record.copy()
        newrec.pop('position', '')
        oldrec = self.old_dump.get(record['doi'], {})
        oldrec.pop('position', '')
        return oldrec != newrec

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
