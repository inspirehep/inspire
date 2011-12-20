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
"""BibFormat element - Prints Update Button
"""
__revision__ = "$Id$"

import urllib

def format_element(bfo, separator='; '):
    """
    This is the default format for adding an update button
    @param separator: the separator between urls.
    @param style: CSS class of the link
    """
    try:
        hepnames_id = bfo.fields('970__a')[0]
        irn = hepnames_id.split('-')[1]
    except:
        return ''

    url = "http://www.slac.stanford.edu/spires/find/hepnames/wwwupd2?IRN=" + urllib.quote(irn)
    return '<a href="' + url + '">' + '<img src="/img/update.jpg"></a>'

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
