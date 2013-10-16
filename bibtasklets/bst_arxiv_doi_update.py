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
Inspire arXiv DOI update script
"""

import urllib
import datetime

from invenio.bibtaskutils import ChunkedBibUpload, ChunkedBibIndex
from invenio.docextract_record import get_record, BibRecord
from invenio.search_engine import perform_request_search
from invenio.config import (CFG_TMPSHAREDDIR,
                            CFG_SITE_ADMIN_EMAIL)
from invenio.bibtask import (write_message,
                             task_update_status,
                             task_update_progress)
from invenio.mailutils import send_email

# NB: For future reference, elementtree.ElementTree is depreciated after
# Python 2.4, Inspire instances on higher Python versions should use xml.etree
# instead. The root.getiterator() function should also be updated.
try:
    import elementtree.ElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    from invenio.config import CFG_ASANA_API_KEY
except ImportError:
    CFG_ASANA_API_KEY = None

MESSAGES = []
ERRORS = []
SCRIPT_NAME = "bst_arxiv_doi_update"
URI_DEFAULT = "https://vendor.ridge.aps.org/arXiv/latest_pub.xml"
ASANA_PARENT_TASK_ID = 8115229241606


class DOIError(Exception):
    """ Exception to be raised for incorrect DOIs """
    pass

# ======================== MAIN =======================


def bst_arxiv_doi_update(input_uri=None, log_dir=CFG_TMPSHAREDDIR, logging=True,
                         asana_key=CFG_ASANA_API_KEY,
                         asana_parent_id=ASANA_PARENT_TASK_ID):
    """
    bst_arxiv_doi_update
    Updates DOIs on documents harvested from ArXiv.

    Parameters:
        * input_uri - Link to new URI data
            DEFAULT: https://vendor.ridge.aps.org/arXiv/latest_pub.xml
            NOTE: Test data can be taken from http://arxiv.org/schemas/doi_feed_test.xml
        * log_dir - Directory to store log files in
        * logging - True or False, default True
        * asana_key - The Asana API, by default uses the value of CFG_ASANA_API_KEY
            NOTE: Passing the value of None for this parameter will skip writing
            to Asana and instead email the instance admin
        * asana_parent_id - The task in Asana to log subtasks to
    """
    if input_uri is None:
        _print("Notice: No URI specified, defaulting to " + URI_DEFAULT)
        input_uri = URI_DEFAULT

    task_update_progress("Resolving URI...")

    # Testing builds characters
    bibupload = ChunkedBibUpload(mode='a', user=SCRIPT_NAME, notimechange=True)
    bibindex = ChunkedBibIndex(indexes='year,global,journal',
                               user=SCRIPT_NAME)
    # open url and parse xml
    try:
        tree = ET.parse(urllib.urlopen(input_uri))
        _print('Opened DOI file ' + input_uri)
    except IOError:
        _print("FATAL ERROR: Could not open URL: " + input_uri, 1)
        task_update_progress("Failed retreiving DOI data")
        task_update_status("FAILED")
        return False
    root = tree.getroot()

    try:
        date_el = root.find('date')
        date_str = '%s-%s-%s' % (date_el.get('year'), date_el.get('month'),
                                 date_el.get('day'))
        _print("Processing DOIs last updated on date %s" % date_str)
    except AttributeError:
        _print("Warning: Couldn't get last published date of Arxiv DOI feed.")

    doi_count = 0
    new_count = 0

    # Stores any DOIs with have issues with in structure:
    # Missing: (doi, arxiv preprint_id, published date)
    # Ambiguous: (doi, arxiv preprint_id, rec_ids)
    # Incorrect: (rec_id, old-doi, new-doi)
    problem_dois = {'missing': [], 'ambiguous': [], 'incorrect': []}

    task_update_progress("Processing records...")
    # NB: Element.getiterator() is deprecated since version 2.7: Use
    # method Element.iter() instead.
    for item in root.getiterator('article'):
        doi_count += 1
        doi = item.get('doi')
        arxiv = item.get('preprint_id')
        published_date = item.get('published')
        _print("XML entry #%s: %s" % (str(doi_count), arxiv), 6)
        rec_id = get_record_by_arxiv_id(arxiv)
        if len(rec_id) == 1:
            rec_id = rec_id[0]
            try:
                record_xml = append_to_record(rec_id, doi, published_date)
            except DOIError as ex:
                problem_dois['incorrect'].append((rec_id, ex.message, doi))
                continue
            if record_xml:
                new_count += 1
                _print("* Now we will run the bibupload and bibindex for " +
                       "%s record" % rec_id, 5)
                _print("** We will upload the following xml code %s" %
                       repr(record_xml), 9)
                bibupload.add(record_xml)
                bibindex.add(rec_id)
        elif len(rec_id) > 1:
            _print('ERROR: %d records found with matching arXiv ID %s' %
                   (len(rec_id), arxiv))
            problem_dois['ambiguous'].append((doi, arxiv, repr(rec_id)))
        else:
            _print('No record found matching arxiv ID: %s' % arxiv, 9)
            problem_dois['missing'].append((doi, arxiv, published_date))

    _print("========================| FINAL SCORE |========================", 1)
    _print("DOIs found and processed: %d" % doi_count, 1)
    _print("Arxiv IDs without corresponding records: %d"
           % len(problem_dois['missing']), 1)
    _print("Arxiv IDs corresponding to multiple records (duplicates): %d"
           % len(problem_dois['ambiguous']), 1)
    _print("Inspire records with an incorrect DOI: %d"
           % len(problem_dois['incorrect']), 1)
    _print("Records without DOIs requiring appends: %d" % new_count, 1)

    if logging:
        task_update_progress("Logging...")
        write_list_to_file(log_dir, 'errors', ERRORS)
        write_list_to_file(log_dir, 'messages', MESSAGES)

    notify_on_errors(problem_dois, log_dir, doi_count, new_count,
                     asana_key, asana_parent_id)

    task_update_progress(SCRIPT_NAME + " finished. %s DOIs processed, %s to add"
                         % (str(doi_count), str(new_count)))
    task_update_status("DONE")

    bibupload.__del__()
    bibindex.__del__()

    return True

# ======================== FUNCTIONS =======================


def _print(string, verbose=3):
    """ Writes message to log and bibsched log """
    MESSAGES.append(string)
    msg = "bst_arxiv_doi_update: " + string
    write_message(msg, None, verbose)


def write_list_to_file(output_dir, name, list_to_write):
    """ Takes a list of strings and writes them to a file """
    if list_to_write:
        if name == 'errors':
            _print('ERRORS OCCURRED DURING DOI UPDATE!', 1)
        now = datetime.datetime.now()
        str_now = now.strftime("_%Y-%m-%d_%H-%M_")
        path = output_dir + '/' + SCRIPT_NAME + str_now + name + '.log.txt'
        try:
            handle = open(path, "w")
            for line in list_to_write:
                handle.write(str(line) + "\n")
            handle.close()
        except IOError:
            _print("Error: Could not write to file: " + path)

        _print("-> " + str(len(list_to_write))+" lines written to " + path)
    else:
        _print("Nothing to write to file " + name)


def is_marked_published(record):
    """ Finds 'Published' in field 980__a for
    a given record """
    fields = record.find_subfields('980__a')
    for field in fields:
        if field.value == 'Published':
            return True
    return False


def append_to_record(rec_id, doi, published_date):
    """ Attempts to add a DOI to a record, also
    adds 930 'Published' if not already there and
    adds the extrapolated PubNote data to 773 """
    record = get_record(recid=rec_id)
    new_record = BibRecord(rec_id)
    # make sure that there is no DOI for this record
    if not record_has_doi(record, rec_id, doi):
        # create new record with only 0247 field, that we will append
        # to the existing record with bibupload function
        new_record = BibRecord(rec_id)
        new_field = new_record.add_field('0247_')
        new_field.add_subfield('2', 'DOI')
        new_field.add_subfield('a', doi.decode('utf-8'))

        _print('DOI to be added: ' + doi +
               ' to the record ' + str(rec_id), 3)

    if not is_marked_published(record):
        new_field_980 = new_record.add_field('980__')
        new_field_980.add_subfield('a', 'Published')

    append_773 = False
    field_773 = record.find_fields('773__')
    new_field_773 = create_pubnote(doi, published_date)
    if len(field_773) == 0:
        append_773 = True
        _print("No pubnote, adding field 773 to record...", 7)
    else:
        if not is_pubnote_identical(field_773, new_field_773):
            append_773 = True
            _print("Field 773 already exists for record, " +
                   "differs from DOI extract", 3)
        else:
            _print("Field 773 already exists, does not " +
                   "contradict DOI extract.", 6)

    if append_773:
        new_field = new_record.add_field('773__')
        for code, value in new_field_773.iteritems():
            new_field.add_subfield(code, value)

    field_260 = record.find_subfields("260__c")

    if len(field_260) == 0:
        # We add 260__c publication date
        new_field = new_record.add_field('260__')
        new_field.add_subfield("c", published_date)

    if len(new_record.record) > 0:
        return new_record.to_xml()
    else:
        return None


def get_record_by_arxiv_id(arxiv):
    """ Retreives record corresponding to an arXiv ID, in the format
    arxiv:xxxx.xxxx - returns a list (hopefully with only one item) """
    # if arxiv doesn't contain "arXiv:" at the beginning, we add it
    if arxiv[:6] != 'arXiv:':
        arxiv = 'arXiv:' + arxiv
    return perform_request_search(p='037__a:' + arxiv)


def create_pubnote(doi, published_date):
    """ Creates pubnote field values from DOI.
    Returns a dictionary of 773 subfields """
    field_773 = {}
    try:
        # Example published date: 2013-08-09
        year = published_date.split('-')[0]
        # Note: this will need updating before the year 10,000
        if len(year) is not 4:
            msg = ("Error: Could not determine pubnote year from date " +
                   published_date + " for DOI " + doi)
            _print(msg)
            ERRORS.append(msg)
        else:
            field_773['y'] = year

    # Example DOI: 10.1103/PhysRevD.88.034502
        doi_part = doi.split('/')[1]
        segments = doi_part.split('.')
        if (len(segments[0]) is 8 and segments[0][:7] == 'PhysRev'
                and segments[0][-1:].isupper()):
            # If PhysRevX then X suffixes journal num
            field_773['p'] = add_dots(segments[0][:-1])
            field_773['v'] = segments[0][-1:] + segments[1]
        else:
            field_773['p'] = add_dots(segments[0])
            field_773['v'] = segments[1]

        field_773['c'] = segments[2]

        return field_773
    except IndexError:
        _print("Error: Could not determine pubnote from DOI " + doi, 2)
    return None


def is_pubnote_identical(fields_773, new_data):
    """ Compares the current field to
    the data infered from the DOI.
    Returns True if a matching field is found"""
    for field in fields_773:
        remainder = list(new_data.keys())
        for sub in field.subfields:
            if sub.code in new_data:
                if new_data[sub.code] == sub.value:
                    try:
                        remainder.remove(sub.code)
                    except ValueError:
                        # Two subfields with the same code
                        continue

        if len(remainder) == 0:
            return True
    return False


def record_has_doi(record, rec_id, doi):
    """ Tests a given record for DOI, returns True if the record has
    a DOI that matches the one sourced from the DOI feed """
    fields = record.find_fields('0247_')
    for field in fields:
        try:
            if 'DOI' in field.get_subfield_values('2'):
                _print('Record %s already has a doi' % str(rec_id), 6)
                sub_a = field.get_subfield_values('a')
                if len(sub_a) != 1:
                    msg = ('Warning: Multiple DOIs (024 7_ $a) found for ' +
                           'record %d' % rec_id)
                    ERRORS.append(msg)
                    _print(msg)

                if doi in sub_a:
                    _print('DOI for %s matches current DOI' % str(rec_id), 7)
                    return True
                else:
                    msg = ('ERROR: DOI of record #%d (%s)' % (rec_id, sub_a[0])
                           + 'is different than the new doi (%s)!' % doi)
                    ERRORS.append(msg)
                    _print(msg, 2)
                    raise DOIError(repr(sub_a))
        except IndexError:
            pass
    _print('No current DOI found for record #%d' % rec_id, 6)
    return False


def add_dots(string):
    """ Adds dots to journals """
    out = string[0]
    for index in range(1, len(string)):
        char = string[index]
        if char.isupper():
            if not string[index - 1] == '.':
                out += '.'
        out += char
    if string[-1:] != '.':
        out += '.'
    return out


def notify_on_errors(dois, log_dir, count_total, count_new, asana_key,
                     asana_parent_task_id):
    """ If the dictionary dois is empty, this function does nothing.
    Else it will attempt to write information about DOI errors to either
    Asana or, failing that, emailing the admin.
    Parameters:
     * dois - dictionary: 3-part dictionary, with a list of DOIs with errors.
     * log_dor - string: The local directory where logs are stored.
     * count_total - int: How many DOIs this script has updated.
     * count_new - int: How many DOIs have been inserted into Inspire.
     * asana_key - string: The API Key of the user account being used.
     * asana_parent_task_id -  int: ID of the parent task in Asana for this
                                    information to be appended to. """
    if (len(dois['missing']) == 0 and len(dois['ambiguous']) == 0 and
            len(dois['incorrect']) == 0):
        return

    mail = False
    if asana_key:
        try:
            from asana.asana import AsanaAPI, AsanaException
            try:
                asana_instance = AsanaAPI(asana_key)
                send_asana_tasks(dois, log_dir, count_total, count_new,
                                 asana_instance, asana_parent_task_id)
            except AsanaException as ex:
                _print("Error occured during Asana update, sending email " +
                       "instead.")
                _print(ex.message)
                mail = True
        except ImportError as ex:
            mail = True
            _print("Warning: Could not import Asana API, sending email" +
                   " instead.", 1)
    else:
        mail = True

    if mail:
        send_notification_email(dois, log_dir, count_total, count_new)


def send_notification_email(dois, log_dir, count_total, count_new):
    """ If any issues occured during the DOI update, this function
    notifies the appropriate authorities with details of the error
    Parameters:
     * dois - a dictionary with three categories of problem DOIs
     * log_dir - the directory where the logs are stored """
    msg_html = """<p>Message from BibTasklet %s:</p>

