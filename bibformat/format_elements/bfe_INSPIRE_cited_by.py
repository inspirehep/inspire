# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints reference to documents citing this one
"""
__revision__ = "$Id$"

import cgi
from invenio.search_engine import search_pattern



def format(bfo, separator='; ', nbOnly='no', searchlink='no'):
    """
    Prints the records (or number of records) citing this record

    DO NOT USE > testing, not on cdsweb
    @param nbOnly  only print number
    @param searchlink print number (if nbOnly) as a link to the search to find these items
    @param separator a separator between citations
    """
    from urllib import quote

   #FIXME temporary while some inspire sites migrating from .92->.99
    try:
        from invenio.config import CFG_SITE_URL
    except:
        from invenio.config import weburl as CFG_SITE_URL

    primary_report_numbers = bfo.fields('037__a')
    additional_report_numbers = bfo.fields('088__a')

    report_numbers = primary_report_numbers
    report_numbers.extend(additional_report_numbers)
    report_numbers = [quote(rep_num) for rep_num in report_numbers]

    res = []
    for rep_num in report_numbers:
        res.extend(list(search_pattern(p=rep_num, f='999C5r')))

    if nbOnly.lower() == 'yes':
        if searchlink.lower()=='yes':
            from bfe_server_info import format as bfe_server
            return '<a href="'+CFG_SITE_URL+'/search?p=recid:'+bfo.control_field('001')+'&rm=citation">'+str(len(res))+'</a>'
        else:
            return str(len(res))
    else:
        from invenio.bibformat import format_records
        return '<br/>'.join(format_records(res, 'hs'))

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
