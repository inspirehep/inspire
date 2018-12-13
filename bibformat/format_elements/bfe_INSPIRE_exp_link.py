# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2018 CERN.
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
"""BibFormat element - Prints HTML link to exp
"""


def format_element(bfo, separator=', ', link="yes"):
    """
    Prints experiment info as best is possible.

    @param link if yes (default) prints link to INSPIRE experiment info
    @param separator  separates multiple experiments

    """

    experiments = bfo.fields('693__e')

    # Process authors to add link, highlight and format affiliation

    output = []

    for exp in experiments:
        if ' ' in exp:
            qexp = "%22{0}%22".format(exp)
        else:
            qexp = exp
        output.append('<a href="/search?cc=Experiments&amp;p=119__a%3A' + qexp
                      + '&amp;of=hd">' + exp + '</a>')

    return separator.join(output)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
