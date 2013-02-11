# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
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
"""BibFormat element - Prints all the publication information in one go

LaTeX formats require some elements to be displayed differently depending on
whether other elements were present or not.  It wasn't obvious how to do that
in the Invenio templating system, so this format element is a facade for
those others and handles the decision logic.
"""

from invenio.bibrank_citation_searcher import get_one_cited_by_weight
from invenio.bibrank_tag_based_indexer import get_lastupdated


def format_element(bfo):
    """Returns how many times record was cited. If 0, returns nothing
    @param bfo BFO to extract data from
    """

    citations = ''
    try:
        times_cited = get_one_cited_by_weight(bfo.recID)
        if times_cited != 0:
            citations = '%d citations counted in INSPIRE as of %s' % (get_one_cited_by_weight(bfo.recID), get_lastupdated('citation').strftime("%d %b %Y"))
    except:
        pass
    return citations

# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
