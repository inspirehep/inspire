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

    # Process to add link, highlight and format affiliation
    output = "<div style=\"text-align: center; margin: 0 auto; display: inline\">"
    newline = "<br />"

    for pubinfo in pubinfos:
        if 'p' in pubinfo:
            output += newline + pubinfo['p'] + ' ' + pubinfo['v'] + ' (' + pubinfo['y'] + ') ' + pubinfo['c']
        if 'x' in pubinfo:
            output += newline + pubinfo['x']

    output += "</div>"
    return output
    # Uncomment next line if default value must be returned
    # return 'whatever'

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
