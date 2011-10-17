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
"""BibFormat element - Prints INSPIRE jobs contact name HEPNAMES search
"""

from urllib import quote_plus

def format_element(bfo, style="", separator=', '):
    """
    This is the default format for formatting the contact person
    link in the Jobs format. This link will point to a direct search
    in the HepNames database.

    @param style: CSS class of the link
    @type style: str

    @param separator: the separator between names.
    @type separator: str
    """

    contact_list = bfo.fields("270__p")
    if style != "":
        style = 'class="'+style+'"'

# KEEP UNTIL HEPNAMES ARE ON INSPIRE
#    urls = ['<a '+ style + \
#            'href="/search?ln=en&cc=HepNames&p=' + quote_plus(contact) + '">' + contact +'</a>'
#            for contact in contact_list]
    # SPIRES link http://www.slac.stanford.edu/spires/find/hepnames/www?rawcmd=FIND+NAME+DIXON%2C+Ned+S%2E
    contacts = ['<a '+ style + \
            ' href="http://www.slac.stanford.edu/spires/find/hepnames/www?rawcmd=FIND+NAME+' \
            + quote_plus(contact) + '">' + contact +'</a>'
            for contact in contact_list]

    return separator.join(contacts)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
