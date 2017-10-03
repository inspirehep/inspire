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


from invenio.config import CFG_BASE_URL


def format_element(bfo):
    """ Datasets link for the brief format.
        Only for records that are not data themselves.
    """

    out = ""
    if bfo.field("980__a") == 'DATA':
        return out

    out += "Data: "
    hepdata_out = ""
    dataverse_out = ""
    hep_data = bfo.fields('035__')
    for hep in hep_data:
        if not hepdata_out and hep.get('9', '') == 'HEPDATA':
            # add hepdata link
            hepdata_out = '| <a href="https://hepdata.net/record/ins%s">HepData</a> ' % \
                          (str(bfo.recID),)

    hep_dverse = bfo.fields('520__')
    for hep in hep_dverse:
        if not dataverse_out and hep.get('9', '') == 'Dataverse':
            # add dataverse link
            links = bfo.fields('8564_')
            for link in links:
                if link.get('y', '') == 'Dataverse':
                    dataverse_out += '| <a href="%s">Dataverse</a> ' % \
                                     (link.get('u', ''),)
                    break
    if hepdata_out or dataverse_out:
        #internal
        out += ' <a href="%s/record/%s/data">INSPIRE</a> ' % \
               (CFG_BASE_URL, str(bfo.recID))
        out += hepdata_out
        out += dataverse_out

    if len(out) > 6:
        return out
    else:
        return ""


# we know the argument is unused, thanks
# pylint: disable=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable=W0613
