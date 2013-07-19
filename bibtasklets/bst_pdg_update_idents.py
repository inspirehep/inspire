#!/usr/bin/python
# -*- coding: utf-8 -*-
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2011 CERN.
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

"""
Inspire PDG Update Identifiers
"""

import sys
import os
import getopt
import datetime
import argparse
import re

from copy import deepcopy

from invenio.search_engine import (perform_request_search,
                                   get_record)
from invenio.search_engine_utils import get_fieldvalues
from invenio.bibrecord import (record_get_field_instances,
                               field_get_subfield_values,
                               record_add_field,
                               record_xml_output,
                               record_add_subfield_into,
                               record_delete_field)
from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibtask import write_message


MESSAGE_DESCRIPTION = """Updates the PDG identifiers for records included in
The Review of Particle Physics (http://pdg.lbl.gov/)"""
MESSAGE_COPYRIGHT = "Part of Inspire (http://www.inspirehep.net) - Copyright (C) 2013 CERN."
SEARCH_TERM = "084:pdg"
OUTPUT_PREFIX = "PDG-update_"


class ParseResult:
    """ Pseudo-enum type for line parsing:
         * Success - Found recid of record
         * Missing - No recid found
         * Ambiguous - Multiple records found
         * Invalid - Couldn't parse line """
    Success, Missing, Ambiguous, Invalid = range(4)


def _print_out(line):
    write_message("bst_pdg_update_idents: " + line)


def _print_verbose(line):
    write_message("* " + line, verbose=3)


def get_lines_from_file(input_file):
    """ given the path to a file, this function will
    return all lines in the file as a list """
    try:
        f = open(input_file)
    except IOError:
        _print_out("Error: Could not open " + input_file + " for reading.")
        sys.exit(2)

    _print_out("Reading from file " + input_file)
    lines = []
    count = 0
    for line in f:
        if not line.startswith('#'):
            lines.append(line.strip())

    _print_out(str(len(lines)) + " lines parsed from file")

    return lines


def write_list_to_file(output_dir, name, list_to_write):
    now = datetime.datetime.now()
    str_now = now.strftime("%Y-%m-%d_%H-%M-%S_")
    path = output_dir + OUTPUT_PREFIX + str_now + name
    try:
        handle = open(path, "w")
        for line in list_to_write:
            handle.write(str(line) + "\n")
        handle.close()
    except IOError:
        _print_out("Error: Could not write to file: " + path)

    _print_out("-> " + str(len(list_to_write))+" lines written to " + path)


def write_records_to_file(output_dir, name, records, dry_run):
    """
    Writes a new MARCXML file to specified path from a list of records.
    """
    if len(records) > 0:
        out = []
        out.append("<collection>")
        for record in records.itervalues():
            if record != {}:
                out.extend(record_xml_output(record).split('\n'))
        out.append("</collection>")
        if dry_run:
            _print_out("DRY: Ready to write " + str(len(records)) + " entries to file.")
        else:
            _print_out("-> Writing " + str(len(records)) + " entries to file...")
            write_list_to_file(output_dir, name, out)


def parse_pdg_line(line):
    """Given a line (string) from the PDG update file, this
    function will attempt to find the recid of the matching
    record and return it with the parsed PDG data.

    Params: string line - the line to be parsed
    Return: ParseResult - Status code
            string recid - record ID
            list pdg_values - pdg_values
    """
    recid = None
    pdg_values = None
    values = line.rsplit(',')
    if len(values) < 3:
        return ParseResult.Invalid, None, None

    search_terms = []
    if values[1] is '' and values[2] is '':
        search_terms.append("irn " + str(values[0]))
    else:
        search_terms.append("j " + values[0] + "," + values[1] + "," + values[2])
        vol = values[1][-1] + values[:-1]
        search_terms.append("j " + values[0] + "," + vol + "," + values[2])

    if not search_terms:
        return ParseResult.Invalid, None, None

    result = None
    for term in search_terms:
        result = perform_request_search(p=term)
        if len(result) > 1:
            return ParseResult.Ambiguous, None, None
        elif len(result) is 0:
            continue
        else:
            # len(result) == 1 hence record found succesfully
            recid = result[0]
            pdg_values = values[3:]
            return ParseResult.Success, recid, pdg_values

    return ParseResult.Missing, None, None


def is_pdg_field(field):
    if field_get_subfield_values(field, '2')[0] == 'PDG':
        if field_get_subfield_values(field, '9')[0] == 'PDG':
            return True
    return False


