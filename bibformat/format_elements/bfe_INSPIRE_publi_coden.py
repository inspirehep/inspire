# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
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
"""Print coden associated with the bfo (if it has a pubnote)"""


from invenio.bibknowledge import get_kbr_keys


def format_element(bfo, separator=','):
    """Produces a SPIRES-style coden reference for a record"""
    return get_coden_formatted(bfo, separator)


def get_coden_formatted(bfo, separator=','):
    """Produces a SPIRES-style coden reference for a record

    This typically looks like JOURNAL-CODEN,VOLUME,FIRSTPAGE

    If this is impossible (for example if we lack sufficient information about
    the reference or lack a CODEN lookup KB), produces empty string.

    @param separator A string used to join the pieces of the reference
    """
    coden = ''
    publication_info = bfo.fields('773__')
    if publication_info:
        publication_info = publication_info[0]
    else:
        return ''
    journal = publication_info.get('p', '')
    volume  = publication_info.get('v', '')
    pages   = publication_info.get('c', '')

    if pages:
        dashpos = pages.find('-') 
        if dashpos > -1: 
            pages = pages[:dashpos]

    try:
        if journal and (volume != '' or pages != ''):
            coden = separator.join([get_kbr_keys("CODENS", searchvalue=journal, searchtype='e')[0][0], volume, pages])
    except:
        return ''

    return coden


# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
