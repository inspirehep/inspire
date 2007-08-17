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

def format(bfo):
    """
    Displays inline publication information with html link to ejournal
    (when available).
    TODO: Complete element to display full publ. info.
    """
    out = ''

    publication_info = bfo.fields('773__')
    action_notes = bfo.fields("583__a")

    if publication_info == [] and action_notes == []:
        return ""

    if publication_info:
        publication_info = publication_info[0]
        journal_source = publication_info.get('p')
        journal = bfo.kb('ejournals', journal_source)
        volume = publication_info.get('v')
        year = publication_info.get('y')
        number = publication_info.get('n')
        pages = publication_info.get('c')
        url = publication_info.get('u')
    if action_notes:
        for action_note in action_notes:
            if action_note == 'yes':
                out += '<br /><small><img border="0" ' + \
                       'src="/img/iconpen.gif" alt="open icon"/></small>' 
                out += " - Submitted as a scientific note."
                if journal_source:
                    out += 'After approval will be submitted to Journal ' + \
                           '<span style="color:#0A0">' + cgi.escape(journal_source) + \
                           '</span> .'
                out += 'All ATLAS members are invited to ' + \
                       '<a href="http://doc.cern.ch/EDS/snotes/sendc.php?rn=' + \
                        quote(bfo.field('037__a')) + \
                        '''">send comments</a> within 4 weeks from the
                        submission date (''' + bfo.field('961__x', 2) + ')'

    elif bfo.field('960__a') in ['11', '10', '90', '91']:
        out += " - Submitted to: "
        if journal is not None:
            journal = cgi.escape(journal)
            out += '<i><a href="http://weblib.cern.ch/cgi-bin/ejournals?publication=' + \
                   journal_source.replace(' ', '+') + '" >' + \
                   cgi.escape(journal_source) + '</a></i>'
        else:
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
        if url:
            url = cgi.escape(url)
        else:
            url = ''
        if journal:
            if volume:
            
                out += 'Published in <b class="nounderline"><a href="http://weblib.cern.ch/cgi-bin/ejournals?publication='
                out += journal_source.replace(' ', '+')
                out += '&amp;volume=' + volume
                if year:
                    out += '&amp;year=' + year
                if pages:
                    out += '&amp;page='
                    page = pages.split('-')# get first page from range
                    if len(page) > 0:
                        out += page[0]
                out += '">%(journal)s %(volume)s (%(year)s) %(page)s</a></b>' % {'journal': journal,
                                                                            'volume': volume,
                                                                            'year': year,
                                                                            'page': pages}
            elif number and \
                     bfo.kb('ejournals_base', journal_source) is not None:
                out += 'Published in <b class="nounderline"><a href="' + \
                       bfo.kb('ejournals_base', journal_source) + \
                       number + '">' + cgi.escape(journal_source) + \
                       '</a></b>'
        else:
            out += 'Published in ' 
            if url:
                out += """<b class="nounderline"><a href="%s">%s</a></b>""" % (url, journal_source)
            else:
                out += journal_source 
             
            if volume:
                out += ': ' + volume 
            if year:
                out += ' (' + year + ') '
            if number:
                out += 'no. ' + number + ', '
            if pages:
                out += 'pp. ' + pages
            out += publication_info.get('d', '')
         
    return out
      
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0





