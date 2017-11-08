# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""BibFormat element - Enhanced INSPIRE MARCXML"""
from zlib import decompress

from invenio.intbitset import intbitset
from invenio.bibrecord import record_xml_output, record_get_field_instances, field_get_subfield_instances, record_add_field, create_record
from invenio.search_engine import perform_request_search
from invenio.bibrank_citation_indexer import get_tags_config as _get_tags_config, get_recids_matching_query
from invenio.refextract_linker import find_doi, find_journal, find_reportnumber, find_book, find_isbn
from invenio.dbquery import run_sql
from invenio.access_control_engine import acc_authorize_action
from invenio.config import CFG_BIBFORMAT_HIDDEN_TAGS
from invenio.bibdocfile import BibRecDocs

INSTITUTION_CACHE = {}
def get_institution_ids(text):
    # HACK: I know... I am sorry for that. It's for a good cause
    # FIXME: use redis
    global INSTITUTION_CACHE
    if text not in INSTITUTION_CACHE:
        INSTITUTION_CACHE[text] = intbitset(perform_request_search(cc='Institutions', p='110__u:"%s"' % text)) or \
            intbitset(perform_request_search(cc='Institutions', p='110__t:"%s"' % text))
    return INSTITUTION_CACHE[text]

HEPNAME_CACHE = {}
def get_hepname_id(personid):
    global HEPNAME_CACHE
    if personid not in HEPNAME_CACHE:
        canonical_name = get_personid_canonical_id().get(personid)
        if canonical_name is None:
            HEPNAME_CACHE[personid] = None
        else:
            recids = perform_request_search(p='035__a:"%s"' % canonical_name, cc='HepNames')
            HEPNAME_CACHE[personid] = recids[0] if recids else None
    return HEPNAME_CACHE[personid]

INSPIRE_ID_CACHE = {}
def get_hepname_id_from_inspire_id(inspire_id):
    global INSPIRE_ID_CACHE
    if inspire_id not in INSPIRE_ID_CACHE:
        recids = perform_request_search(p='035__a:"%s"' % inspire_id, cc='HepNames')
        INSPIRE_ID_CACHE[inspire_id] = recids[0] if recids else None
    return INSPIRE_ID_CACHE[inspire_id]

CANONICAL_NAME_CACHE = {}
def get_personid_canonical_id():
    global CANONICAL_NAME_CACHE
    if not CANONICAL_NAME_CACHE:
        CANONICAL_NAME_CACHE = dict(run_sql("SELECT personid, data FROM aidPERSONIDDATA WHERE tag='canonical_name'"))
    return CANONICAL_NAME_CACHE

RELATED_JOURNAL_CACHE = {}
def get_related_journal(journal_name):
    global RELATED_JOURNAL_CACHE
    if journal_name not in RELATED_JOURNAL_CACHE:
        recids = perform_request_search(p='711__a:"%s"' % journal_name, cc='Journals')
        RELATED_JOURNAL_CACHE[journal_name] = recids[0] if recids else None
    return RELATED_JOURNAL_CACHE[journal_name]

def reference2citation_element(subfields):
    citation_element = {}
    for code, value in subfields:
        if code == 'a':
            citation_element['doi_string'] = value
        elif code == 't':
            citation_element['title'] = value
        elif code == 'i':
            citation_element['ISBN'] = value
        elif code == 'r':
            citation_element['report_num'] = value
        elif code == 'y':
            citation_element['year'] = value
        elif code == 's':
            try:
                citation_element['pubnote'] = value
                journal, volume, page = value.split(',')
                citation_element['journal_title'] = journal
                citation_element['volume'] = volume
                citation_element['page'] = page
            except ValueError:
                pass
    if 'journal_title' in citation_element:
        # HACK: to work around clash between find_journal() and find_book()
        citation_element['title'] = citation_element['journal_title']
    return citation_element


