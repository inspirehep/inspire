# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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
"""BibFormat element - Prints the list of the "children" institutions
   for a given institution
"""


def format_element(bfo, separator='; '):
    """
    Prints the list of the "children" institutions
    """
    from invenio.search_engine import search_pattern
    from invenio.bibformat_engine import BibFormatObject

    recID = str(bfo.recID)
    out = ""
    children = []
    if not recID:
        #Something is wrong, return empty string
        return out
    all_institutions = search_pattern(p="510__0:" + str(recID))
    for institution_id in all_institutions:
        for field in BibFormatObject(institution_id).fields('510__'):
            if field.get('0') == str(recID) and field.get('w') == 't':
                children.append(institution_id)

    if children:
        out += "Subsidiary Institution: "
        for item in children:
            # get the abbreviated name of the institution
            abbrev = BibFormatObject(item).field('110__t')
            # if there is no abbreviated name, we try different names
            if not abbrev:
                abbrev = BibFormatObject(item).field('110__u')
            if not abbrev:
                abbrev = BibFormatObject(item).field('110__a')
            if not abbrev:
            # if no name is found, we display record ID as a text of the link
                abbrev = item
            out += '<a href="/record/' + str(item) + '">' + str(abbrev) \
                + '</a>' + separator

    # remove last separator and space, then return the string
    out = out[:-2]
    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
