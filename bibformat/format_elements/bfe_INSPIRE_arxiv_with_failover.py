# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011 CERN.
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
"""BibFormat element - Return the arxiv id, or failover smartly

If arxiv ID (eprint) isn't available, prefer report number, or barring that,
return the INSPIRE recid for the record.
"""


from invenio.bibformat_elements.bfe_INSPIRE_arxiv import get_arxiv


def format_element(bfo):
    # Return arxiv ID if its available
    out = get_arxiv(bfo, category="no")
    if out:
        return out[0]

    # No arxiv id?  How about a report number?
    # Cf. bfe_report_numbers
    out = bfo.fields("037__a")
    out.extend(bfo.fields("088__a"))
    if out:
        return out[0]
        
    # No arxiv id and no report number.  Fail to recid
    return bfo.recID


# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
