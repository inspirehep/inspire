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
"""BibFormat element - Prints document date
"""
__revision__ = "$Id$"

from invenio.dateutils import convert_datetext_to_dategui
import re

def format(bfo):
    """
    Prints best available date

    """

    date = bfo.fields('269__c')
    if date:
        out=convert_datetext_to_dategui(date)
        if out:
            return(out)
    primary_report_numbers = bfo.fields('037__')
    additional_report_numbers = bfo.fields('088__')
    report_numbers = primary_report_numbers
    report_numbers.extend(additional_report_numbers)
    arxiv = [num.get('a','') for num in report_numbers if num.get('s') == 'arxiv']
    if arxiv:
        date=re.search('(\d+)',arxiv[0]).groups()[0]
        if len(date) >=4:
            year = date[0:2]
            if year > '90':
                year='19'+year
            else:
                year='20'+year
            date = year+'-'+date[2:4]
            return convert_datetext_to_dategui(date)
        

    date = bfo.fields('961__x')
    if date:
        return convert_datetext_to_dategui(date)

    return None
