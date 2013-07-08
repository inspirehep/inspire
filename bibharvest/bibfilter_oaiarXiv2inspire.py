#!/usr/bin/python
"""
    name:           bibfilter_oaiarXiv2inspire
    decription:     Program to filter and analyse MARCXML records
                    harvested from external OAI sources, in order to determine
                    which action needs to be taken (insert, holding-area, etc)
"""

import os
import sys
import getopt

from invenio.bibupload import open_marc_file
from invenio.config import CFG_ETCDIR
from invenio.bibrecord import create_records, \
                              record_get_field_instances, \
                              record_add_field, record_xml_output, \
                              field_get_subfield_values, \
                              record_get_field_values, \
                              record_get_field_value
from invenio.search_engine import get_record
from invenio.bibmerge_differ import record_diff, match_subfields
from invenio.bibupload import retrieve_rec_id
from invenio.textutils import wash_for_xml, wash_for_utf8
from invenio.search_engine import perform_request_search
from invenio.oai_harvest_daemon import create_ticket


def parse_actions(action_line):
    """
    Parses action list and returns list of tuples [(diff_code, action),..].
    It expects a string with the following structure:

    "diff_code1 -> action1, diff_code2 -> action2"
    where:
        actionN is one of ["append", "holdingpen", "correct"]
        diff_codeN is one of ["c","a","r"]
    """
    actions = []
    for action in action_line:
        parts = action.split('->')
        if len(parts) != 2:
            print "Error, action's file does not fit the syntax rules"
            sys.exit(4)
        diff_code = parts[0].strip()
        action = parts[1].strip()
        if action not in ["append", "holdingpen", "correct"] or diff_code not in "rca":
            print "Error, action's file does not fit the syntax rules"
            sys.exit(4)
        actions.append((diff_code, action))
    return actions


def read_actions_configuration_file(filename):
    """
    Reads the configuration file describing actions to be taken.

    Each other line should be build in the following format:
    identifier, change_type -> action1, change_type -> action2, ...
    where actionN is one of [append, correct, holdingpen]
       append : add field content
       correct : replace existing fields with new fields
       holdingpen: puts the entire record update in holdingpen for manual oversight

    identifier is either a field-tag or default

    @result actions
    """
    if not os.path.exists(filename):
        sys.stderr.write("Error: Missing configuration file")
        sys.exit(4)
    f = open(filename, "r")
    content = f.readlines()
    f.close()
    actions = {}

    for line in content:
        if line.strip() == "":
            continue
        parts = line.split(",")
        if len(parts) < 2:
            sys.stderr.write("Error when parsing the actions configuration file %s" % (str(parts)))
            sys.exit(4)
        identifier = parts[0]
        parsed_actions = parse_actions(parts[1:])
        actions.setdefault(identifier, []).append(parsed_actions)
    return actions


def get_action(tag, diff_code, action_dict):
    """
    Returns an 'action'-string describing the action to be taken.
    It will iterate over an action_dict containing elements of this structure:

    'tag': [('code', 'act'), ..]

    """
    actionlist = []
    # Check if tag is specified in config
    if tag not in action_dict:
        tag = "default"
    actionlist = action_dict[tag]
    for actions in actionlist:
        for code, act in actions:
            if diff_code in code:
                return act
    else:
        # tag->code not specified in configuration file, lets do defaults
        for actions in action_dict["default"]:
            for code, act in actions:
                if diff_code in code:
                    return act
    return None


def create_record_from_list(recid, field_list):
    """
    Returns a new record from a list of (tag, subfields) tuples and adds the recid.
    It also checks against an record if a field already exists, too avoid duplicates.

    Each tag contains a list of field tuples
    (Subfields, ind1, ind2, value, field_position_global)
    where subfields is a list of (code, value).
    """
    new_rec = {}
    for tag, subfields in field_list:
        for subfields, ind1, ind2, value, field_position_global in subfields:
            record_add_field(new_rec,
                             tag,
                             ind1=ind1,
                             ind2=ind2,
                             controlfield_value=value,
                             subfields=subfields)
    if len(new_rec) > 0:
        record_add_field(new_rec,
                         tag='001',
                         controlfield_value=str(recid))
    return new_rec


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


def has_field_origin(field_list, origin, code):
    """
    This function checks if any of the fields for a certain tag contains
    origin in given subfield code. I.e. $9 arXiv.
    """
    for field in field_list:
        if origin in field_get_subfield_values(field, code):
            return True
    return False


def has_field(field, field_list):
    """
    This function checks if the given list of fields contains an field
    identical to passed field.
    """
    if len(field_list) > 0:
        for subfields, ind1, ind2, value, dummy in field_list:
            if (ind1, ind2, value) == field[1:4]:
                for sub in subfields:
                    if sub not in field[0]:
                        break
                else:
                    return True
    return False


def get_minimal_arxiv_id(record):
    """
    Returns the OAI arXiv id in the given record skipping the prefixes.
    I.e. oai:arxiv.org:1234.1234 becomes 1234.1234 and oai:arxiv.org:hep-ex/2134123
    becomes hep-ex/2134123. Used for searching.
    """
    values = record_get_field_values(record, tag="035", code="a")
    for value in values:
        if 'arXiv' in value:
            return value.split(':')[-1]


