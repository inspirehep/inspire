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

def format_element(bfo, fvalue, tag, default = "0 Records found"):
    """ uses tag to fetch a tag from the given bfo, searches that value in
    fvalue, and outputs the number of records found, linked to a search
    for those recs.
    @param fvalue field to search
    @param tag tag from record to use to search
    @param default returned if there are no results
    """
    out = ''
    reccnt = 0
    pvalue = bfo.field(tag)
    reccnt = len(search_pattern(p=pvalue, f=fvalue).tolist())
    if reccnt > 0:
        out = "<a href=\"" + CFG_SITE_URL + "/search?f=" + fvalue + "&p=" + pvalue + "\">" +str(reccnt) + "</a> Records"
        return out
    return default
def escape_values(bfo):
    return 0
