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
"""BibFormat element - Prints related institutions
"""


def format_element(bfo, style, separator='; '):
    """
    This is the default format for printing related institutions
    @param separator: the separator between institutions.
    @param style: CSS class of the link
    """

    urls_u = bfo.fields("510__")

    if style != "":
        style = 'class="'+style+'"'
    # there will be 4 different categories of institutions
    inst_dict = {'a': [],
                 'b': [],
                 't': [],
                 'r': []}

    prefix_inst = {'a': 'Preceding Institution: ',
                   'b': 'Successive Institution: ',
                   't': 'Parent Institution: ',
                   'r': 'Related Institution: '}

    for url in urls_u:
        if url.get('w') in ['a', 'b', 't', 'r']:
            inst_dict[url.get('w')].append('<a href="/record/' + url['0'] + '">' + url['a'] + '</a>')
        else:
            inst_dict['r'].append('<a href="/record/' + url['0'] + '">' + url['a'] + '</a>')

    out = ''
    for field in inst_dict:
        # is there is something inside the list, print it with prefix
        if inst_dict[field]:
            out += prefix_inst[field] + separator.join(inst_dict[field]) + '<br>'

    # return the string without last line break
    return out[:-4]


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
