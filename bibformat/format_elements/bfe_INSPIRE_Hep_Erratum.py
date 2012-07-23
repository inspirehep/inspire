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
"""BibFormat element - Hep Erratum info
"""


def format_element(bfo):
    """
    Prints Hep Erratum info
    """
    pubinfos = bfo.fields('773__')

    if not pubinfos:
        return ""

    # Process pubnotes
    newline = "<br />"
    out = []
    for pubinfo in pubinfos:
        if 'p' in pubinfo:
            out.append("<strong>" + pubinfo['p'] + ' ' + pubinfo['v'] + ' (' + pubinfo['y'] + ') ' + pubinfo['c'] + "</strong>")
        if 'x' in pubinfo and ("In *".lower() in pubinfo['x'].lower() or "Also in *".lower() in pubinfo['x'].lower()):
            out.append("<small>" + pubinfo['x'] + "</small>")

    return newline.join(out)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
