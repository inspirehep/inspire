#!/usr/bin/env python
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

"""
    name:           bibfilter_zenodo2inspire
    decription:     Program to filter and analyse MARCXML records
                    harvested from external OAI sources, in order to determine
                    which action needs to be taken (insert, holding-area, etc)

                    Based on bibfilter_oaicds2inspire
"""
from tempfile import mkstemp

import os
import sys
import re
import getopt

from itertools import product

from invenio.dateutils import datetime
from invenio.apsharvest_utils import (unzip,
                                      locate)
from invenio.filedownloadutils import (download_url,
                                       InvenioFileDownloadError)
from invenio.config import (CFG_ETCDIR,
                            CFG_TMPSHAREDDIR)
from invenio.bibrecord import (create_record,
                               record_get_field_instances,
                               record_add_field,
                               record_xml_output,
                               record_get_field_values,
                               record_delete_field,
                               record_delete_fields,
                               field_get_subfield_instances,
                               create_field,
                               record_strip_controlfields)
from invenio.search_engine import perform_request_search
from invenio.bibtask import write_message

# NB: For future reference, elementtree.ElementTree is depreciated after
# Python 2.4, Inspire instances on higher Python versions should use xml.etree
# instead. The root.getiterator() function should also be updated.
try:
    import elementtree.ElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

#python2.4 compatibility layer. Function any() is not included in 2.4
try:
    any([True])
except NameError:
    def any(x):
        for element in x:
            if element:
                return True
        return False

PRINT_OUT = False


