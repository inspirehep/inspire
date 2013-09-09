# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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
""" BibFormat element - adds the Datasets link
"""

__revision__ = "$Id$"


from invenio.config import CFG_BASE_URL


def format_element(bfo):
    """ Datasets link for the brief format.
        Only for records that are not data themselves.
    """

    out = ""
    if bfo.field("980__a") == 'DATA':
        return out

    out += "Data: "
    hep_data = bfo.fields('520__')
    for hep in hep_data:
        if hep.get('9', '') == 'HEPDATA' or hep.get('9', '') == 'Dataverse':
            #internal
            out += ' <a href="' + CFG_BASE_URL + '/record/' + str(bfo.recID) + '/hepdata">INSPIRE</a> '
            #hepdata
            links = bfo.fields('8564_')
            for link in links:
                if link.get('y', '') == 'DURHAM':
                    out += '| <a href="' + link.get('u', '') + '">HepData</a> '
                if link.get('y', '') == 'Dataverse':
                    out += '| <a href="' + link.get('u', '') + '">Dataverse</a> '
            break

    if len(out) > 6:
        return out
    else:
        return ""

# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
