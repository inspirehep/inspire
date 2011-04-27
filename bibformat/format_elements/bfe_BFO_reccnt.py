# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
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
"""BibFormat element - Prints record count for BFO search, provides link to search.
"""
__revision__ = "$Id$"
from invenio.config import CFG_SITE_LANG, CFG_SITE_URL

from invenio.search_engine import search_pattern

def format_element(bfo, fvalue, tag, items = "Records", printtag = "",
    default = "", number_only = False):
    """ uses tag to fetch a tag from the given bfo, searches that value in
    fvalue, and outputs the number of records found, linked to a search
    for those recs.
    @param fvalue field to search
    @param tag tag from record to use to search
    @param items string for X ITEMS found
    @param printtag if non-null string will print X ITEMS <printtag>
    <tagvalue>
       so printtag=from would give:
       23 Papers from SLAC
    @param default returned if there are no result [0 items]
    @param number_only return only the number of itesm with no formatting
    """
    text = items
    out = ''
    reccnt = 0
    tagvalue = bfo.field(tag)
    if tagvalue:
        if printtag:
            text += " " + printtag + " " + tagvalue
        tagvalue = "'" + tagvalue + "'"
        reccnt = len(search_pattern(p=tagvalue, f=fvalue).tolist())
        if number_only:
            return reccnt
        if reccnt > 0:
            out = "<a href=\"" + CFG_SITE_URL + "/search?f=" + fvalue + "&p=" \
                  + tagvalue + "\" >" +str(reccnt) + " " + text + " </a> "
            return out

    if not default:
        default = "0 " + text
    return default

def escape_values(bfo):
    return 0
