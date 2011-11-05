# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
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
"""BibFormat element - Prints publcation information and link to ejournal
"""

from invenio.bibformat_elements.bfe_INSPIRE_arxiv import get_arxiv
#from invenio.bibknowledge import get_kbd_values
import cgi

def format_element(bfo, style='eu', markup = 'html', separator = ', '):
    """
    Displays inline publication information

    @param style takes 'us' or 'eu'(default)  which changes date location
    @param markup takes 'latex' or 'html'(default) which sets the markup used

    """
    
    latexperiod = ''
    displayouts = []
    displaycnt = 0
    backup_out = ''

    publication_infos = bfo.fields('773__')

    for publication_info in publication_infos :
        out = ''
        journal_source = cgi.escape(publication_info.get('p', ''))
        volume         = cgi.escape(publication_info.get('v', ''))
        year           = cgi.escape(publication_info.get('y', ''))
        number         = cgi.escape(publication_info.get('n', ''))
        pages          = cgi.escape(publication_info.get('c', ''))
        doi            = publication_info.get('a')
        conf_code      = publication_info.get('w')
        latex_p        = markup.lower() == 'latex'
        eu_style_p     = style.lower() == 'eu'

        if journal_source:
            if not (volume or number or pages or doi):
                out += "Submitted to: "
                if latex_p:
                    out = '%' + out
                out += journal_source

            else:
                if latex_p:
                    journal_source = journal_source.replace(".",'.\\ ')
                out += journal_source

            if volume:       # preparing volume and appending it
                if latex_p:
                    char_i = 0
                    for char in volume:
                        if char.isalpha():
                            char_i += 1
                        else:
                            break
                    journal_letter = volume[:char_i]
                    volume_number = volume[char_i:]
                    out += journal_letter + '\\ {\\bf ' + volume_number + '}'
                else:
                    out += ' ' + volume

            if year:         # preparing year; it's appended below
                if eu_style_p or latex_p:
                    year = ' (' + year + ')'
                else:
                    year = ', ' + year

            if number:       # preparing number; it's appended below
                if eu_style_p:
                    number = ' ' + number + ', '
                else:
                    number = ', no. ' + number

            if latex_p:
                if pages:
                    dashpos = pages.find('-') 
                    if dashpos > -1:
                        pages = pages[:dashpos]

            if eu_style_p:   # EU style reference
                out += year
                out += number
                if pages:
                    out += ' ' + pages
            else:            # US style reference
                out += number
                if pages:
                    if latex_p:
                        out += ', ' + pages
                    else:
                        out += ': ' + pages
                out += ' ' + year
            displaycnt += 1            
            if displaycnt > 1 :
                if latex_p:
                    out = '[' + out + ']'    
            displayouts.append(out)

        elif conf_code:
            pass
            # Do nothing, instead use bfe_INSPIRE_conference
            # if conf_type:
            #     conf_type = bfo.kb('talktype', conf_type)
            #     out += cgi.escape(conf_type)
            # conf_code = get_kbd_values('conferences', conf_code)
            # out += " " + cgi.escape(conf_code)
        else:
            # no journal source and not a conference, we should do our best if
            # there is nothing else
            backup_out = publication_info.get('x')

    if displayouts :
        # determine if there's an arxiv number to decide whether to put a
        # period after the pub-note.  There should be a period after either
        # a pub-note or an Arxiv number, but not two periods, and no period if no pub/arxiv info.
        if latex_p:
            if not get_arxiv(bfo, category="no"):
                latexperiod = '.'
                    
        return separator.join(displayouts) + latexperiod
    elif backup_out:
        return backup_out


# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
