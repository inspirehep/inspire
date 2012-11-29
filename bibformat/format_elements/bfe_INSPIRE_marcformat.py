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
"""BibFormat element - Prints link to MARC-format if user has access.
"""

from invenio.urlutils import create_html_link
from invenio.config import CFG_BASE_URL, CFG_SITE_RECORD
from invenio.access_control_engine import acc_authorize_action
from invenio.search_engine import get_all_collections_of_a_record


def format_element(bfo, style=""):
    """
    Prints link to MARC-format if user has access.
    """
    out = ""
    user_info = bfo.user_info
    if bfo.recID and user_can_perform_action_on_collection(user_info, bfo.recID, 'runbibedit'):
        linkattrd = {}
        if style != '':
            linkattrd['style'] = style
        out += create_html_link('%s/%s/%s/export/hm?ln=%s' % \
                                (CFG_BASE_URL, CFG_SITE_RECORD, str(bfo.recID), bfo.lang),
               {},
               link_label="MARC",
               linkattrd=linkattrd)
    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0


def user_can_perform_action_on_collection(req, recid, action=""):
    """ Check if user has authorization to modify a collection
    the recid belongs to
    """
    record_collections = get_all_collections_of_a_record(recid)
    if not record_collections:
        # Check if user has access to all collections
        auth_code, auth_message = acc_authorize_action(req, action,
                                                       collection='')
        if auth_code == 0:
            return True
    else:
        for collection in record_collections:
            auth_code, auth_message = acc_authorize_action(req, action,
                                                           collection=collection)
            if auth_code == 0:
                return True
    return False
