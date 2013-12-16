# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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
"""BibFormat element - Creates update references button
"""


def format_element(bfo, position='top'):
    out = """
    <div id='referenceinp_link_box'>
        <span id='referenceinp_link_span'>
    """
    references = bfo.fields("999C5", escape=1, repeatable_subfields_p=True)
    if references:
        out += "<a id='referenceinp_link' href='/record/%s/export/hru'>Update these references</a>" % bfo.control_field("001")
    else:
        if position == "bottom":
            out += "<a id='referenceinp_link' href='/record/%s/export/hra'>Add references</a>" % bfo.control_field("001")
        else:
            return ""
    out += """
        </span>
    </div>
    """
    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
