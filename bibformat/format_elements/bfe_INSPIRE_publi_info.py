# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints publcation information and link to ejournal
"""
__revision__ = "$Id$"

from urllib import quote
import cgi

def format(bfo,style='us'):
    """
    Displays inline publication information with html link to ejournal
    (when available).
    @param style takes 'us'(default) or 'eu'  which changes date location
    
    """
    out = ''

    publication_info = bfo.fields('773__')
    action_notes = bfo.fields("583__a")

    if publication_info == [] and action_notes == []:
        return ""

    if publication_info:
        publication_info = publication_info[0]
        journal_source = publication_info.get('p', '')
        journal = bfo.kb('ejournals', journal_source)
        volume = publication_info.get('v')
        year = publication_info.get('y')
        number = publication_info.get('n')
        pages = publication_info.get('c')
        url = publication_info.get('u')

    if bfo.field('960__a') in ['11', '10', '90', '91']:
        out += " Submitted to: "
        out += cgi.escape(journal_source)

    else:

        if journal:
            journal = cgi.escape(journal)
        if volume:
            volume = cgi.escape(volume)
        if year:
            year = cgi.escape(year)
        else:
            year = ''
        if number:
            number = cgi.escape(number)
        if pages:
            pages = cgi.escape(pages)
        else:
            pages = ''
        out += journal_source
        if style.lower() == 'eu':
            if volume:
                out += ': ' + volume
            if year:
                out += ' (' + year + ') '
            if number:
                out += 'no. ' + number + ', '
            if pages:
                out += 'pp. ' + pages
            out += publication_info.get('d', '')
        else:   #defaults to US style
            if volume:
                out +=  ' '+volume
            if number:
                out += ', no. ' + number 
            if pages:
                out += ': ' + pages
            if year:
                out +=  ', '+ year
            out += publication_info.get('d', '')

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0





