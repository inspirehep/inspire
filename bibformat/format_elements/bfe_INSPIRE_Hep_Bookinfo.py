# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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
"""BibFormat element - Prints authors
"""

def format_element(bfo, limit, separator='',
           extension='[...]',
           print_links="yes",
           print_affiliations='yes',
           affiliation_prefix=' (',
           affiliation_suffix=')',
           interactive="no",
           highlight="no",
           link_author_pages="no"):
    """
    Prints the list of authors of a record.

    @param limit: the maximum number of authors to display
    @param separator: the separator between authors.
    @param extension: a text printed if more authors than 'limit' exist
    @param print_links: if yes, prints the authors as HTML link to their publications
    @param print_affiliations: if yes, make each author name followed by its affiliation
    @param affiliation_prefix: prefix printed before each affiliation
    @param affiliation_suffix: suffix printed after each affiliation
    @param interactive: if yes, enable user to show/hide authors when there are too many (html + javascript)
    @param highlight: highlights authors corresponding to search query if set to 'yes'
    """
    authors = bfo.fields('773__')

    # Process authors to add link, highlight and format affiliation
    output = ""
    cell = "<tr><td>"
#'<a href="/search?ln=en&cc=Institutions&ln=en&cc=Institutions&p=110__u%3A%22' + author'a']  '%22&action_search=Search&sf=&so=d&rm=&rg=25&sc=0&of=hd">'
    for author in authors:
        if author.has_key('x'):
            output += '<table><tr><td>' + author['x'] + '</td></tr></table>'
#            output += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (author['a'], author['r'], author['s'], author['t'])

    return output
    # Uncomment next line if default value must be returned
    # return 'whatever'

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
