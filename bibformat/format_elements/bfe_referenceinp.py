# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2010 CERN, SLAC
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
"""BibFormat element - Prints reference input box"""


import simplejson

from invenio.bibknowledge import get_kb_mappings
from invenio.search_engine import search_unit
from invenio.bibformat import format_record


def format_element(bfo, reference_prefix, reference_suffix):
    """
    Prints the references of this record

    @param reference_prefix a prefix displayed before each reference
    @param reference_suffix a suffix displayed after each reference
    """

    if reference_prefix == None: reference_prefix = ''
    if reference_suffix == None: reference_suffix = ''

    out = ""
    tableid = 0
    for reference in bfo.fields("999C5", escape=0):
        tableid += 1

        ordinal       = reference.get('o', '')
        clean_report  = reference.get('r', '')
        clean_journal = reference.get('s', '')
        clean_doi     = reference.get('a', '')
        h_key         = reference.get('h', '')
        m_key         = reference.get('m', '')
        inputid = 'c' + str(tableid)

        format_line = reference_prefix
        # the onfocusout chgcite() js is called in the format_template referenceinp
        ref_out = '<td><input type="text" name="cite" size="35" value="%s" class="cite_search_box" id="%s" onChange="chgcite(this.id)"></td>' % (_first_nonempty([clean_report, clean_journal, clean_doi]),inputid)

        recid = _get_unique_recid_for(clean_journal, clean_report, clean_doi)
        if recid:
            ref_out += '<td><small>' + format_record(recid, 'hs') + '</small></td>'
        else:
            ref_out += '<td><small>%s %s <a href="http://dx.doi.org/%s">%s</a> %s</small></td>' % (h_key, m_key, clean_doi, clean_doi, clean_journal)
        #<input id="t%(tableid)s" type="button" onclick="insRow(this.id)" value = "V"> (the previous button for safekeeping)
        format_line = """<table id="t%(tableid)s" ><tr id="tr%(tableid)s"><td>%(ordinal)s</td><td><input id="t%(tableid)s" type="image"  src="/img/add.png" onclick="insertRowAfter(%(tableid)s); return false;" value = "+"></td>%(ref_out)s</tr></table>""" % {'tableid': str(tableid), 'ref_out': ref_out, 'ordinal': ordinal}
        format_line += reference_suffix

        out += format_line

    # In our BFT we will want to have an onSubmit() handler which substitutes
    # every short title for a coden; this makes the data for that available
    #out += '\n<script type="text/javascript">gCODENS = %s</script>\n' % (get_kb_mappings_json('CODEN_MAP'), )
    out += _get_json_dump_of_codens()

    return out


# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """Should BibFormat escape this element's output?

    No.
    """
    return 0
# pylint: enable-msg=W0613


def _first_nonempty(ls):
    """Iterate through a list, return the first value != '' or else return ''"""
    for item in ls:
        if item != '':
            return item
    return ''


def _get_unique_recid_for(journal='', report='', doi=''):
    """Return the recid for this set of identifiers.

    If no recid can be found or if too many are found, returns 0 to indicate
    failure.
    """

    hits = []
    if journal:
        hits = search_unit(f='journal', p=journal)
    if report and len(hits) != 1:
        hits = search_unit(f='reportnumber', p=report)
    if doi and len(hits) != 1:
        hits = search_unit(f='doi', p=doi)

    if len(hits) > 1:
        # FIXME: should throw exception or maybe show multiple possibilities
        return 0
    elif len(hits) == 1:
        return hits.pop()
    else:
        return 0

def _get_json_dump_of_codens():
    """Dump codens to a global variable where our javascript can get it.

    In our BFT we will want to have an onSubmit() handler which substitutes
    every short title for a coden; this makes the data for that available"""

    return '\n<script type="text/javascript">gCODENS = %s</script>\n' % simplejson.dumps(dict([(x['value'], x['key']) for x in get_kb_mappings('CODENS')]))

