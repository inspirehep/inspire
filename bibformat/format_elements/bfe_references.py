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
"""BibFormat element - Prints references
"""

from invenio.search_engine import search_unit, get_record
from invenio.bibformat import format_record

def format_element(bfo, reference_prefix, reference_suffix):
    """
    Prints the references of this record

    @param reference_prefix a prefix displayed before each reference
    @param reference_suffix a suffix displayed after each reference
    """
    references = bfo.fields("999C5", escape=1, repeatable_subfields_p=True)

    out = ""
    last_o = ""

    if not references:
        return out

    out += "<table>"
    for reference in references:
        ref_out = []
        ref_out.append('<tr><td valign="top">')

        display_journal = ''
        display_report = ''
        clean_report = ''
        clean_journal = ''
        hits = []
        if reference.has_key('o') and not reference['o'][0] == last_o:
            temp_ref = reference['o'][0].replace('.', '')
            if '[' in temp_ref and ']' in temp_ref:
                ref_out.append("<small>" + temp_ref + "</small> ")
            else:
                ref_out.append("<small>[" + temp_ref + "] </small> ")
            last_o = temp_ref
        ref_out.append("</td><td>")

        if reference_prefix:
            ref_out.append(reference_prefix)

        if reference.has_key('s'):
            display_journal = reference['s'][0]
            clean_journal = reference['s'][0]
        if reference.has_key('r'):
            if "[" in reference['r'][0] and "]" in reference['r'][0]:
                breaknum = reference['r'][0].find('[')
                newreference = reference['r'][0][:breaknum].strip()
                display_report = newreference
                clean_report = newreference
            else:
                display_report = reference['r'][0]
                clean_report = reference['r'][0]
        if clean_report:
            hits = search_unit(f='reportnumber', p=clean_report)
        if clean_journal and len(hits)!=1:
            hits = search_unit(f='journal', p=clean_journal)
        if reference.has_key('a') and len(hits)!=1:
            hits = search_unit(p=reference['a'][0])
        if reference.has_key('0') and len(hits)!=1:
            # check if the record exists in the database
            try:
                recID = int(reference['0'][0])
                if get_record(recID):
                    # since we already have a recID, we can assign it directly
                    # to the "hits" variable, so it will be handled in the last if statement
                    hits = [recID]
            except ValueError:
                pass
        if len(hits) == 1:
            ref_out.append('<small>' + format_record(list(hits)[0],'hs') + '</small>')
        else:
            if reference.has_key('h'):
                ref_out.append("<small> " + reference['h'][0] + ".</small>")
            if reference.has_key('t'):
                ref_out.append("<small> " + reference['t'][0] + "</small> -")
            if reference.has_key('y'):
                ref_out.append("<small> " + reference['y'][0] + ".</small>")
            if reference.has_key('p'):
                ref_out.append("<small> " + reference['p'][0] + ".</small>")
            if reference.has_key('m'):
                ref_out.append("<small> "+ reference['m'][0].replace(']]', ']') + ".</small>")
            if reference.has_key('a'):
                ref_out.append("<small> <a href=\"http://dx.doi.org/" + \
                reference['a'][0] + "\">" + reference['a'][0]+ "</a></small>")
            if reference.has_key('u'):
                ref_out.append("<small> <a href=" + reference['u'][0] + ">" + \
                reference['u'][0]+ "</a></small>")
            if reference.has_key('i'):
                for r in reference['i']:
                    ref_out.append("<small> <a href=\"/search?ln=en&amp;p=020__a%3A"+r+"\">"+r+"</a></small>")

            ref_out.append('<small>')
            if display_journal:
                ref_out.append(display_journal)
            if display_report:
                ref_out.append(' ' + display_report)
            ref_out.append("</small>")

        if reference_suffix:
            ref_out.append(reference_suffix)

        ref_out.append("</td></tr>")
        out += ' '.join(ref_out)

    return out + "</table>"


# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
