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
"""BibFormat element - Prints a links to fulltext
"""
__revision__ = "$Id$"

from cgi import escape
from urllib import quote

def format(bfo, style, separator='; ', elec_loc_field='1'):
    """
    Prints HTML links to fulltext
    @param separator the separator between urls.
    @param style CSS class of the link
    @param elec_loc_field if contains '1' retrieve in 8564_. If contains '2' retrieve in 85642
    """

    urls = []
    coll = bfo.field('960__a')

    if '1' in elec_loc_field:
        urls = bfo.fields('8564_')

    if '2' in elec_loc_field:
        urls.extend(bfo.fields('85642'))

    out = []

    if style != "":
        style = 'class="'+style+'"'

    for url in urls:
        if coll in ['31', '32'] and \
               url.get('x', '') == 'map':
            # Periodicals
            continue

        elif coll in ['74', '75'] and \
                 'BUL-SA-' not in bfo.field('037__a') and \
                 bfo.field('088__a'):
            # Weekly bulletin
            continue


        elif url.has_key('u'):

            label = url.get('y', '')
            if coll in ['60', '61', '62', '63', '69'] or \
               coll in ['81', '82', '83', '84', '86','87','88', '89', '115', '117']:
                # Council documents +
                # Photos
                label = escape(url.get('z', ''))
            if label.lower() in ['', 'access to fulltext document', 'access to document', 'full text']:
                label = "Fulltext"
            if label.lower() in ['audio files']:
                label = '<img src=http://cdsweb.cern.ch/img/speaker.png border="0">' + \
                        label


            link = '<a ' + style + ' href="' + url['u'] + '">' + \
                   label + '</a>'
            out.append(link)

    if coll == '05':
        file_numbers = bfo.field('927__a')
        for file_number in file_numbers:
            if '-' in file_number or '_' in file_number:
                link = '<a href="http://doc.cern.ch/cgi-bin/setlink?base=pauli&categ=&id="%s">Fulltext</a>' % file_number
                out.append(link)

    if coll in ['74', '75'] and \
           'BUL-SA-' not in bfo.field('037__a') and \
           bfo.field('088__a'):
        # Weekly bulletin
        link = 'Published in <a href="http://bulletin.cern.ch/eng/bulletin.php?bullno=' + \
               bfo.field('088__a') +'">CERN weekly bulletin ' + bfo.field('088__a') + '</a>' + \
               ' (' + bfo.field('260__c') + ')'
        out.append(link)

    return separator.join(out)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
