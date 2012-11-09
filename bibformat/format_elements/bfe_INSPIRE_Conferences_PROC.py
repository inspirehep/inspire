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
"""BibFormat element - Prints link to proceedings for conferences
"""

from invenio.search_engine import search_pattern

def format_element(bfo, newline=False):
    """
    Prints link to single proceeding if the proceeding exists.
    If not, nothing is returned.

    @param newline if True, add <br /> at the end
    """

    cnum = str(bfo.field('111__g'))
    out = ""
    if not cnum:
        #Something is wrong, return empty string
        return out
    search_result = search_pattern(p="773__w:" + cnum + " and 980__a:proceedings")
    if search_result:
        recID = list(search_result)[0]
        if recID != '':
            out = '<a href="/record/' + str(recID) + '">Procedings</a>'
            if newline:
                out += '<br/>'

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