def record_get_value_with_provenence(record, tag, ind1=" ", ind2=" ", value_code="", provenence_code="9", provenence_value="arXiv"):
    """
    Retrieves the value of the field with given provenence.
    """
    fields = record_get_field_instances(record, tag, ind1, ind2)
    final_values = []
    for subfields, dummy1, dummy2, dummy3, dummy4 in fields:
        for code, value in subfields:
            if code == provenence_code and value == provenence_value:
                # We have a hit. Stop to look for right value
                break
        else:
            # No hits.. continue to next field
            continue
        for code, value in subfields:
            if code == value_code:
                # This is the value we are looking for with the correct provenence
                final_values.append(value)
    return final_values


def generate_ticket(record):
    """
    Will generate the ticket subject and body.
    Returns a tuple of strings: (subject, body)
    """
    arxiv_id = get_minimal_arxiv_id(record)
    pdfurl = "http://arxiv.org/pdf/%s" % (arxiv_id,)
    abstracturl = "http://arxiv.org/abs/%s" % (arxiv_id,)

    categories = record_get_value_with_provenence(record, "650", "1", "7", "a", provenence_code="2")
    comments = record_get_value_with_provenence(record, "500", value_code="a")
    authors = record_get_field_values(record, tag="100", code="a") + record_get_field_values(record, tag="700", code="a")

    subject = "ARXIV:" + arxiv_id
    text = \
"""
%(submitdate)s

ABSTRACT: %(abstracturl)s
PDF: %(pdfurl)s

Paper: %(arxiv_id)s

Title: %(title)s

Comments: %(comments)s

Authors: %(authors)s

Categories: %(categories)s
    
%(abstract)s

Try to find the record on INSPIRE: %(inspiresearchurl)s

""" \
    % {
        'submitdate': record_get_field_value(record, tag="269", code="c"),
        'pdfurl': pdfurl,
        'abstracturl': abstracturl,
        'arxiv_id': arxiv_id,
        'title': record_get_field_value(record, tag="245", code="a"),
        'comments': "; ".join(comments),
        'categories': " ".join(categories),
        'authors': " / ".join(authors[:10]),
        'abstract': record_get_field_value(record, tag="520", code="a"),
        'inspiresearchurl': "http://inspirehep.net/search?p=find%20eprint%20" + arxiv_id,
    }
    return subject, text.replace('%', '%%')


