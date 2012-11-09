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
"""BibFormat element - Prints link to search result for contributions
"""

from invenio.search_engine import search_pattern

def format_element(bfo, newline=False):
    """
    Prints link to all contributions related to certain CNUM.
    """

    #check if it's a conference paper (contribution)
    info = bfo.fields('980')
    confpap = False
    for field in info:
        if field.has_key('a'):
            if field['a'].lower() == "conferencepaper":
                confpap = True
    if confpap == True:
        # it's a proceeding, so return nothing
        return ''

    cnum = str(bfo.field('773__w'))
    out = ""
    if not cnum:
        #No CNUM, return empty string
        return out
    # some CNUMs have "/" and some have "-" as separator, we need to check both
    if "/" in cnum:
        cnum2 = cnum.replace("/", "-")
    else:
        cnum2 = cnum.replace("-", "/")
    out = '<a href= "/search?p=773__w:' + cnum + ' or 773__w:' + cnum2 + \
    ' and 980__a:ConferencePaper">Contributions</a>'
    if newline:
        out += '<br />'

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
