# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013, 2014, 2015 CERN.
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

""" Delete VOLATILE contents from records in given collection. """

import codecs
import os
import time
from copy import deepcopy
from invenio.bibrecord import \
    create_records, \
    record_delete_subfield_from, \
    record_xml_output
from invenio.search_engine import \
    search_pattern, \
    get_collection_reclist, \
    get_record

from tempfile import mkstemp
from invenio.bibtask import write_message, task_low_level_submission
from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibedit_config import CFG_BIBEDIT_RECORD_TEMPLATES_PATH

TEMPLATE_TYPES = {'HEP': ['HEP', 'article', 'book_chapter', 'book', 'thesis',
                          'conference_paper', 'preprint', 'proceedings'],
                  'Conferences' : ['conference', 'conference'],
                  'HepNames' : ['hepnames', 'hepnames'],
                  'Experiments': ['experiment', 'experiment'],
                  'Institutions': ['institution', 'institution'],
                  'Jobs': ['jobs', 'jobs'],
                  'Data': ['data', 'data_template']
                 }

def read_record(filename):
    """
    Read template as record

    @param filename: base_name of template file
    @type  filename: string
    @yield: record
    """

    path_templates = CFG_BIBEDIT_RECORD_TEMPLATES_PATH
    template = codecs.EncodedFile(codecs.open('%s%s%s' %
               (path_templates, os.sep, filename), mode='r'), 'utf8')
    xmlrecords = template.read()
    recs = create_records(xmlrecords, verbose=1)
    template.close()
    for recordtuple in recs:
        if recordtuple[1] != 0:
            yield recordtuple[0]

def read_templates(collection):
    """
    Read templates, return dict of fields to check.

    @param collection: collection to be checked
    @type  collection: string
    @return: dict {tagiic: array of search_strings}
    """

    subfields = {}
    if not TEMPLATE_TYPES.has_key(collection):
        write_message('ERROR: collection %s not available' % collection)
        return subfields

    filename = 'volatile_check_' + TEMPLATE_TYPES[collection][0] + '.xml_ignore'
    sf_ignore = {}
    for record in read_record(filename):
        for tag in record.keys():
            for field in record[tag]:
                tagii = tag + field[1] + field[2]
                tagii = tagii.replace(' ', '_')
                for code, value in field[0]:
                    tagiic = tagii + code
                    value = value.replace('VOLATILE:', '', 1).strip()
                    if sf_ignore.has_key(tagiic):
                        sf_ignore[tagiic].append(value)
                    else:
                        sf_ignore[tagiic] = [value, ]

    ignore_tags = ['980', 'FFT']
    for typ in TEMPLATE_TYPES[collection][1:]:
        filename = 'record_' + typ + '.xml'
        for record in read_record(filename):
            for tag in record.keys():
                if tag in ignore_tags:
                    continue
                for field in record[tag]:
                    tagii = tag + field[1] + field[2]
                    tagii = tagii.replace(' ', '_')
                    for code, value in field[0]:
                        tagiic = tagii + code
                        value = value.replace('VOLATILE:', '', 1).strip()
                        if sf_ignore.has_key(tagiic) and \
                            value in sf_ignore[tagiic]:
                            pass
                        else:
                            if subfields.has_key(tagiic):
                                if not value in subfields[tagiic]:
                                    subfields[tagiic].append(value)
                            else:
                                subfields[tagiic] = [value, ]
    return subfields

def find_records(collection, subfields):
    """
    Find records with VOLATILE content.

    @param collection: collection to be checked
    @type  collection: string
    @param subfields: VOLATILE content in tagiic
    @type  subfields: dict
    @return: dict {recid: array of tagiic}
    """

    sf_keys = subfields.keys()
    sf_keys.sort()

    recs_collection = get_collection_reclist(collection)
    recs_to_change = {}
    for tagiic in sf_keys:
        for value in subfields[tagiic]:
            result = search_pattern(p=value, f=tagiic, m='e') & recs_collection
            if result:
                write_message('Update %i records with %s:"%s" -- %s' \
                              % (len(result), tagiic, value, list(result)))
            for recid in result:
                if recs_to_change.has_key(recid):
                    recs_to_change[recid].append(tagiic)
                else:
                    recs_to_change[recid] = [tagiic, ]
    return recs_to_change

