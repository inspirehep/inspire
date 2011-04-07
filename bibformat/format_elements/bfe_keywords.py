# -*- coding: utf-8 -*-
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
"""BibFormat element - Prints keywords
"""
__revision__ = "$Id$"

import cgi
from urllib import quote
from invenio.config import CFG_SITE_URL

def format_element(bfo, keyword_prefix, keyword_suffix, separator=' | ', link='yes'):
    """
    Display keywords of the record.

    @param keyword_prefix a prefix before each keyword
    @param keyword_suffix a suffix after each keyword
    @param separator: a separator between keywords
    @param link: links the keywords if 'yes' (HTML links)
    """

    keywords = bfo.fields('695__a')
    out = ""
    if len(keywords) > 0:
        out += "<small>INSPIRE:</small> " + \
               print_kw(bfo,
                        keyword_prefix,
                        keyword_suffix,
                        separator, link, keywords)
    keywords = bfo.fields('6531_a')
    if len(keywords) > 0:
        out += '<br /><small>Author supplied:</small> ' + \
               print_kw(bfo,
                        keyword_prefix,
                        keyword_suffix,
                        separator, link, keywords)
    return out

def print_kw(bfo,
             keyword_prefix,
             keyword_suffix,
             separator=' | ',
             link='yes',
             keywords=[]):
    """
    Print a list of words in keyword style

    @param keyword_prefix a prefix before each keyword
    @param keyword_suffix a suffix after each keyword
    @param separator: a separator between keywords
    @param link: links the keywords if 'yes' (HTML links)
    @param keywords list of keywords to print
    """

    if link == 'yes':
        keywords = ['<a href="' + CFG_SITE_URL + '/search?p=keyword:'+ \
                    quote('"' + keyword + '"') + \
                    '&amp;ln=' + bfo.lang + \
                    '">' + cgi.escape(keyword) + '</a>'
                    for keyword in keywords]
    else:
        keywords = [cgi.escape(keyword)
                    for keyword in keywords]

    keywords = [keyword_prefix + keyword + keyword_suffix
                    for keyword in keywords]
    return separator.join(keywords)

# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