<p>Problems have occurred while updating the DOIs of records. In total %d DOIs were
processed, of which %d were processed succesfully.</p>

<p>Further details on these errors can be found in the log files, they should be
available here: '%s'</p>
""" % (SCRIPT_NAME, count_total, count_new, log_dir)

    if len(dois['missing']) > 0:
        msg_html += """
<h3>No records could be found to match the following arXiv tags:</h3>
<table>
    <tr>
        <td><p><strong>DOI</strong></p></td>
        <td><p><strong>ArXiv PrePrint ID</strong></p></td>
        <td><p><strong>Date of Publishing</strong></p></td>
    </tr>
"""
        for doi, arxiv, date in dois['missing']:
            msg_html += """<tr>
                        <td><p>%s</p></td>
                        <td><p>%s</p></td>
                        <td><p>%s</p></td>
                      </tr>""" % (doi, arxiv, date)
        msg_html += "</table>"

    if len(dois['ambiguous']) > 0:
        msg_html += """
<h3>Multiple records were found for the following arXiv tags:</h3>
<table>
    <tr>
        <td><p><strong>DOI</strong></p></td>
        <td><p><strong>ArXiv PrePrint ID</strong></p></td>
        <td><p><strong>RecIDs found</strong></p></td>
    </tr>
"""
        for doi, arxiv, rec_ids in dois['ambiguous']:
            msg_html += """<tr>
                        <td><p>%s</p></td>
                        <td><p>%s</p></td>
                        <td><p>%s</p></td>
                      </tr>""" % (doi, arxiv, rec_ids)
        msg_html += "</table>"

    if len(dois['incorrect']) > 0:
        msg_html += """
