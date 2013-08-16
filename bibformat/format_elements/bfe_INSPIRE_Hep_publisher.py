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
"""BibFormat element - Prints dates for Experiment.
"""
__revision__ = "$Id$"


def format_element(bfo, separator=" "):
    """
    Adds information from 260__x datafield.
    """
    date_fields = bfo.fields('260__')
    # Make sure the same information is only printed once

    date_list = []
    for date in date_fields:
        if date not in date_list:
            date_list.append(date)
    out = []

    for item in date_list:
        text = []
        if item.has_key('a'):
            text.append(item['a'] + ':')
        if item.has_key('b'):
            text.append(' ' + item['b'])
        if item.has_key('c'):
            text.append(' (' + item['c'] + ')')
        out.append(" ".join(text))

    if out:
        return separator.join(out)
    else:
        return ''


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
