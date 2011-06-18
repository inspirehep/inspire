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
__revision__ = "$Id$"

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

    publication_infos = bfo.fields('773__')
    #publication_info = publication_info[0]

    for publication_info in publication_infos :
        out = ''
        #if publication_info == []:
        #    return ""
        journal_source = publication_info.get('p', '')
        volume = publication_info.get('v')
        year = publication_info.get('y')
        number = publication_info.get('n')
        pages = publication_info.get('c')
        #url = publication_info.get('u')
        doi = publication_info.get('a')
        conf_code = publication_info.get('w')
        #conf_type = publication_info.get('t')        
        if journal_source:
            if not (volume or number or pages or doi):
                out += "Submitted to: "
                if markup.lower() == 'latex':
                    out = '%' + out
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
            displaycnt += 1            
            if displaycnt > 1 :
                if markup.lower() == 'latex' :
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
            # not a conference, we should do our best if there is nothing else
            backup_out = publication_info.get('x')

    if displayouts :
        # determine if there's an arxiv number to decide whether to put a
        # period after the pub-note.  There should be a period after either
        # a pub-note or an Arxiv number, but not two periods, and no period if no pub/arxiv info.
        if markup.lower() == 'latex' :
            arxiv=get_arxiv(bfo, category="no")
            if not arxiv :
                latexperiod = '.'
                    
        return separator.join(displayouts) + latexperiod
    elif not conf_code and backup_out:
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

#def get_arxiv(bfo,category="yes"):
#    """
#    Take a bfo and return a list of arXiv ids found within the report numbers
#    """
#
#    primary_report_numbers = bfo.fields('037__')
#    additional_report_numbers = bfo.fields('088__')
#    report_numbers = primary_report_numbers
#    report_numbers.extend(additional_report_numbers)
#
#    arxiv = [num.get('a','') for num in report_numbers if num.get('9') == 'arXiv' or num.get('s')=='arXiv']
#
#    if category=="yes":
#        cats = [num.get('c','') for num in report_numbers if num.get('9') == 'arXiv' or num.get('s')=='arXiv']
#        arxiv=map(append_cat,arxiv,cats)
#
#    return(arxiv)