def create_new_pdg_fields(recids, pdg_data):
    _print_out("Creating new PDG fields for " + str(len(recids)) + " records...")
    records = {}
    for recid in recids:
        records[recid] = {}
        record_add_field(records[recid], '001',  controlfield_value=str(recid))
        pdg_fields = pdg_data[recid]
        for field in pdg_fields:
            position = record_add_field(records[recid], '084', ' ', ' ')
            record_add_subfield_into(records[recid], '084', '2', 'PDG', field_position_global=position)
            record_add_subfield_into(records[recid], '084', '9', 'PDG', field_position_global=position)
            record_add_subfield_into(records[recid], '084', 'a', field, field_position_global=position)
    return records


def remove_pdg_fields(recids, current_records):
    _print_out("Removing PDG data from " + str(len(recids)) + " records...")
    records = {}
    for recid in recids:
        record_mod = deepcopy(current_records[recid])
        fields = record_get_field_instances(record_mod, '084')
        count = 0
        for field in fields:
            count = count + 1
            if is_pdg_field(field):
                record_delete_field(record_mod, '084', ind1=' ', ind2=' ',
                                    field_position_global=field[4])

        _print_verbose(str(count) + " of " + str(len(fields)) +
                       " fields to be removed from record #" + str(recid))

        records[recid] = record_mod
    return records


def check_existing_pdg_fields(recids, pdg_data, current_records):
    _print_out("Comparing new and old PDG data for " + str(len(recids)) + " records...")
    records = {}
    for recid in recids:
        record_mod = {}
        record_mod['001'] = deepcopy(current_records[recid]['001'])
        record_mod['084'] = deepcopy(current_records[recid]['084'])
        fields = record_get_field_instances(record_mod, '084')
        current_pdg_data = []
        for field in fields:
            if is_pdg_field(field):
                current_pdg_data.append(field_get_subfield_values(field, 'a')[0])

        current_set = set(current_pdg_data)
        new_set = set(pdg_data[recid])
        deletions = list(current_set - new_set)
        additions = list(new_set - current_set)

        if len(deletions) > 0 or len(additions) > 0:
            if len(deletions) > 0:
                for field in fields:
                    if is_pdg_field(field):
                        if field_get_subfield_values(field, 'a')[0] in deletions:
                            record_delete_field(record_mod, '084', ind1=' ', ind2=' ',
                                                field_position_global=field[4])

            for pdg_field in additions:
                position = record_add_field(record_mod, '084', ' ', ' ')
                record_add_subfield_into(record_mod, '084', '2', 'PDG', field_position_global=position)
                record_add_subfield_into(record_mod, '084', '9', 'PDG', field_position_global=position)
                record_add_subfield_into(record_mod, '084', 'a', pdg_field, field_position_global=position)

            records[recid] = record_mod
            _print_verbose("Record #" + str(recid) + ": " + str(len(deletions)) +
                           " deletions and " + str(len(additions)) + " additons.")
        else:
            _print_verbose("Nothing to change for record #" + str(recid))

    _print_out(str(len(records)) + " records to be corrected.")
    return records


def parse_arguments():
    # Not with the wife
    input_file = ''
    dry_run = False

    parser = argparse.ArgumentParser(description=MESSAGE_DESCRIPTION,
                                     epilog=MESSAGE_COPYRIGHT)
    parser.add_argument("input_file", help="Location of the text file containing updated PDG information")
    parser.add_argument("output_dir", help="Directory to store operation results in.", default=CFG_TMPSHAREDDIR)
    parser.add_argument("-d", "--dry-run", help="Outputs changes without modifying records in the database.", action='store_true')
    parser.add_argument("-v", "--verbose", help="Verbose output (for debugging)", action='store_true')
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        _print_out("Error: Not a valid file: " + args.input_file)
        sys.exit(2)

    if not os.path.isdir(args.output_dir):
        _print_out("Error: Not a valid directory: " + args.output_dir)
        sys.exit(2)
    elif not os.access(args.output_dir, os.W_OK):
        _print_out("Error: Cannot write to directory: " + args.output_dir)
        sys.exit(2)

    if args.output_dir[-1] is '/':
        out_dir = args.output_dir
    else:
        out_dir = args.output_dir + '/'

    return args.input_file, args.dry_run, out_dir


