#!/usr/bin/python
"""
    name:           bibfilter_oaicds2inspire
    decription:     Program to filter and analyse MARCXML records
                    harvested from external OAI sources, in order to determine
                    which action needs to be taken (insert, holding-area, etc)

                    Based on bibfilter_oaiarXiv2inspire
"""

import os
import sys
import getopt
import re

try:
    import json
except ImportError:
    import simplejson as json

from invenio.config import CFG_ETCDIR
from invenio.bibrecord import (create_record,
                               record_get_field_instances,
                               record_add_field, record_xml_output,
                               field_get_subfield_values,
                               record_get_field_values,
                               record_delete_field, record_delete_fields,
                               record_replace_field,
                               field_get_subfield_instances,
                               create_field, record_get_field_values,
                               record_strip_controlfields,
                               record_xml_output)
from invenio.search_engine import get_record, perform_request_search
from invenio.bibmerge_differ import record_diff, match_subfields
from invenio.bibupload import retrieve_rec_id
from invenio.bibmatch_engine import match_record
from invenio.textutils import wash_for_xml, wash_for_utf8
from invenio.search_engine import perform_request_search
from invenio.bibconvert_xslt_engine import convert

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


CONFIG_FILE = 'oaicds_bibfilter_config.json'

CONF_SERVER = 'localhost'

CONFIG = {}

# ==============================| Main |==============================


def main(args):
    config_path = CFG_ETCDIR + "/bibharvest/" + CONFIG_FILE

    if len(args) != 1:
        sys.stderr.write("Error: Missing MARCXML to analyse")
        sys.exit(1)

    input_filename = args[0]

    if not os.path.exists(input_filename):
        sys.stderr.write("Please input_xml a valid filename for input.")
        sys.exit(1)
    if not os.path.exists(config_path):
        sys.stderr.write("Please enter a valid filename for config.")
        sys.exit(1)

    load_config(config_path)
    record_tree = clean_oai_xml(input_filename)
    records = element_tree_to_record(record_tree)
    insert_records = []

    for record in records:
        # Step 1: Attempt to match the record to those already in Inspire
        recid = record['001'][0][3]
        res = attempt_record_match(recid)
        if not res:
            _print("Record %s not in INSPIRE" % (recid,))
            # No record found
            # Step 2: Appply filter to transform CDS MARC to Inspire MARC
            insert_records.append(apply_filter(record))
            #insert_records.append(record)
        else:
            _print("Record %s found in INSPIRE: %r Skipping.." % (recid, res))

    # Output results. Create new files, if necessary.
    write_record_to_file("%s.insert.xml" % (input_filename,), insert_records)
    print "%s.insert.xml" % (input_filename,)
    sys.stdout.write("Number of records to insert:  %d\n"
                     % (len(insert_records),))


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


def load_config(json_file=CONFIG_FILE):
    """ Loads configuration from JSON file """
    _print('Loading config from %s' % json_file)
    try:
        handle = open(json_file, 'r')
        conf = json.load(handle)
        handle.close()
    except IOError:
        _print("FATAL ERROR: Could not read config file.")
        sys.exit(1)

    global CONFIG
    CONFIG = {'config': {}}
    for key, values in conf['config'].iteritems():
        parse_dict = {}
        for di in values:
            try:
                parse_dict[di['cds']] = di['inspire']
            except KeyError:
                _print("ERROR: Could not parse dictionary pair %s" % repr(di))
        CONFIG['config'][key] = parse_dict


def determine_collection(setspec):
    """ Splits setSpec header attribute for collection """
    return setspec.split(':')[-1:][0].upper()


def element_tree_to_record(tree):
    """ Takes an ElementTree and converts the nodes
    into BibRecord records so they can be worked with
    This expects a clean OAI response with the tree root as GetRecord
    and record as the subtag like so:
    <ListRecords>
        <record>
            <header>
                <!--- Record Information --->
            </header>
            <metadata>
                <record>
                    <!--- MARCXML --->
                </record>
            </metadata>
        </record>
    </ListRecords>

    Parameters:
     * tree - ElementTree: Tree object corresponding to GetRecord node from
                           OAI request
    Returns: [(bibrecord, collection), ...] A list of tuples, with a BibRecord
        format in the first position and collection (string from setSpec) second
    """
    records = []
    oai_records = tree.getroot()
    for record_element in oai_records.getchildren():
        marc_root = record_element.find('metadata').find('record')
        marcxml = ET.tostring(marc_root)
        record, status, errors = create_record(marcxml)
        if status == 1:
            records.append(record)
        else:
            _print("ERROR: Could not create record from MARCXML")
            for err in errors:
                _print(" * %r" % (errors,))
        # set_spec = record_element.find('header').find('setSpec').text
    return records


