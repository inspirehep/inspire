#!/usr/bin/python
"""
    name:           bibfilter_oaicds2inspire
    decription:     Program to filter and analyse MARCXML records
                    harvested from external OAI sources, in order to determine
                    which action needs to be taken (insert, holding-area, etc)

                    Based on bibfilter_oaiarXiv2inspire
"""
from tempfile import mkstemp

import os
import sys
import re
import getopt

from itertools import product

try:
    import json
except ImportError:
    import simplejson as json

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
                               record_replace_field,
                               field_get_subfield_instances,
                               create_field,
                               record_strip_controlfields)
from invenio.search_engine import perform_request_search
from invenio.plotextractor_converter import convert_images
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


CONFIG_FILE = 'oaicds_bibfilter_config.json'
CONF_SERVER = 'localhost'
CONFIG = {}
PRINT_OUT = False

# ==============================| Main |==============================


def main(args):
    usage = """
    name:           bibfilter_oaicds2inspire
    decription:     Program to filter and analyse MARCXML records
                    harvested from external OAI sources, in particular CDS.
    usage:
                    bibfilter_oaicds2inspire [-nh] MARCXML-FILE
    options:
                -n  forces the script not to check if the record exists in the database
                    (useful when re-harvesting existing record)
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "nh", [])
    except getopt.GetoptError, err_obj:
        sys.stderr.write("Error:" + err_obj + "\n")
        print usage
        sys.exit(1)

    skip_recid_check = False

    for opt, opt_value in opts:
        if opt in ['-n']:
            skip_recid_check = True
        if opt in ['-h']:
            print usage
            sys.exit(0)

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
        except (KeyError, IndexError) as err:
            _print('Error: Cannot process record without 001:recid')
            error_records.append(record)
            continue

        if skip_recid_check or not res:
            _print("Record %s does not exist: inserting" % (recid,))
            # No record found
            # Step 2: Appply filter to transform CDS MARC to Inspire MARC
            insert_records.append(apply_filter(record))
            #insert_records.append(record)
        else:
            _print("Record %s found: %r" % (recid, res))

    for record in deleted_records:
        recid = record_get_field_values(record, tag="035", code="a")[0].split(":")[-1]
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


def load_config(json_file=CONFIG_FILE):
    """ Loads configuration from JSON file """
    _print('Loading config from %s' % json_file, verbose=5)
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


def get_languages():
    return CONFIG['config']['languages']


def get_journals():
    return CONFIG["config"]["journals"]


def get_experiments():
    return CONFIG["config"]["experiments"]


def get_categories():
    return CONFIG['config']['categories']


def determine_collection(setspec):
    """ Splits setSpec header attribute for collection """
    return setspec.split(':')[-1:][0].upper()


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
            record_add_field(deleted_record, "035", subfields=[("9", "CDS"), ("a", recid)])
            record_add_field(deleted_record, "037", subfields=subs)
            record_add_field(deleted_record, "980", subfields=[("c", "DELETED")])
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
    cds_id = rec['001'][0][3]
    if not 'hidden' in [x.lower() for x in record_get_field_values(rec, "980",
                                                                   code="a")]:
        record_add_field(rec, '035', subfields=[('9', 'CDS'), ('a', cds_id)])
    # Clear control fields
    record_strip_controlfields(rec)

    # Clear other uninteresting fields
    interesting_fields = ["024", "041", "035", "037", "088", "100",
                          "110", "111", "242", "245", "246", "260",
                          "269", "300", "502", "650", "653", "693",
                          "700", "710", "773", "856", "520", "500",
                          "980"]
    for tag in rec.keys():
        if tag not in interesting_fields:
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

    if not 'NOTE' in collections:
        # TODO: Move this to a KB
        kb = ['ATLAS-CONF-', 'CMS-PAS-', 'ATL-', 'CMS-DP-',
              'ALICE-INT-', 'LHCb-PUB-']
        values = record_get_field_values(rec, "088", code='a')
        for val, rep in product(values, kb):
            if val.startswith(rep):
                collections.add('NOTE')
                break

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

    # 041 Language
    languages = get_languages()
    language_fields = record_get_field_instances(rec, '041')
    record_delete_fields(rec, "041")
    for field in language_fields:
        subs = field_get_subfields(field)
        if 'a' in subs:
            if "eng" in subs['a']:
                continue
            new_value = translate_config(subs['a'][0], languages)
            new_subs = [('a', new_value)]
            record_add_field(rec, "041", subfields=new_subs)

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
                    new_subs = [('a', 'SPIRES-%s' % subs['a'][0])]
                    record_add_field(rec, '970', subfields=new_subs)
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

    # 269 Date normalization
    for field in record_get_field_instances(rec, '269'):
        for idx, (key, value) in enumerate(field[0]):
            if key == "c":
                field[0][idx] = ("c", convert_date_to_iso(value))
                record_delete_fields(rec, "260")

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
    categories = get_categories()
    category_fields = record_get_field_instances(rec, '650', ind1='1', ind2='7')
    record_delete_fields(rec, "650")
    for field in category_fields:
        for idx, (key, value) in enumerate(field[0]):
            if key == 'a':
                new_value = translate_config(value, categories)
                if new_value != value:
                    new_subs = [('2', 'INSPIRE'), ('a', new_value)]
                else:
                    new_subs = [('2', 'SzGeCERN'), ('a', value)]
                record_add_field(rec, "650", ind1="1", ind2="7",
                                 subfields=new_subs)
                break

    # 653 Free Keywords
    for field in record_get_field_instances(rec, '653', ind1='1'):
        subs = field_get_subfields(field)
        new_subs = []
        if 'a' in subs:
            for val in subs['a']:
                new_subs.extend([('9', 'author'), ('a', val)])
        new_field = create_field(subfields=new_subs)
        record_replace_field(rec, '653', new_field, field_position_global=field[4])

    experiments = get_experiments()
    # 693 Remove if 'not applicable'
    for field in record_get_field_instances(rec, '693'):
        subs = field_get_subfields(field)
        if 'not applicable' in [x.lower() for x in subs['a']]:
            if 'not applicable' in [x.lower() for x in subs['e']]:
                record_delete_field(rec, '693',
                                    field_position_global=field[4])
        new_subs = []
        experiment_a = ""
        experiment_e = ""
        for (key, value) in subs.iteritems():
            if key == 'a':
                experiment_a = value[0]
                new_subs.append((key, value[0]))
            elif key == 'e':
                experiment_e = value[0]
        experiment = "%s---%s" % (experiment_a.replace(" ", "-"),
                                  experiment_e)
        translated_experiments = translate_config(experiment,
                                                  experiments)
        new_subs.append(("e", translated_experiments))
        record_delete_field(rec, tag="693",
                            field_position_global=field[4])
        record_add_field(rec, "693", subfields=new_subs)

    # 710 Collaboration
    for field in record_get_field_instances(rec, '710'):
        subs = field_get_subfield_instances(field)
        for idx, (key, value) in enumerate(subs[:]):
            if key == '5':
                subs.pop(idx)
            elif value.startswith('CERN. Geneva'):
                subs.pop(idx)
        if len(subs) == 0:
            record_delete_field(rec, '710', field_position_global=field[4])

    # 773 journal translations
    journals = get_journals()
    for field in record_get_field_instances(rec, '773'):
        subs = field_get_subfield_instances(field)
        new_subs = []
        for idx, (key, value) in enumerate(subs):
            if key == 'p':
                new_subs.append((key, translate_config(value, journals)))
            else:
                new_subs.append((key, value))
        record_delete_field(rec, tag="773",
                            field_position_global=field[4])
        record_add_field(rec, "773", subfields=new_subs)

    # FFT (856) Dealing with graphs
    figure_counter = 0
    for field in record_get_field_instances(rec, '856', ind1='4'):
        subs = field_get_subfields(field)

        newsubs = []
        remove = False

        if 'z' in subs:
            is_figure = [s for s in subs['z'] if "figure" in s.lower()]
            if is_figure and 'u' in subs:
                is_subformat = [s for s in subs['u'] if "subformat" in s.lower()]
                if not is_subformat:
                    url = subs['u'][0]
                    if url.endswith(".pdf"):
                        # We try to convert
                        fd, local_url = mkstemp(suffix=os.path.basename(url), dir=CFG_TMPSHAREDDIR)
                        os.close(fd)
                        _print("Downloading %s into %s" % (url, local_url), verbose=5)
                        plotfile = ""
                        try:
                            plotfile = download_url(url=url,
                                                    download_to_file=local_url,
                                                    timeout=30.0)
                        except InvenioFileDownloadError:
                            _print("Download failed while attempting to reach %s. Skipping.." % (url,))
                            remove = True
                        if plotfile:
                            converted = convert_images([plotfile])
                            if converted:
                                url = converted.pop()
                                _print("Successfully converted %s to %s" % (local_url, url), verbose=5)
                            else:
                                _print("Conversion failed on %s" % (local_url,))
                                url = None
                                remove = True
                    if url:
                        newsubs.append(('a', url))
                        newsubs.append(('t', 'Plot'))
                        figure_counter += 1
                        if 'y' in subs:
                            newsubs.append(('d', "%05d %s" % (figure_counter, subs['y'][0])))
                            newsubs.append(('n', subs['y'][0]))
                        else:
                            # Get basename without extension.
                            name = os.path.basename(os.path.splitext(subs['u'][0])[0])
                            newsubs.append(('d', "%05d %s" % (figure_counter, name)))
                            newsubs.append(('n', name))

        if not newsubs and 'u' in subs:
            is_fulltext = [s for s in subs['u'] if ".pdf" in s]
            if is_fulltext:
                newsubs = [('t', 'INSPIRE-PUBLIC'), ('a', subs['u'][0])]

        if not newsubs and 'u' in subs:
            remove = True
            is_zipfile = [s for s in subs['u'] if ".zip" in s]
            if is_zipfile:
                url = is_zipfile[0]
                local_url = os.path.join(CFG_TMPSHAREDDIR, os.path.basename(url))
                _print("Downloading %s into %s" % (url, local_url), verbose=5)
                zipped_archive = ""
                try:
                    zipped_archive = download_url(url=is_zipfile[0],
                                                  download_to_file=local_url,
                                                  timeout=30.0)
                except InvenioFileDownloadError:
                    _print("Download failed while attempting to reach %s. Skipping.."
                           % (is_zipfile[0],))
                    remove = True
                if zipped_archive:
                    unzipped_archive = unzip(zipped_archive)
                    list_of_pngs = locate("*.png", unzipped_archive)
                    for png in list_of_pngs:
                        if "_vti_" in png or "__MACOSX" in png:
                            continue
                        figure_counter += 1
                        plotsubs = []
                        plotsubs.append(('a', png))
                        caption = '%05d %s' % (figure_counter, os.path.basename(png))
                        plotsubs.append(('d', caption))
                        plotsubs.append(('t', 'Plot'))
                        record_add_field(rec, 'FFT', subfields=plotsubs)

        if not remove and not newsubs and 'u' in subs:
            urls = ('http://cdsweb.cern.ch', 'http://cms.cern.ch',
                    'http://cmsdoc.cern.ch', 'http://documents.cern.ch',
                    'http://preprints.cern.ch', 'http://cds.cern.ch')
            for val in subs['u']:
                if any(url in val for url in urls):
                    remove = True
                    break
                if val.endswith('ps.gz'):
                    remove = True

        if newsubs:
            record_add_field(rec, 'FFT', subfields=newsubs)
            remove = True

        if remove:
            record_delete_field(rec, '856', ind1='4',
                                field_position_global=field[4])

    # 500 - Preliminary results
    subs = [('a', "Preliminary results")]
    record_add_field(rec, "500", subfields=subs)

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
    return subs, field[1], field[2], field[3], field[4]


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


def translate_config(key, config_dict):
    """ Given a string, this returns the Inspire equivilant
    found in the given config dictionary by searching the
    imported configuration """
    if key in config_dict:
        return config_dict[key]
    return key


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


def convert_date_to_iso(value):
    """
    Will try to convert a date-value to the ISO date standard.
    """
    date_formats = ["%d %b %Y", "%Y/%m/%d"]
    for dformat in date_formats:
        try:
            date = datetime.strptime(value, dformat)
            return date.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return value


def _print(message, verbose=1):
    """ Used for logging """
    write_message(message, verbose=verbose)
    if PRINT_OUT:
        print message


# ==============================| Init, innit? |==============================
if __name__ == '__main__':
    PRINT_OUT = True
    main(sys.argv[1:])
