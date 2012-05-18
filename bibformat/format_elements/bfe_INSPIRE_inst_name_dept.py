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
"""BibFormat element - Prints 110a and 110b
"""
__revision__ = "$Id$"

import cgi

def format_element(bfo, note_suffix, separator=', '):
    notes = []
    x = bfo.fields('110__')

    for item in x:
        if 'a' in item and 'b' in item:
            notes.append(item['a'] + " - " + item['b'])
        elif 'a' in item and not 'b' in item:
            notes.append(item['a'])
        elif 'b' in item and not 'a' in item:
            notes.append(item['b'])

    return separator.join(notes)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