def clean_oai_xml(xml):
    """ Cleans MARCXML harvested from OAI, allowing in
    to be used with BibUpload or BibRecord
    Parameters:
     * xml - either XML as a string or path to an XML file
    Returns: ElementTree of clean data """
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
    root = strip_xml_namespace(root)
    records = root.find('ListRecords')

    return ET.ElementTree(records)


def strip_xml_namespace(root):
    """ Strips out namespace data from an ElementTree
    This function is recursive and will traverse all
    subnodes to the root element
    Parameters:
     * root - the root element
    Returns: the same root element, minus namespace """
    try:
        root.tag = root.tag.split('}')[1]
    except IndexError:
        pass

    for element in root.getchildren():
        element = strip_xml_namespace(element)
    return root


def apply_filter(rec):
    """ Filters the record to be compatible within Inspire
    Parameters:
     * rec - dictionary: BibRecord structure
    Returns: dictionary, BibRecord structure
    """
    # Move recid from 001 to 035
    cds_id, pos = rec['001'][0][-2:]
    record_add_field(rec, '035', subfields=[('9', 'CDS'), ('a', cds_id)])
    # Clear control fields
    record_strip_controlfields(rec)

    # Clear other uninteresting fields
    uninteresting_fields = ["903", "963", "690", "859", "937"]
    for tag in uninteresting_fields:
        record_delete_fields(rec, tag)

    # 980 Determine Collections
    collections = set([])
    for value in record_get_field_values(rec, '980', code='a'):
        if 'NOTE' in value.upper():
            collections.add('NOTE')
        if 'THESIS' in value.upper():
            collections.add('THESIS')

    if is_published(rec):
        collections.add("PUBLISHED")
        collections.add("CITEABLE")

    # 980 Arxiv tag
    if record_get_field_values(rec, '035', filter_subfield_code="a",
                               filter_subfield_value="arXiv"):
        collections.add("arXiv")

    # 980 HEP && CORE
    collections.add('HEP')
    collections.add('CORE')

    record_delete_fields(rec, "980")

    intnote = record_get_field_values(rec, '690', filter_subfield_code="a",
                                      filter_subfield_value='INTNOTE')
    if intnote:
        val_088 = record_get_field_values(rec, '088', filter_subfield_code="a")
        for val in val_088:
            if 'CMS' in val:
                url = ('http://weblib.cern.ch/abstract?CERN-CMS' +
                       val.split('CMS', 1)[-1])
                record_add_field(rec, '856', ind1='4', subfields=[('u', url)])

    # FFT (856) Dealing with graphs
    for _idx, field in enumerate(record_get_field_instances(rec, '856')):
        subs = field_get_subfields(field)
        if 'z' in subs and 'Figure' in subs['z']:
            if not ('u' in subs and 'subformat' in subs['u']):
                newsubs = []
                url = ('/afs/cern.ch/project/inspire/uploads/cms-pas/%s_%s.png'
                       % (cds_id, subs['y'][0]))
                newsubs.append(('a', url))
                newsubs.append(('n', subs['y'][0]))
                newsubs.append(('f', '.png'))
                pos = '0000%s' % str(_idx + 1)
                newsubs.append(('d', pos))
                newsubs.append(('t', 'Plot'))
                newsubs.append(('z', 'KEEP-OLD-VALUE'))
                newsubs.append(('r', 'KEEP-OLD-VALUE'))
                record_add_field(rec, 'FFT', subfields=newsubs)

    # 041 Language
    languages = CONFIG['config']['languages']
    lang_fields = record_get_field_instances(rec, '041')
    for field in lang_fields:
        subs = []
        for key, value in field_get_subfield_instances(field):
            if key == 'a' and value in languages.keys():
                subs.append(('a', languages[value]))
            else:
                subs.append((key, value))
        new_field = field_swap_subfields(field, subs)
        record_replace_field(rec, '041', new_field,
                             field_position_global=field[4])

    # 035 Externals
    scn_035_fields = record_get_field_instances(rec, '035')
    forbidden_values = ["cercer",
                        "inspire",
                        "xx",
                        "cern annual report",
                        "cmscms",
                        "wai01"]
    for field in scn_035_fields:
        subs = field_get_subfields(field)
        if '9' in subs:
            if not 'a' in subs:
                continue
            for sub in subs['9']:
                if sub.lower() in forbidden_values:
                    break
            else:
                # No forbidden values (We did not "break")
                suffixes = [s.lower() for s in subs['9']]
                if 'spires' in suffixes:
                    new_sub = ('a', 'SPIRES-%s' % subs['a'])
                    record_add_field(rec, '970', subfields=new_sub)
                    continue
        if 'a' in subs:
            for sub in subs['a']:
                if sub.lower() in forbidden_values:
                    record_delete_field(rec, tag="035",
                                        field_position_global=field[4])

    rep_088_fields = record_get_field_instances(rec, '088')
    for field in rep_088_fields:
        subs = field_get_subfields(field)
        if '9' in subs:
            for val in subs['9']:
                if val.startswith('P0') or val.startswith('CM-P0'):
                    sf = [('9', 'CERN'), ('b', val)]
                    record_add_field(rec, '595', subfields=sf)
        for key, val in field[0]:
            if key in ['a', '9'] and not val.startswith('SIS-'):
                record_add_field(rec, '037', subfields=[('a', val)])
    record_delete_fields(rec, "088")

    rep_037_fields = record_get_field_instances(rec, '037')
    for field in rep_037_fields:
        subs = field_get_subfields(field)
        if 'a' in subs:
            for value in subs['a']:
                if 'arXiv' in value:
                    new_subs = [('a', value), ('9', 'arXiv')]
                    for fld in record_get_field_instances(rec,  '695'):
                        for key, val in field_get_subfield_instances(fld):
                            if key == 'a':
                                new_subs.append(('c', val))
                                break
                    nf = create_field(subfields=new_subs)
                    record_replace_field(rec, '037', nf, field[4])
        for key, val in field[0]:
            if key in ['a', '9'] and val.startswith('SIS-'):
                record_delete_field(rec, '037', field_position_global=field[4])

    for field in record_get_field_instances(rec, '242'):
        record_add_field(rec, '246', subfields=field[0])
    record_delete_fields(rec, '242')

    if not 'THESIS' in collections:
        for field in record_get_field_instances(rec, '260'):
            record_add_field(rec, '269', subfields=field[0])
        record_delete_fields(rec, '260')

    # 300 page number
    for field in record_get_field_instances(rec, '300'):
        for idx, (key, value) in enumerate(field[0]):
            if key == 'a':
                if "mult." not in value and value != " p":
                    field[0][idx] = ('a', re.sub(r'[^\d-]+', '', value))
                else:
                    record_delete_field(rec, '300',
                                        field_position_global=field[4])
                    break

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

    # 700 -> 701 Thesis supervisors
    if 'THESIS' in collections:
        for field in record_get_field_instances(rec, '700'):
            record_add_field(rec, '701', subfields=field[0])
        record_delete_fields(rec, '700')

    # 501 move subfields
    fields_501 = record_get_field_instances(rec, '502')
    for idx, field in enumerate(fields_501):
        new_subs = []
        for key, value in field[0]:
            if key == 'a':
                new_subs.append(('b', value))
            elif key == 'b':
                new_subs.append(('c', value))
            elif key == 'c':
                new_subs.append(('d', value))
            else:
                new_subs.append((key, value))
        fields_501[idx] = field_swap_subfields(field, new_subs)

    # 650 Translate Categories
    for field in record_get_field_instances(rec, '650', ind1='1', ind2='7'):
        for idx, (key, value) in enumerate(field[0]):
            if key == 'a' and translate_category(value) is not None:
                field[0][idx] = ('a', translate_category(value))

    # 653 Free Keywords
    for field in record_get_field_instances(rec, '653', ind1='1'):
        subs = field_get_subfields(field)
        new_subs = []
        if 'a' in subs:
            for val in subs['a']:
                new_subs.extend([('9', 'author'), ('a', val)])
        new_field = create_field(subfields=new_subs)
        record_replace_field(rec, '653', new_field, field_position_global=field[4])

    # 693 Remove if 'not applicable'
    for field in record_get_field_instances(rec, '693'):
        subs = field_get_subfields(field)
        if 'not applicable' in [x.lower() for x in subs['a']]:
            if 'not applicable' in [x.lower() for x in subs['e']]:
                record_delete_field(rec, '693',
                                    field_position_global=field[4])

    # 710 Collaboration
    for field in record_get_field_instances(rec, '710'):
        subs = field_get_subfield_instances(field)
        for idx, (key, value) in enumerate(subs[:]):
            if key == 'c':
                subs.pop(idx)
            elif value.startswith('CERN. Geneva'):
                subs.pop(idx)
        if len(subs) == 0:
            record_delete_field(rec, '710', field_position_global=field[4])

    # 773 journal translations
    journals = CONFIG["config"]["journals"]

    def _translate_journal(cds_jour):
        for the_d in journals:
            if the_d['cds'] == cds_jour:
                return the_d['inspire']
        return cds_jour

    for field in record_get_field_instances(rec, '773'):
        subs = field_get_subfield_instances(field)
        for idx, (key, value) in enumerate(subs):
            if key == 'p':
                subs[idx] = _translate_journal(value)

    # 856(4_) Figures!
    for field in record_get_field_instances(rec, '856', ind1='4'):
        subs = field_get_subfields(field)
        try:
            if not 'Figure' in subs['z']:
                for val in subs['u']:
                    if 'http://cdsweb.cern.ch' in val and val.endswith('.pdf'):
                        newsubs = [('t', 'NSPIRE-PUBLIC'), ('a', val)]
                        record_add_field(rec, 'FFT', subfields=newsubs)
        except KeyError:
            pass

        remove = True
        if 'u' in subs:
            urls = ('http://cdsweb.cern.ch', 'http://cms.cern.ch',
                    'http://cmsdoc.cern.ch', 'http://documents.cern.ch',
                    'http://preprints.cern.ch')
            for val in subs['u']:
                if any(url in val for url in urls):
                    remove = True
                    break
                if val.endswith('ps.gz'):
                    remove = True

            if remove:
                record_delete_field(rec, '856', ind1='4',
                                    field_position_global=field[4])

    for collection in collections:
        record_add_field(rec, '980', subfields=[('a', collection)])

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


