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
"""BibFormat element - Prints Publisher Information
"""
__revision__ = "$Id$"

def format_element(bfo, separator=' - '):
    """
    This is the default format for formatting full-text URLs.
    @param separator: the separator between urls.
    @param style: CSS class of the link
    """
    out = []
    pubs = bfo.fields('643__')

    for pub in pubs:
        if pub.has_key('a') and pub.has_key('b'):
            out.append('<a href="/search?ln=en&cc=Institutions&p=110__u%3A%27'+pub['a']+'%27&of=hd">'+pub['a']+'</a>')
            out.append(pub['b'])
        else:
            if pub.has_key('a'):
                out.append('<a href="/search?ln=en&cc=Institutions&p=110__u%3A%27'+pub['a']+'%27&of=hd">'+pub['a']+'</a>')
            if pub.has_key('b'):
                out.append(pub['b'])

    return separator.join(out)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