def main(input_file, dry_run, output_dir):
    # Ensure we have data to update first
    _print_out("--------------- Fetching current data ---------------")
    current_record_ids = perform_request_search(p=SEARCH_TERM)
    _print_out(str(len(current_record_ids)) + " records found matching search term \"" + SEARCH_TERM + "\"")
    _print_verbose("Record IDs found: " + str(current_record_ids))

    current_records = {}  # Struct {'recid': (record)}
    bad_record_ids = []
    # We don't need the records for new PDG data, they are appended
    for recid in current_record_ids:
        record = get_record(recid)
        if '084' not in record:
            bad_record_ids.append(str(recid))
            _print_out("WARNING: No 084 in fetched record %s" % (str(recid),))
        else:
            current_records[recid] = record

    if len(bad_record_ids) > 0:
        _print_out("WARNING: Bad record IDs found! Printing to file")
        write_list_to_file(output_dir, "bad_record_ids", bad_record_ids)

    new_lines = get_lines_from_file(input_file)
    new_pdg_data = {}  # Struct {'recid': [pdg_data]}
    lines_missing = []
    lines_ambiguous = []
    lines_invalid = []
    _print_out("Finding records from input file")
    for i, line in enumerate(new_lines):
        status, r_id, data = parse_pdg_line(line)
        if status is ParseResult.Success:
            new_pdg_data[r_id] = data
            _print_verbose("line #"+str(i)+": Success! Record ID " + str(r_id) + " found for line " + line)
        elif status is ParseResult.Invalid:
            lines_invalid.append(line)
            _print_verbose("line #"+str(i)+": Invalid line: "+line)
        elif status is ParseResult.Missing:
            lines_missing.append(line)
            _print_verbose("line #"+str(i)+": Missing line: "+line)
        elif status is ParseResult.Ambiguous:
            lines_ambiguous.append(line)
            _print_verbose("line #"+str(i)+": Ambiguous line: "+line)

    # Results
    _print_out("--------------- Input Parsing ---------------")
    _print_out("Records matched to PDG data (valid): "+str(len(new_pdg_data)))
    _print_out("Missing records (not found): "+str(len(lines_missing)))
    _print_out("Ambiguous (multiple results): "+str(len(lines_ambiguous)))
    _print_out("Invalid lines (Dodgy data): "+str(len(lines_invalid)))

    if len(lines_missing) is not 0:
        write_list_to_file(output_dir, "missing-records.txt", lines_missing)
    if len(lines_ambiguous) is not 0:
        write_list_to_file(output_dir, "ambiguous-records.txt", lines_ambiguous)
    if len(lines_invalid) is not 0:
        write_list_to_file(output_dir, "invalid-lines.txt", lines_invalid)

    # These lists contain record IDs of records to have PDG data either:
    #  - add, the PDG data should be appended (record was added to PDG)
    #  - compare, the PDG data should be compared for possible correction
    #  - delete, the PDG data should be removed (record was removed from PDG)
    ids_add = list(set(new_pdg_data.keys()) - set(current_record_ids))
    ids_compare = list(set(current_record_ids) & set(new_pdg_data.keys()))
    ids_delete = list(set(current_record_ids) - set(new_pdg_data.keys()))
    # At this point all rec IDs should be valid!

    _print_out("--------------- Update ---------------")

    appends, updates, deletions = None, None, None

    # Now, cycle through the lists
    if len(ids_add) > 0:
        appends = create_new_pdg_fields(ids_add, new_pdg_data)
    else:
        _print_out("No new fields to append.")
    if len(ids_compare) > 0:
        updates = check_existing_pdg_fields(ids_compare, new_pdg_data, current_records)
    else:
        _print_out("No duplicate records to compare.")
    if len(ids_delete) > 0:
        deletions = remove_pdg_fields(ids_delete, current_records)
    else:
        _print_out("No fields in records to be deleted.")

    _print_out("--------------- Writing Changes ---------------")
    if appends is not None:
        write_records_to_file(output_dir, "append.xml", appends, dry_run)
    else:
        _print_out("No records to append.")

    if updates is not None:
        write_records_to_file(output_dir, "correct.xml", updates, dry_run)
    else:
        _print_out("No records to correct.")

    if deletions is not None:
        write_records_to_file(output_dir, "replace.xml", deletions, dry_run)
    else:
        _print_out("No records to replace.")


def bst_pdg_update_idents(input_file, dry=False, outdir=CFG_TMPSHAREDDIR):
    """usage: bst_pdg_update_idents.py [-h] [-d] [-v] input_file

    Updates the PDG identifiers for records included in The Review of Particle
    Physics (http://pdg.lbl.gov/)

    positional arguments:
      input_file     Location of the text file containing updated PDG information

    optional arguments:
      -h, --help     show this help message and exit
      -d, --dry-run  Outputs changes without modifying records in the database.
      -v, --verbose  Verbose output (for debugging)

    Part of Inspire (http://www.inspirehep.net) - Copyright (C) 2013 CERN.
    """
    main(input_file, dry, outdir)

if __name__ == '__main__':
    f_in, dry, outdir = parse_arguments()
    main(f_in, dry, outdir)
