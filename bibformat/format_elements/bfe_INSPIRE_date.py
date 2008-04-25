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

from invenio.dateutils import convert_datetext_to_datestruct
from invenio.dateutils import convert_datestruct_to_dategui
import re


def format(bfo, us="yes"):
    """
    returns dategui for the best available date, looking in several
    locations for it (date, eprint, journal, date added)
    @params us us style date Mon dd, yyyy (default)  otherwise dd mon yyyy
    """
    datestruct=get_date(bfo)
    date= re.sub(',\s00:00$','',convert_datestruct_to_dategui(datestruct))
    if us=="yes":
        return(re.sub(r' 0(\d),',r' \1,',(re.sub(r'(\d{2})\s(\w{3})',r'\2 \1,',date))))
    else:
        return(date)
    
def get_date(bfo):
    """
    returns datestruct for best available date

    """
    from invenio.bibformat_elements.bfe_INSPIRE_arxiv import get_arxiv

    #true date
    date = bfo.fields('269__c')
    if date:
        datestruct=parse_date(date[0])
        if datestruct[1]:
            return(datestruct)

    #arxiv date        
    arxiv = get_arxiv(bfo,category="no")
    if arxiv:
        date=re.search('(\d+)',arxiv[0]).groups()[0]
        if len(date) >=4:
            year = date[0:2]
            if year > '90':
                year='19'+year
            else:
                year='20'+year
            date = year+date[2:4]+'00'
            date=parse_date(date)
            if date[1]: return(date)



    #journal year
    if bfo.fields('773__y'):
        date= parse_date(bfo.fields('773__y')[0]+'0000')
        if date[0]:
            return date
            
    #date added
    if bfo.fields('961__x'):
        date= parse_date(bfo.fields('961__x')[0])
        if date[0]:
            return date
  

    return None



def parse_date(datetext):
    """
    Reads in a date imported from SPRIES, returning the datestruct
    accounts for either native spires (YYYYMMDD) or invenio style
    (YYYY-MM-DD)
    @param datetext: date from SPIRES record
    """
    import time
    match=re.search(r'\d+\-\d+\-\d+ \d+:\d+:\d+', datetext)
    if match:    
        return(convert_datetext_to_datestruct(datetext))

    datetext=datetext.split(' ')[0]      
    if re.search(r'\d+\-\d+\-\d+', datetext):
        return(convert_datetext_to_datestruct(datetext+' 0:0:0'))
    if re.search(r'\d+\-\d+', datetext):
        return(convert_datetext_to_datestruct(datetext+'-01 0:0:0'))
    if re.search(r'\d+', datetext):
        #Correct by hand spires convention of 00 for missing month and/or day
        #use instead invenio convention of 0101  
        datetext=re.sub('0000$','0101',datetext)
        datetext=re.sub('00$','01',datetext)

        try:
            return time.strptime(datetext, "%Y%m%d")
        except ValueError or TypeError:
            return (0,0,0,0,0,0,0,0,0)
    
    return (0,0,0,0,0,0,0,0,0)
