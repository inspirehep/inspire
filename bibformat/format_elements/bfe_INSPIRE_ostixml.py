# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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
BibFormat element - outputs special purpose OSTI xml
"""

def format_element(bfo):
    """
    Special contract with US DoE Office of Scientific and Technical Information
    29/08/2013 R.A.

    Serializes selected record info as "OSTI" xml
    """

    try:
        from lxml import etree
    except ImportError:
        return

    from invenio.search_engine import perform_request_search, \
        get_fieldvalues, record_exists

    # a dictionary of Inspire subjects mapped to OSTI coded research categories
    osticats = {
        'Accelerators': '43 PARTICLE ACCELERATORS',
        'Computing': '99 GENERAL AND MISCELLANEOUS//MATHEMATICS, COMPUTING, AND INFORMATION SCIENCE',
        'Experiment-HEP': '72 PHYSICS OF ELEMENTARY PARTICLES AND FIELDS',
        'General Physics': '71 CLASSICAL AND QUANTUM MECHANICS, GENERAL PHYSICS',
        'Instrumentation': '46 INSTRUMENTATION RELATED TO NUCLEAR SCIENCE AND TECHNOLOGY',
        'Astrophysics': '71 CLASSICAL AND QUANTUM MECHANICS, GENERAL PHYSICS',
        'Lattice': '72 PHYSICS OF ELEMENTARY PARTICLES AND FIELDS',
        'Math and Math Physics': '72 PHYSICS OF ELEMENTARY PARTICLES AND FIELDS',
        'Theory-Nucl': '72 PHYSICS OF ELEMENTARY PARTICLES AND FIELDS',
        'Experiment-Nucl': '72 PHYSICS OF ELEMENTARY PARTICLES AND FIELDS',
        'Phenomenology-HEP': '72 PHYSICS OF ELEMENTARY PARTICLES AND FIELDS',
        'Theory-HEP': '72 PHYSICS OF ELEMENTARY PARTICLES AND FIELDS',
        'Other': '71 CLASSICAL AND QUANTUM MECHANICS, GENERAL PHYSICS',
        }


    rec = etree.Element("rec")
    recid = bfo.recID
    if record_exists(recid) == -1:
        return etree.tostring(rec, encoding='UTF-8', xml_declaration=False)

    node = etree.SubElement

    for recnum in [x.replace('SPIRES-', '') for x in \
                       [r for r in get_fieldvalues(recid, "970__a") \
                            if r.startswith('SPIRES-')]]:
        # SPIRES record number is used if available to prevent OSTI loading
        # duplicate records from INSPIRE which they already got from SPIRES.
        node(rec, "accession_num").text = recnum
    if not rec.xpath('//accession_num'):
        # use regular inspire recid
        node(rec, "accession_num").text = str(recid)

    for title in get_fieldvalues(recid, "245__a"):
        node(rec, "title").text = unicode(title, "utf-8")

    # The authors in the ostixml are all strung together between author tags
    # delimited by ';' If zero or > 10 authors don't show any authors
    authors = get_fieldvalues(recid, "100__a") \
        + get_fieldvalues(recid, "700__a")

    if len(authors) <= 10 and len(authors) > 0:
        node(rec, 'author').text = \
        '; '.join([unicode(a, "utf-8") for a in authors])

    for category in get_fieldvalues(recid, "65017a"):
        if osticats.has_key(category):
            node(rec, 'subj_category').text = osticats[category]
            node(rec, 'subj_keywords').text = category

    for pubdate in get_fieldvalues(recid, "269__c"):
        node(rec, 'date').text = pubdate

    #Fermilab report numbers mapped to OSTI doc types
    for dtype in get_fieldvalues(recid, "037__a"):
        if 'fermilab' in dtype.lower():
            if "PUB" in dtype:
                doctype = 'JA'
            elif "CONF" in dtype:
                doctype = 'CO'
            elif "THESIS" in dtype:
                doctype = 'TD'
            else:
                doctype = 'TR'
            node(rec, 'doctype').text = doctype
    # One MARC field is used for conferences and journals.  So, the following
    # journal coding handles the variations, and outputs journal and
    # conf. cites in a nice order.  If the conf has a cnum, we get the conf
    # info from its separate record in the conf. "collection."  There are a
    # few if-then gymnastics to cover possible missing information and still
    # make a note that looks okay (sort of)
    journals = bfo.fields('773__', repeatable_subfields_p=True)
    for journal in journals:
        if journal.has_key('p'):
            jinfo = str(journal['p'][0])
            if journal.has_key('v'):
                jinfo += ' %s' % journal['v'][0]
            if journal.has_key('c'):
                jinfo += ':%s' % journal['c'][0]
            if journal.has_key('y'):
                jinfo += ',%s' % journal['y'][0]
            node(rec, 'journal_info').text = unicode(jinfo, "utf-8")

        confstring = ''
        # without t info or cnum don't print anything
        if journal.has_key('t'):
            confstring += '%s: ' % journal['t'][0]
        if journal.has_key('w'):
            conf_info = {}
            cnum = journal['w'][0].replace("/", "-")
            idrec = perform_request_search(p="111__g:" + str(cnum), \
                                               c='Conferences')
            if idrec:
                for subfield in ('a', 'c', 'd'):
                    val = get_fieldvalues(idrec[0], '111__%s' % subfield, \
                                              repetitive_values=True)
                    if val:
                        conf_info[subfield] = val[0]
                confstring += '%s. %s, %s.' % \
                    tuple(conf_info.get(x, '') for x in ('a', 'c', 'd'))
        if journal.has_key('c') and confstring != '':
            confstring += ' pp: %s' % journal['c'][0]

    for doi in get_fieldvalues(recid, "0247_a"):
        node(rec, 'doi').text = doi

    if journals and confstring != '':
        # because it has to come after doi (?)
        # although order is not guaranteed for XML serialization
        node(rec, 'conf_info').text = unicode(confstring, "utf-8")

    for pages in get_fieldvalues(recid, "300__a"):
        node(rec, 'format').text = '%s pages' % pages

    for lang in get_fieldvalues(recid, "041__a"):
        node(rec, 'language').text = lang
    # As with journals, eprints are in with report nos. in our MARC format
    # so they have to be separated out
    eprint = ''
    for repno in get_fieldvalues(recid, "037__a"):
        if "arXiv" in repno:
            eprint = repno
            node(rec, 'arXiv_eprint').text = \
                'arXiv eprint number %s' % unicode(repno, "utf-8")
        else:
            node(rec, 'report_number').text = unicode(repno, "utf-8")

    urls = bfo.fields('8564_', repeatable_subfields_p=True)
    for url in urls:
        if url.has_key('y') and "FERMILAB" in url['y'][0] and url.has_key('u'):
            node(rec, 'url').text = '%s.pdf' % unicode(url['u'][0], "utf-8")

    if eprint:
        node(rec, 'availability').text = \
            'http://arXiv.org/abs/%s' % eprint

    node(rec, 'sponsor_org').text = 'DOE Office of Science'

    dt_harvest = get_modification_date(recid)
    if dt_harvest:
        node(rec, 'dt_harvest').text = dt_harvest
    else:
        # fallback to SPIRES era marc
        for date in get_fieldvalues(recid, "961__c"):
            node(rec, 'dt_harvest').text = date

    out = etree.tostring(rec, encoding='UTF-8', xml_declaration=False, \
                              pretty_print=True, method='xml').rstrip('\n')
    return out

def get_modification_date(recid, fmt="%Y-%m-%d"):
    """
    Returns the date of last modification for the record 'recid'.
    """

    from invenio.search_engine import run_sql
    date = run_sql("SELECT DATE_FORMAT(modification_date, %s)" \
                       + " FROM bibrec WHERE id=%s", (fmt, recid), 1)
    if date:
        return date[0][0]
    return ''

# pylint: disable=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """

    return 0
# pylint: enable=W0613