def create_xml(recs_to_change, subfields):
    """
    Create xmls for upload.

    @param recs_to_change: affected tagiic in recid
    @type  recs_to_change: dict
    @param subfields: VOLATILE content in tagiic
    @type  subfields: dict
    @return: (string, string) xml's for correct and delete
    """

    xml_correct = ''
    xml_delete = ''
    for recid in recs_to_change.keys():
        tags_correct = []
        tags_delete = []
        tags4update = []
        record_old = get_record(recid)
        record = deepcopy(record_old)
        for tagiic in recs_to_change[recid]:
            tag = tagiic[:3]
            for value in subfields[tagiic]:
                if record.has_key(tag):
                    for field_position, field in enumerate(record[tag]):
                        for subfield_position, subfield in enumerate(field[0]):
                            if subfield[1] == value and subfield[0] == tagiic[5]:
                                record_delete_subfield_from(
                                    record, tag, subfield_position,
                                    field_position_local=field_position)
                                tags4update.append(tag)
        for tag in set(tags4update):
            if record.has_key(tag):
                tags_correct.append(tag)
            else:
                tags_delete.append(tag)
        if tags_correct:
            xml_correct += record_xml_output(record,
                                             ['001', '005'] + tags_correct) + '\n'
        if tags_delete:
            xml_delete += record_xml_output(record_old,
                                            ['001', '005'] + tags_delete) + '\n'
    return xml_correct, xml_delete

def submit_xml(xml, mode, stamp):
    """
    Write temporary xml file and submit for batchupload.
    Do nothing for empty xml.

    @param xml: body xml
    @param mode: mode for upload ['delete' | 'correct']
    @param stamp: additional string in filename
    """

    if not xml:
        return

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<collection>\n'\
          + xml + '\n</collection>\n'
    tmp_file_fd, tmp_file = mkstemp(
                            suffix='.xml',
                            prefix="bst_check4template-%s_%s" % (mode, stamp),
                            dir=CFG_TMPSHAREDDIR
                            )
    os.write(tmp_file_fd, xml)
    os.close(tmp_file_fd)
    os.chmod(tmp_file, 0644)
    if mode == 'delete':
        flag = '-d'
    elif mode == 'correct':
        flag = '-c'
    else:
        write_message("Wrong mode: %s" % mode)
        return

    task = task_low_level_submission('bibupload', 'check4template',
                                     flag, tmp_file)
    write_message("Submitted bibupload task %s" % task)

def check4template(collections, max_update):
    """
    Delete VOLATILE contents from records in collections.

    @param collections: list of collection to be checked
    @type  collections: list
    @param max_update: max number of records to be updated
    @type  max_update: integer
    """

    num_records = 0
    xmlupload_correct = ""
    xmlupload_delete = ""

    for collection in collections:
        write_message('\nChecking %s for left over VOLATILE content from templates'\
                      % collection)

# what to search for
        subfields = read_templates(collection)

# which records are affected
        recs_to_change = find_records(collection, subfields)
        num_records += len(recs_to_change.keys())

# create xml for upload
        xml_correct, xml_delete = create_xml(recs_to_change, subfields)
        xmlupload_correct += xml_correct
        xmlupload_delete += xml_delete

# output - upload job
    if num_records == 0:
        write_message('No records to be updated')
    elif num_records > max_update:
        write_message('WARNING: %i records to be updated, MAX=%i' %
                      (num_records, max_update))
    else:
        write_message('---\nUpdate %i records in total\n' % num_records)
        time_stamp = time.strftime("%Y-%m-%d_%H%M%S")
        submit_xml(xmlupload_correct, "correct", time_stamp)
        submit_xml(xmlupload_delete, "delete", time_stamp)

def bst_check4template(collections="", max_update="30"):
    """
    Delete VOLATILE contents from records in given collections.

    @param collections: comma separated list of collections,
                        default: all collections
    @param max_update: max number of records to be updated
    """

    if collections:
        coll_list = collections.split(',')
    else:
        coll_list = TEMPLATE_TYPES.keys()

    check4template(coll_list, int(max_update))

if __name__ == "__main__":
    bst_check4template()