def get_matched_id(subfields):
    citation_element = reference2citation_element(subfields)
    if 'doi_string' in citation_element:
        recids = find_doi(citation_element)
        if len(recids) == 1:
            return recids.pop()
    if 'journal_title' in citation_element and 'year' in citation_element:
        recids = find_journal(citation_element)
        if len(recids) == 1:
            return recids.pop()
    if 'pubnote' in citation_element:
        recids = perform_request_search(p=citation_element['pubnote'], f='journal')
        if len(recids) == 1:
            return recids.pop()
    if 'report_num' in citation_element:
        recids = find_reportnumber(citation_element)
        if len(recids) == 1:
            return recids.pop()
    if 'ISBN' in citation_element:
        recids = find_isbn(citation_element)
        if len(recids) == 1:
            return recids.pop()
    #if 'title' in citation_element:
        #recids = find_book(citation_element)
        #if len(recids) == 1:
            #return recids.pop()
    return None


def salvage_deleted_record_from_history(recid):
    return create_record(decompress(run_sql("SELECT marcxml FROM hstRECORD WHERE id_bibrec=%s ORDER BY job_date DESC LIMIT 1", (recid, ))[0][0]))[0]


def is_record_deleted(bfo):
    return 'DELETED' in [value.upper() for value in bfo.fields('980__%')]


