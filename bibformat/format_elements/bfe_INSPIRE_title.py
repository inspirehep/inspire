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
"""BibFormat element - titles
"""
__revision__ = "$Id$"

import cgi
from urllib import quote
import re


def format(bfo,  highlight="no", force_title_case="no"):
    """
    Provides title  converts to title case (Upper Cased First Letters) if
    the title is in all caps

    
    """

    titles = bfo.fields('245', 1)


    
    out = ""


    for title in titles:
        out += title.get('a')
        

    if highlight == 'yes':
        from invenio import bibformat_utils
        out = bibformat_utils.highlight(out, bfo.search_pattern,
                                        prefix_tag="<span style='font-weight: bolder'>",
                                        suffix_tag='</style>')


    if force_title_case.lower()=="yes" and (out.upper()==out or re.search('THE ',out)):   #title is allcaps
        out=' '.join([word.capitalize() for word in out.split(' ')])   # should not cap 1 letter words...


    return out

    
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