def field_swap_subfields(field, subs):
    """ Recreates a field with a new set of subfields """
    return (subs, field[1], field[2], field[3], field[4])


def attempt_record_match(recid):
    """ Tries to find out if the record is already in Inspire """
    return perform_request_search(p="035:CDS and 035:%s" % (recid,), of="id")


def is_published(record):
    """ Checks fields 980 and 773 to see if the record has
    already been published.
    Parameters:
     * record - dictionary: BibRecord dictionary.
    Returns: True is published, else False """
    field980 = record_get_field_instances(record, '980')
    field773 = record_get_field_instances(record, '773')
    for f980 in field980:
        if 'a' in field_get_subfields(f980):
            for f773 in field773:
                if 'p' in field_get_subfields(f773):
                    return True
    return False


def translate_category(cds_cat):
    """ Given the string of a CDS category, this returns the Inspire
    equivilant by searching the imported configuration """
    categories = CONFIG["config"]["categories"]
    for the_d in categories:
        if the_d['cds'] == cds_cat:
            return the_d['inspire']
    return cds_cat


def punctuate_authorname(an):
    """ Punctuates author names, expects input in the form
    'Bloggs, J K'  and will return 'Bloggs, J. K.'
    Parameter:
     * an - string: the input CDS name
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


def _print(message, verbose=3):
    """ Print - verbosity to be included later """
    print message


# ==============================| Init, innit? |==============================
if __name__ == '__main__':
    main(sys.argv[1:])