<h3>Records found by arXiv tags, but had a different DOI:</h3>
<table>
    <tr>
        <td><p><strong>Record ID</strong></p></td>
        <td><p><strong>Current DOI</strong></p></td>
        <td><p><strong>New DOI</strong></p></td>
    </tr>
"""

        for r_id, old_doi, new_doi in dois['incorrect']:
            msg_html += """<tr>
                        <td><p>%s</p></td>
                        <td><p>%s</p></td>
                        <td><p>%s</p></td>
                      </tr>""" % (r_id, old_doi, new_doi)
        msg_html += "</table>"

    send_email(CFG_SITE_ADMIN_EMAIL, CFG_SITE_ADMIN_EMAIL,
               "Errors during ArXiv DOI Update", html_content=msg_html)


def send_asana_tasks(dois, log_dir, count_total, count_new, asana, parent):
    """ If any issues occured during the DOI update, this function
    logs the faulty DOIs to Asana
    Parameters:
     * dois - a dictionary with three categories of problem DOIs
     * log_dir - the directory where the logs are stored """

    date_str = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M")
    msg = """Message from BibTasklet %s:

Problems have occurred while updating the DOIs of records. In total %d DOIs were
processed, of which %d were processed succesfully.

Further details on these errors can be found in the log files, they should be
available in the following directory: '%s'
""" % (SCRIPT_NAME, count_total, count_new, log_dir)

    # Create the subtasks
    parent_task = asana.create_subtask(parent,
                                       "DOI Update on %s" % date_str,
                                       notes=msg)
    par_id = parent_task['id']

    categories = [
        ('missing', 'Missing Records',
         "No records could be found to match the following arXiv tags.",
         "DOI, ArXiv PrePrint ID, Date of Publishing"),
        ('ambiguous', 'Ambigous Records (duplicates)',
         "Multiple records were found for the following arXiv tags.",
         "DOI, ArXiv PrePrint ID, Inspire Record IDs"),
        ('incorrect', 'Incorrect DOIs',
         "Records found by arXiv tags, but had a different DOI.",
         "Record ID, DOI from Inspire, DOI from APS")]

    for dic, title, desc, structure in categories:
        if len(dois[dic]) > 0:
            msg = "%s\n\nLine Structure: %s" % (desc, structure)
            _parent = asana.create_subtask(par_id, title, notes=msg)
            for prt1, prt2, prt3 in dois[dic]:
                asana.create_subtask(_parent['id'],
                                     "%s | %s | %s" % (prt1, prt2, prt3))