def format_element(bfo, oai=0):
    """Produce MARCXML with enhanced fields.

    Adds 100/700 $x with Record ID of linked HepName,
         701/702 $y with True/False if the signature is claimed
                 $z with Record ID of institution
                 $w with BAI of linked Profile
         371/110 $z with Record ID of institution
         119/502 $z with Record ID of institution
         999C5   $0 with on the fly discovered Record IDs (not for books)
         773     $0 with Record ID of corresponding Book or Proceeding or Report
                 $1 with Record ID of corresponding Journal
                 $2 with Record ID of corresponding Conference
         693/710 $0 with Record ID of corresponding experiment
    """
    can_see_hidden_stuff = not acc_authorize_action(bfo.user_info, 'runbibedit')[0]
    recid = bfo.recID
    if can_see_hidden_stuff and is_record_deleted(bfo):
        record = salvage_deleted_record_from_history(recid)
    else:
        record = bfo.get_record()

    # Let's filter hidden fields
    if can_see_hidden_stuff:
        # Let's add bibdoc info
        bibrecdocs = BibRecDocs(recid)
        for bibdocfile in bibrecdocs.list_latest_files():
            fft = [
                ('a', bibdocfile.fullpath),
                ('d', bibdocfile.description or ''),
                ('f', bibdocfile.format or ''),
                ('n', bibdocfile.name or ''),
                ('r', bibdocfile.status or ''),
                ('s', bibdocfile.cd.strftime('%Y-%m-%d %H:%M:%S')),
                ('t', bibdocfile.get_type()),
                ('v', str(bibdocfile.version)),
                ('z', bibdocfile.comment or ''),
            ]
            for flag in bibdocfile.flags:
                fft.append(('o', flag))
            record_add_field(record, 'FFT', subfields=fft)
    else:
        # not authorized
        for tag in CFG_BIBFORMAT_HIDDEN_TAGS:
            if tag in record:
                del record[tag]


    is_institution = 'INSTITUTION' in [collection.upper() for collection in bfo.fields('980__a')]

    signatures = {}
    if '100' in record or '700' in record:
        signatures = dict((name, (personid, flag)) for name, personid, flag in run_sql("SELECT name, personid, flag FROM aidPERSONIDPAPERS WHERE bibrec=%s AND flag>-2", (recid, )))

    # Let's add signatures
    for field in record_get_field_instances(record, '100') + record_get_field_instances(record, '700') + record_get_field_instances(record, '701') + record_get_field_instances(record, '702'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        if 'a' in subfield_dict:
            author_name = subfield_dict['a']
            if 'i' in subfield_dict:
                inspire_id = subfield_dict['i']
                hepname_id = get_hepname_id_from_inspire_id(inspire_id)
                if hepname_id:
                    subfields.append(('x', '%i' % hepname_id))
                    subfields.append(('y', '1'))
            else:
                personid, flag = signatures.get(author_name, (None, None))
                bai = get_personid_canonical_id().get(personid)
                if bai:
                    subfields.append(('w', bai))
                    hepname_id = get_hepname_id(personid)
                    if hepname_id:
                        subfields.append(('x', '%i' % hepname_id))
                    subfields.append(('y', '%i' % (flag == 2)))

        # And matched affiliations
        if 'u' in subfield_dict:
            for code, value in subfields:
                if code == 'u':
                    ids = get_institution_ids(value)
                    if len(ids) == 1:
                        subfields.append(('z', '%i' % ids[0]))

    # Thesis institution
    for field in record_get_field_instances(record, '502'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        if 'c' in subfield_dict:
            for code, value in subfields:
                if code == 'c':
                    ids = get_institution_ids(value)
                    if len(ids) == 1:
                        subfields.append(('z', '%i' % ids[0]))

    # Related institution
    for field in record_get_field_instances(record, '510'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        if 'a' in subfield_dict and not '0'in subfield_dict:
            ids = get_institution_ids(subfield_dict['a'])
            if len(ids) == 1:
                subfields.append(('0', '%i' % ids[0]))

    # Related journal
    for field in record_get_field_instances(record, '530'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        if 'a' in subfield_dict and not '0'in subfield_dict:
            ids = get_institution_ids(subfield_dict['a'])
            if len(ids) == 1:
                subfields.append(('0', '%i' % ids[0]))

    # Enhance affiliation in Experiments
    for field in record_get_field_instances(record, '119'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        if 'u' in subfield_dict:
            for code, value in subfields:
                if code == 'u':
                    ids = get_institution_ids(value)
                    if len(ids) == 1:
                        subfields.append(('z', '%i' % ids[0]))

    # Enhance affiliation in HepNames and Jobs and Institutions and
    # naked affiliations in HEP
    for field in record_get_field_instances(record, '371') + record_get_field_instances(record, '902'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        if 'a' in subfield_dict:
            for code, value in subfields:
                if code == 'a':
                    ids = get_institution_ids(value)
                    if len(ids) == 1:
                        subfields.append(('z', '%i' % ids[0]))

    for field in record_get_field_instances(record, '110'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        if is_institution:
            # We try to resolve obsolete ICNs
            if 'x' in subfield_dict:
                for code, value in subfields:
                    if code == 'x':
                        ids = get_institution_ids(value)
                        if len(ids) == 1:
                            subfields.append(('z', '%i' % ids[0]))
        else:
            # In other collections institution is in a
            if 'a' in subfield_dict:
                for code, value in subfields:
                    if code == 'a':
                        ids = get_institution_ids(value)
                        if len(ids) == 1:
                            subfields.append(('z', '%i' % ids[0]))

    # Enhance citation
    for field in record_get_field_instances(record, '999', ind1='C', ind2='5'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        if '0' in subfield_dict:
            # Already available recid
            subfields.append(('z', '1'))
        else:
            matched_id = get_matched_id(subfields)
            if matched_id:
                subfields.append(('0', str(matched_id)))

    # Enhance related records
    for field in (record_get_field_instances(record, '780', ind1='0', ind2='2') +
                  record_get_field_instances(record, '785', ind1='0', ind2='2') +
                  record_get_field_instances(record, '787', ind1='0', ind2='8')):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        subfield_citation = []
        if subfield_dict.get('r'): # Reportnumber
            subfield_citation.append(('r', subfield_dict['r']))
        if subfield_dict.get('z'): # ISBN
            subfield_citation.append(('i', subfield_dict['z']))
        if 'w' not in subfield_dict and subfield_citation:
            matched_id = get_matched_id(subfield_citation)
            if matched_id:
                subfields.append(('w', str(matched_id)))

    # Enhance CNUMs and Journals
    for field in record_get_field_instances(record, '773'):
        subfields = field_get_subfield_instances(field)
        subfield_dict = dict(subfields)
        for code, value in subfields:
            if code == 'w':
                # Conference CNUMs
                recids = perform_request_search(p='111__g:"%s"' % value, cc='Conferences')
                if len(recids) == 1:
                    subfields.append(('2', str(recids.pop())))
                if '0' not in subfield_dict:
                    recids = perform_request_search(p='773__w:"%s" 980:PROCEEDINGS' % value)
                    if recid in recids:
                        # We remove this very record, since it can be a proceedings
                        recids.remove(recid)
                    if len(recids) == 1:
                        subfields.append(('0', str(recids.pop())))
            elif code == 'p':
                # Journal title
                recids = perform_request_search(p='711__a:"%s"' % value, cc='Journals')
                if len(recids) == 1:
                    subfields.append(('1', str(recids.pop())))
            elif code == 'z' and '0' not in subfield_dict:
                # ISBN
                recids = find_isbn({'ISBN': value})
                if len(recids) == 1:
                    subfields.append(('0', str(recids.pop())))
            elif code == 'r' and '0' not in subfield_dict:
                # Report
                recids = perform_request_search(p='reportnumber:"%s"' % value)
                if len(recids) == 1:
                    subfields.append(('0', str(recids.pop())))

    # Enhance Experiments
    for field in record_get_field_instances(record, '693'):
        subfields = field_get_subfield_instances(field)
        for code, value in subfields:
            if code == 'e':
                recids = perform_request_search(p='119__a:"%s"' % value, cc='Experiments')
                if len(recids) == 1:
                    subfields.append(('0', str(recids.pop())))
            elif code == 'a':
                recids = perform_request_search(p='119__b:"%s"' % value, cc='Experiments')
                if len(recids) == 1:
                    subfields.append(('0', str(recids.pop())))


    # Enhance Experiments
    for field in record_get_field_instances(record, '710'):
        subfields = field_get_subfield_instances(field)
        for code, value in subfields:
            if code == 'g':
                recids = perform_request_search(p='119__a:"%s"' % value, cc='Experiments')
                if len(recids) == 1:
                    subfields.append(('0', str(recids.pop())))

    # Add Creation date:
    if '961' in record:
        del record['961']
    creation_date, modification_date = run_sql("SELECT creation_date, modification_date FROM bibrec WHERE id=%s", (recid,))[0]
    record_add_field(record, '961', subfields=[('x', creation_date.strftime('%Y-%m-%d')), ('c', modification_date.strftime('%Y-%m-%d'))])

    formatted_record = record_xml_output(record)
    if oai:
        formatted_record = formatted_record.replace("<record>", "<marc:record xmlns:marc=\"http://www.loc.gov/MARC21/slim\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd\" type=\"Bibliographic\">\n     <marc:leader>00000coc  2200000uu 4500</marc:leader>")
        formatted_record = formatted_record.replace("<record xmlns=\"http://www.loc.gov/MARC21/slim\">", "<marc:record xmlns:marc=\"http://www.loc.gov/MARC21/slim\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd\" type=\"Bibliographic\">\n     <marc:leader>00000coc  2200000uu 4500</marc:leader>")
        formatted_record = formatted_record.replace("</record", "</marc:record")
        formatted_record = formatted_record.replace("<controlfield", "<marc:controlfield")
        formatted_record = formatted_record.replace("</controlfield", "</marc:controlfield")
        formatted_record = formatted_record.replace("<datafield", "<marc:datafield")
        formatted_record = formatted_record.replace("</datafield", "</marc:datafield")
        formatted_record = formatted_record.replace("<subfield", "<marc:subfield")
        formatted_record = formatted_record.replace("</subfield", "</marc:subfield")
    return formatted_record

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