def main():
    usage = """
    name:           bibfilter_oaiarXiv2inspire
    decription:     Program to filter and analyse MARCXML records
                    harvested from external OAI sources, in order to determine
                    which action needs to be taken (insert, holdingpen, etc)
    usage:
                    bibfilter_oaiarXiv2inspire [-nhc:] MARCXML-FILE
    options:
                    source_id is the optional parameter indicating the
                    Invenio harvesting source identifier. This value is
                    used to produce logs allowing to trace the harvesting source

                -c CONFIG-FILE
                    path to configuration file. Defaults to CFG_ETCDIR + /bibharvest/oaiarXiv_bibfilter_actions.cfg
                -n
                    forces the script not to check if the record exists in the database
                    (useful when re-harvesting existing record)
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:nh", [])
    except getopt.GetoptError, err_obj:
        sys.stderr.write("Error:" + err_obj + "\n")
        print usage
        sys.exit(1)

    config_path = CFG_ETCDIR + "/bibharvest/" + "oaiarXiv_bibfilter_actions.cfg"
    skip_recid_check = False

    for opt, opt_value in opts:
        if opt in ['-c']:
            config_path = opt_value
        if opt in ['-n']:
            skip_recid_check = True
        if opt in ['-h']:
            print usage
            sys.exit(0)

    if len(args) != 1:
        sys.stderr.write("Error: Missing MARCXML to analyse")
        print usage
        sys.exit(1)

    input_filename = args[0]

    if not os.path.exists(input_filename):
        sys.stderr.write("Please enter a valid filename for input.")
        sys.exit(1)
    if not os.path.exists(config_path):
        sys.stderr.write("Please enter a valid filename for config.")
        sys.exit(1)

    # Read and wash incoming data
    file_data = open_marc_file(input_filename)
    washed_data = wash_for_xml(wash_for_utf8(file_data))

    # Transform MARCXML to record structure
    records = create_records(washed_data)
    action_dict = read_actions_configuration_file(config_path)
    insert_records = []
    append_records = []
    correct_records = []
    holdingpen_records = []

    for rec in records:
        record = rec[0]
        if record is None:
            sys.stderr.write("Record is None: %s" % (rec[2],))
            sys.exit(1)
        # Perform various checks to determine an suitable action to be taken for
        # that particular record. Whether it will be inserted, discarded or replacing
        # existing records
        #
        # Firstly, is the record already in the database?
        if skip_recid_check:
            recid = None
        else:
            recid = retrieve_rec_id(record, "")

        if not recid or recid == -1:
            # Try again with p_r_s
            arxiv_id = get_minimal_arxiv_id(record)
            if arxiv_id:
                results = perform_request_search(p="reportnumber:%s" % (arxiv_id,), of='id')
                if len(results) > 0:
                    # FIXME: Ambiguous results may happen. Now just taking first result..
                    recid = results[0]

        if not recid or recid == -1:
            # Record (probably) does not exist, flag for insert into database
            # FIXME: Add some automatic deny/accept parameters, perhaps also bibmatch call

            # New CORE records creates a ticket in RT
            if "CORE" in record_get_field_values(record, tag="980", code="a"):
                queue = "HEP_curation"
                subject, body = generate_ticket(record)
                create_ticket(queue, subject=subject, text=body)
            insert_records.append(record)
        else:
            # Record exists, fetch existing record
            existing_record = get_record(recid)
            if existing_record is None:
                # Did not find existing record in database
                holdingpen_records.append(record)
                continue

            # Now compare new version with existing one, returning a diff[tag] = (diffcode, [..])
            # None - if field is the same for both records
            # ('r',) - field missing from input record, ignored ATM
            # ('a',) - new field added, should be updated with append
            # ('c', difference_comparison) -> if field field_id exists in both records, but it's value has changed
            #                              -> uploaded with correct if accepted
            fields_to_add = []
            fields_to_correct = []
            holdingpen = False

            difference = record_diff(existing_record, record, compare_subfields=match_subfields)
            for tag, diff in difference.iteritems():
                if diff is None:
                    # No difference in tag
                    continue
                diff_code = diff[0]
                new_field_list = record_get_field_instances(record, tag, ind1="%", ind2="%")
                existing_field_list = record_get_field_instances(existing_record, tag, ind1="%", ind2="%")
                if tag == "245" and diff_code == "c":
                    # Special handling of field 245. We add title to 245 iff origin and original is arXiv
                    field = record_get_field_instances(record, tag, ind1="%", ind2="%")[0]
                    if has_field_origin(new_field_list, "arXiv", "9") and has_field_origin(existing_field_list, "arXiv", "9"):
                        fields_to_correct.append((tag, [field]))
                    else:
                        holdingpen = True
                    # Check for duplicates and add title update as 246
                    field_list_246 = record_get_field_instances(existing_record, "246", ind1="%", ind2="%")
                    if not has_field(field, field_list_246):
                        fields_to_add.append(("246", [field]))
                else:
                    corrected_fields = []
                    if has_field_origin(new_field_list, "arXiv", "9") \
                       and has_field_origin(existing_field_list, "arXiv", "9"):
                        for field in existing_field_list:
                            if not "arXiv" in field_get_subfield_values(field, "9"):
                                corrected_fields.append(field)
                        for field in new_field_list:
                            if not has_field(field, corrected_fields):
                                corrected_fields.append(field)

                    action = get_action(tag, diff_code, action_dict)
                    if action == 'holdingpen' and not holdingpen:
                        holdingpen = True

                    if action == 'correct' or len(corrected_fields) > 0:
                        if len(corrected_fields) == 0:
                            corrected_fields = new_field_list
                        fields_to_correct.append((tag, corrected_fields))

                    if action == 'append':
                        added_fields = record_get_field_instances(record, tag, ind1="%", ind2="%")
                        fields_to_add.append((tag, added_fields))

            # Lets add any extracted 'append' or 'correct' fields
            if len(fields_to_add) > 0:
                #Check if DOI is included in fields_to_add
                fields_without_DOI = []
                record_with_DOI = {}
                for tag, value in fields_to_add:
                    if tag == '024':
                        DOI_field = [(tag, value)]
                        #Create record just with DOI field
                        record_with_DOI = create_record_from_list(recid, DOI_field)
                    else:
                        fields_without_DOI.append((tag, value))
                # Append extra DOI record
                append_records.append(create_record_from_list(recid, fields_without_DOI))
                if record_with_DOI:
                    append_records.append(record_with_DOI)

            if len(fields_to_correct) > 0:
                correct_records.append(create_record_from_list(recid, fields_to_correct))
            if holdingpen:
                if "FFT" in record:
                    del record["FFT"]
                holdingpen_records.append(record)

    # Output results. Create new files, if necessary.
    write_record_to_file("%s.insert.xml" % (input_filename,), insert_records)
    sys.stdout.write("Number of records to insert:  %d\n" % (len(insert_records),))

    write_record_to_file("%s.append.xml" % (input_filename,), append_records)
    sys.stdout.write("Number of records to append fields: %d:\n" % (len(append_records),))

    write_record_to_file("%s.correct.xml" % (input_filename,), correct_records)
    sys.stdout.write("Number of records to correct fields: %d:\n" % (len(correct_records),))

    write_record_to_file("%s.holdingpen.xml" % (input_filename,), holdingpen_records)
    sys.stdout.write("Number of records to the holding pen: %d\n" % (len(holdingpen_records),))

    sys.exit(0)
if __name__ == '__main__':
    main()
