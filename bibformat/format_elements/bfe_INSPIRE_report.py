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
"""BibFormat element - report numbers (other than arxiv)
"""
__revision__ = "$Id$"

import cgi
from urllib import quote
from bfe_INSPIRE_arxiv import get_arxiv

def format(bfo, links="no", incl_arxiv="no"):
    """
    Provides report numbers

    @param links yes(not implemented)->display links to repositories if known no(default)->  value only
    @param arxiv no (default)-> excludes arxiv numbers yes-> includes

    """


    primary_report_numbers = bfo.fields('037__')
    additional_report_numbers = bfo.fields('088__')
    report_numbers = primary_report_numbers
    report_numbers.extend(additional_report_numbers)
    report_numbers = [num.get('a','') for num in report_numbers]


    if incl_arxiv.lower() == "no":
        arxiv=get_arxiv(bfo, category="no")
        report_numbers=filter(lambda x:x not in arxiv,report_numbers)

   # if links.lower() == 'yes':
        # nothing here...
    out = ', '.join(report_numbers)

    return(out)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

