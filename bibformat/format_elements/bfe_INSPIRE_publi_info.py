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

from invenio.bibknowledge import get_kbd_values
import cgi

def format(bfo, style='eu', markup = 'html'):
    """
    Displays inline publication information

    @param style takes 'us' or 'eu'(default)  which changes date location
    @param markup takes 'latex' or 'html'(default) which sets the markup used

    """
    out = ''

    publication_info = bfo.fields('773__')


    if publication_info == []:
        return ""


    publication_info = publication_info[0]
    journal_source = publication_info.get('p', '')
    volume = publication_info.get('v')
    year = publication_info.get('y')
    number = publication_info.get('n')
    pages = publication_info.get('c')
    url = publication_info.get('u')
    doi = publication_info.get('a')
    conf_code = publication_info.get('w')
    conf_type = publication_info.get('t')

    if journal_source:
        if not (volume or number or pages or doi):
            out += " Submitted to: "
            out += cgi.escape(journal_source)

        else:

            if journal_source:
                journal_source = cgi.escape(journal_source)
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
            if markup.lower() == 'latex':
                journal_source = journal_source.replace(".",'.\\ ')
            out += journal_source



            if style.lower() == 'eu':
                if volume:
                    if markup.lower() == 'latex':
                        out += ' {\\bf ' + volume + ' }'
                    else:
                        out += ' ' + volume
                if year:
                    out += ' (' + year + ') '
                if number:
                    out += ' ' + number + ', '
                if pages:
                    out += ' ' + pages
            else:
                if volume:
                    if markup.lower() == 'latex':
                        out += ' {\\bf ' + volume + '}'
                    else:
                        out += ' ' + volume
                if number:
                    out += ', no. ' + number
                if pages:
                    if markup.lower() == 'latex':
                        out += ', ' + pages
                    else:
                        out += ': ' + pages
                if year:
                    if markup.lower() == 'latex':
                        out += ' (' + year + ')'
                    else:
                        out +=  ', ' + year


    elif conf_code:
        pass
        # Do nothing, instead use bfe_INSPIRE_conference
        # if conf_type:
        #     conf_type = bfo.kb('talktype', conf_type)
        #     out += cgi.escape(conf_type)
        # conf_code = get_kbd_values('conferences', conf_code)
        # out += " " + cgi.escape(conf_code)
    else:
        # not a conference, we should do our best if there is nothing else
        backup_out = publication_info.get('x')

    if out:
        return out
    elif not conf_code and backup_out:
        return backup_out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0