def main(args):
    usage = """
    name:           bibfilter_zenodo2inspire
    decription:     Program to filter and analyse MARCXML records
                    harvested from external OAI sources, in particular Zenodo datasets.
    usage:
                    bibfilter_zenodo2inspire [-nh] MARCXML-FILE
    options:
                -n  forces the script not to check if the record exists in the database
                    (useful when re-harvesting existing record)
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "nh", [])
    except getopt.GetoptError as err_obj:
        sys.stderr.write("Error:" + err_obj + "\n")
        print(usage)
        sys.exit(1)

    skip_recid_check = False

    for opt, opt_value in opts:
        if opt in ['-n']:
            skip_recid_check = True
        if opt in ['-h']:
            print(usage)
            sys.exit(0)

    if len(args) != 1:
        sys.stderr.write("Error: Missing MARCXML to analyse")
        sys.exit(1)

    input_filename = args[0]

    if not os.path.exists(input_filename):
        sys.stderr.write("Please input_xml a valid filename for input.")
        sys.exit(1)

    # Hack to activate UTF-8
    reload(sys)
    sys.setdefaultencoding("utf8")
    assert sys.getdefaultencoding() == "utf8"

    record_tree, next_process, header_subs = clean_xml(input_filename)
    records, deleted_records = next_process(record_tree, header_subs)
    insert_records = []
    append_records = []
    error_records = []

    for record in records:
        # Step 1: Attempt to match the record to those already in Inspire
        try:
            recid = record['001'][0][3]
            res = attempt_record_match(recid)
            print(res)
        except (KeyError, IndexError) as err:
            _print('Error: Cannot process record without 001:recid')
            error_records.append(record)
            continue

        if skip_recid_check or not res:
            _print("Record %s does not exist: inserting" % (recid,))
            # No record found
            # Step 2: Appply filter to transform Zenodo MARC to Inspire MARC
            insert_records.append(apply_filter(record))
            #insert_records.append(record)
        else:
            _print("Record %s found: %r" % (recid, res))

    for record in deleted_records:
        recid = record_get_field_values(record,
                                        tag="035",
                                        code="a")[0].split(":")[-1]
        res = attempt_record_match(recid)
        if res:
            # Record exists and we should then delete it
            _print("Record %s exists. Delete it" % (recid,))
            append_records.append(record)

    # Output results. Create new files, if necessary.
    if input_filename[-4:].lower() == '.xml':
        input_filename = input_filename[:-4]

    write_record_to_file("%s.insert.xml" % (input_filename,), insert_records)
    _print("%s.insert.xml" % (input_filename,))
    _print("Number of records to insert:  %d\n"
           % (len(insert_records),))
    write_record_to_file("%s.append.xml" % (input_filename,), append_records)
    _print("%s.append.xml" % (input_filename,))
    _print("Number of records to append:  %d\n"
           % (len(append_records),))
    write_record_to_file("%s.errors.xml" % (input_filename,), error_records)
    _print("%s.errors.xml" % (input_filename,))
    _print("Number of records with errors:  %d\n"
           % (len(append_records),))


# ==============================| Functions |==============================


def write_record_to_file(filename, record_list):
    """
    Writes a new MARCXML file to specified path from a list of records.
    """
    if len(record_list) > 0:
        out = []
        out.append("<collection>")
        for record in record_list:
            if record != {}:
                out.append(record_xml_output(record))
        out.append("</collection>")
        if len(out) > 2:
            file_fd = open(filename, 'w')
            file_fd.write("\n".join(out))
            file_fd.close()


def element_tree_to_record(tree, header_subs=None):
    marcxml = ET.tostring(tree.getroot(), encoding="utf-8")
    record, status, errors = create_record(marcxml)
    if errors:
        _print(str(status))
    return [record], []


def element_tree_collection_to_records(tree, header_subs=None):
    """ Takes an ElementTree and converts the nodes
    into BibRecord records so they can be worked with.
    This function is for a tree root of collection as such:
    <collection>
        <record>
            <!-- MARCXML -->
        </record>
        <record> ... </record>
    </collection>
    """
    records = []
    collection = tree.getroot()
    for record_element in collection.getchildren():
        marcxml = ET.tostring(record_element, encoding="utf-8")
        record, status, errors = create_record(marcxml)
        if errors:
            _print(str(status))
        records.append(record)
    return records, []


def element_tree_oai_to_records(tree, header_subs=None):
    """ Takes an ElementTree and converts the nodes
    into BibRecord records so they can be worked with.
    This expects a clean OAI response with the tree root as ListRecords or GetRecord
    and record as the subtag like so:
    <ListRecords|GetRecord>
        <record>
            <header>
                <!-- Record Information -->
            </header>
            <metadata>
                <record>
                    <!-- MARCXML -->
                </record>
            </metadata>
        </record>
        <record> ... </record>
    </ListRecords|GetRecord>

    @param tree: ElementTree: Tree object corresponding to GetRecord node from
                              OAI request
    @param header_subs: OAI header subfields, if any

    @return: (record_list, deleted_list) A tuple, with first a list of BibRecords
             found and second a list of BibRecords to delete.
    """
    records = []
    deleted_records = []
    if not header_subs:
        header_subs = []
    # Make it a tuple, this information should not be changed
    header_subs = tuple(header_subs)

    oai_records = tree.getroot()
    for record_element in oai_records.getchildren():
        header = record_element.find('header')

        # Add to OAI subfield
        datestamp = header.find('datestamp')
        identifier = header.find('identifier')
        identifier = identifier.text

        # The record's subfield is based on header information
        subs = list(header_subs)
        subs.append(("a", identifier))
        subs.append(("d", datestamp.text))

        if "status" in header.attrib and header.attrib["status"] == "deleted":
            # Record was deleted - create delete record
            recid = identifier.split(":")[-1]
            deleted_record = {}
            record_add_field(deleted_record,
                             "035",
                             subfields=[("9", "Zenodo"), ("a", recid)])
            record_add_field(deleted_record,
                             "037",
                             subfields=subs)
            record_add_field(deleted_record,
                             "980",
                             subfields=[("c", "DELETED")])
            deleted_records.append(deleted_record)
            _print("Record has been deleted: %s" % (identifier,))
            continue

        marc_root = record_element.find('metadata').find('record')
        marcxml = ET.tostring(marc_root, encoding="utf-8")
        record, status, errors = create_record(marcxml)
        if status == 1:
            # Add OAI request information
            record_add_field(record, "035", subfields=subs)
            records.append(record)
        else:
            _print("ERROR: Could not create record from %s" % (identifier,))
            _print(" * %r" % (errors,))
    return records, deleted_records


def get_request_subfields(root):
    """
    Builds a basic 035 subfield with basic information from the OAI-PMH request.

    @param root: ElementTree root node

    @return: list of subfield tuples [(..),(..)]
    """
    request = root.find('request')
    responsedate = root.find('responseDate')

    subs = [("9", request.text),
            ("h", responsedate.text),
            ("m", request.attrib["metadataPrefix"])]
    return subs


def clean_xml(xml):
    """
    Cleans MARCXML harvested from OAI, allowing in
    to be used with BibUpload or BibRecord

    @param xml: either XML as a string or path to an XML file

    @return: ElementTree of clean data
    """
    try:
        if os.path.isfile(xml):
            tree = ET.parse(xml)
        else:
            _print("Warning: input is not a valid file, attempting to parse " +
                   "input as XML...")
            tree = ET.fromstring(xml)
    except Exception, e:
        _print("ERROR: Could not read OAI XML, aborting filter!")
        raise e
    root = tree.getroot()
    strip_xml_namespace(root)
    if root.tag.lower() == 'collection':
        return ET.ElementTree(root), element_tree_collection_to_records, None
    elif root.tag.lower() == 'record':
        new_root = ET.Element('collection')
        new_root.append(root)
        return ET.ElementTree(new_root), element_tree_to_record, None

    header_subs = get_request_subfields(root)

    records = root.find('ListRecords')
    if records is None:
        records = root.find('GetRecord')
    if records is None:
        raise ValueError("Cannot find ListRecords or GetRecord!")

    return ET.ElementTree(records), element_tree_oai_to_records, header_subs


def strip_xml_namespace(root):
    """
    Strips out namespace data from an ElementTree
    This function is recursive and will traverse all
    subnodes to the root element

    @param root: the root element

    @return: the same root element, minus namespace
    """
    try:
        root.tag = root.tag.split('}')[1]
    except IndexError:
        pass

    for element in root.getchildren():
        strip_xml_namespace(element)


def apply_filter(rec):
    """ Filters the record to be compatible within Inspire
    Parameters:
     * rec - dictionary: BibRecord structure
    Returns: dictionary, BibRecord structure
    """
    # Move recid from 001 to 035 if not hidden
    zenodo_id = rec['001'][0][3]
    if not 'hidden' in [x.lower() for x in record_get_field_values(rec, "980",
                                                                   code="a")]:
        record_add_field(rec,
                         '035',
                         subfields=[('9', 'Zenodo'), ('a', zenodo_id)])

    # Clear control fields
    record_strip_controlfields(rec)

    # Clear other uninteresting fields
    interesting_fields = ["024", "035", "100",
                          "245", "260", "700",
                          "710", "773", "856",
                          "520", "500"]
    for tag in rec.keys():
        if tag not in interesting_fields:
            record_delete_fields(rec, tag)

    descriptions = record_get_field_instances(rec, '520')
    record_delete_fields(rec, '520')
    for desc in descriptions:
        subs = field_get_subfields(desc)
        if 'a' in subs:
            record_add_field(rec,
                             "520",
                             subfields=[('9', 'Zenodo'), ('h', subs['a'][0])])

    # 100 & 700 punctuate author names
    author_names = record_get_field_instances(rec, '100')
    author_names.extend(record_get_field_instances(rec, '700'))
    for field in author_names:
        subs = field_get_subfields(field)
        if not 'i' in subs or 'XX' in subs['i']:
            if not 'j' in subs or 'YY' in subs['j']:
                for idx, (key, value) in enumerate(field[0]):
                    if key == 'a':
                        field[0][idx] = ('a', punctuate_authorname(value))

    # 773 is cited by, DOI of the extended paper
    # match the INSPIRE record ID of that paper and add it in 786__w
    for field in record_get_field_instances(rec, '773'):
        subs = field_get_subfields(field)
        if 'i' in subs and 'isSupplementTo' in subs['i']:
            if 'n' in subs and "doi" in [s.lower() for s in subs['n']]:
                paper_recid = perform_request_search(
                    p="0247_a:%s" % subs['a'][0],
                    of="id"
                )

                if paper_recid:
                    record_add_field(rec,
                                     "786",
                                     subfields=[('w', str(paper_recid[0]))])
            if 'n' in subs and "arxiv" in [s.lower() for s in subs['n']]:
                paper_recid = perform_request_search(
                    p="037__a:%s" % subs['a'][0],
                    of="id"
                )

                if paper_recid:
                    record_add_field(rec,
                                     "786",
                                     subfields=[('w', str(paper_recid[0]))])

    # Other mandatory fields
    # 786 formatting
    record_add_field(rec, "786", subfields=[('q', '0')])

    # 980 only DATA Collection
    record_add_field(rec, '980', subfields=[('a', 'DATA')])

    return rec


def field_get_subfields(field):
    """ Given a field, will place all subfields into a dictionary
    Parameters:
     * field - tuple: The field to get subfields for
    Returns: a dictionary, codes as keys and a list of values as the value """
    pairs = {}
    for key, value in field[0]:
        if key in pairs and pairs[key] != value:
            pairs[key].append(value)
        else:
            pairs[key] = [value]
    return pairs


def attempt_record_match(recid):
    """ Tries to find out if the record is already in Inspire """
    return perform_request_search(
        p="035:Zenodo and 035:%s and 980:DATA" % (recid,),
        of="id",
        c="Data"
    )


def punctuate_authorname(an):
    """ Punctuates author names, expects input in the form
    'Bloggs, J K'  and will return 'Bloggs, J. K.'
    Parameter:
     * an - string: the input name
    Returns: string, the formatted Inspire name """
    name = an.strip()
    parts = [x for x in name.split(',') if x != '']
    ret_str = ''
    for idx, part in enumerate(parts):
        subparts = part.strip().split(' ')
        for sidx, substr in enumerate(subparts):
            ret_str += substr
            if len(substr) == 1:
                ret_str += '.'
            if sidx < (len(subparts) - 1):
                ret_str += ' '
        if idx < (len(parts) - 1):
            ret_str += ', '
    return ret_str.strip()


def _print(message, verbose=1):
    """ Used for logging """
    write_message(message, verbose=verbose)
    if PRINT_OUT:
        print message


if __name__ == '__main__':
    PRINT_OUT = True
    main(sys.argv[1:])
