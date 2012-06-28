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
"""BibFormat element - Prints HEP Thesis Info
"""
__revision__ = "$Id$"

def format_element(bfo, separator=''):
    """
    This is the default format for formatting full-text URLs.
    @param separator: the separator between urls.
    @param style: CSS class of the link
    """
    bai = bfo.fields('502__')
    output = ''

    for item in bai:
        if item.has_key('a'):
            output += item['a'] + " - "
        if item.has_key('b'):
            output += item['b'] + " "
        if item.has_key('c'):
            output += '<a href="/search?ln=en&amp;cc=Institutions&amp;p=110__u%3A%22' + item['c'] + '%22">' + item['c'] + "</a> "
        if item.has_key('d'):
            output += "(" + item['d'] + ")"

    return output

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
