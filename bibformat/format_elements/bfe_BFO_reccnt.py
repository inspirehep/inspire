# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2011 CERN.
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

import urllib

try:
    from invenio.config import CFG_BASE_URL
except ImportError:
    from invenio.config import CFG_SITE_URL
    CFG_BASE_URL = CFG_SITE_URL
from invenio.urlutils import create_html_link
from invenio.search_engine import perform_request_search

def format_element(bfo, fvalue, tag, item = "Record", printtag = "",
    default = "", number_only = False, collection='', plural = "Records"):
    """ uses tag to fetch a tag from the given bfo, searches that value in
    fvalue, and outputs the number of records found, linked to a search
    for those recs.
    @param fvalue field to search
    @param tag tag from record to use to search
    @param item string for X ITEM found - default ="Record"  (see plural)
    @param printtag if non-null string will print X ITEMS <printtag>
    <tagvalue>
       so printtag=from would give:
       23 Papers from SLAC
    @param default returned if there are no result [0 items]
    @param number_only return only the number of items with no formatting
    @param collection: which collection to search in [default=Home]
    @param plural string for X ITEMS (default = "Records")
    """
    text = ""
    reccnt = 0
    tagvalue = bfo.field(tag)
    if tagvalue:
        if printtag:
            text = " " + printtag + " " + tagvalue
        tagvalue = '"' + tagvalue + '"'
        reccnt = len(perform_request_search(p=tagvalue, f=fvalue, cc=collection))
        if number_only:
            return reccnt
        if reccnt > 0:
            if reccnt == 1:
                text = item + text
            else:
                text = plural + text
            return create_html_link(urlbase='%s/search' % (CFG_BASE_URL,),
                                    urlargd={'p': tagvalue, 'f': fvalue},
                                    link_label=str(reccnt) + " " + text)

    if not default:
        default = "0 " + text
    return default

def escape_values(bfo):
    return 0
