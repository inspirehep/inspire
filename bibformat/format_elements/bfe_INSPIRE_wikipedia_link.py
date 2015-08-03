# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015 CERN.
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
"""BibFormat element - return link to Wikipedia for the author
"""


def format_element(bfo):
    """
    Create link to Wikipedia from HepNames author data
    """

    bai = bfo.fields('035__')

    for item in bai:
        if item.has_key('9') and item['9'].lower() == 'wikipedia' and item.has_key('a'):
            return '<a href="https://wikipedia.org/wiki/' + item['a'] + '">'+ '[Wikipedia]' +'</a>'


# pylint: disable=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """

    return 0
# pylint: enable=W0613
