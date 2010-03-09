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
"""BibFormat Print links to copy/loan a document
"""

__revision__ = "$Id$"

def format(bfo):
    """
    Print HTML link(s) to request a copy/loan of the document.
    """
    out = ""

    test_val = bfo.fields('690C_a')
    base = bfo.field('960__a')
    sysno = bfo.field('970__a')

    if "distribution" in test_val:
        out += '<a href="http://weblib.cern.ch/publreq.php?base=' + base +\
               '&amp;sysnb=' + sysno + \
               '">Request paper copy</a>'

    if "notheld" in test_val:
        out += 'Item not held in the library - ' + \
               '<a href="mailto:external.loans@cern.ch">Ask for InterLibrary Loan</a>'

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
