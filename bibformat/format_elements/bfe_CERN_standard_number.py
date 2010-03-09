# -*- coding: utf-8 -*-
##
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
"""BibFormat element - Prints the report standard number
"""

__revision__ = ""



def format(bfo, limit, extension=" etc.", separator=" "):
    """
    Prints the report standard number(s)

    @param limit max number of standard numbers to print
    @param extension a suffix printed if 'limit' is reached
    """

    numbers=[]

    numbers = bfo.fields("021__a")

    if limit.isdigit() and int(limit) <= len(numbers):
        return separator.join(numbers[:limit]) + extension
    else:
        return separator.join(numbers)
