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
"""BibFormat Print series and volumes
"""

__revision__ = "$Id$"

import cgi

def format(bfo, print_links="yes", serie_prefix="<br /><strong>Series: </strong>", separator="; "):
    """
    Print series and volumes

    @param print_links Prints HTML links if "yes"
    @param serie_prefix A prefix printed before each serie
    @param separator a separator between series
    """
    out = []

    series = bfo.fields('490')
    for serie in series:
        serie_out = ""
        if serie.has_key('a'):
           serie_out += serie_prefix
           if print_links.lower() == "yes":
               serie_out += '<a href="http://cdsweb.cern.ch/search?f=490__a&p=' + \
                            serie['a'].replace(' ', '+') + '"' + \
                            cgi.escape(serie['a']) + '</a>'
           else:
               serie_out += cgi.escape(serie['a'])

        if serie.has_key('v'):
            serie_out += ', ' + serie['v']
        if serie_out:
            out.append(serie_out)

    return separator.join(out)
