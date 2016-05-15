# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2016 CERN.
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
"""BibFormat element - Prints report numbers"""

import cgi
from invenio.urlutils import create_html_link


def format_element(bfo, separator=', ', limit='9999', extension=" etc.", just_one='no'):
    """
    Print the report numbers of the record (037__a and 088__a)

    Call get_report_numbers_formatted to do the heavy lifting so that it can
    be re-used inside other BFEs easily.  Retaining the magic function
    format_element is still handy for magic parameters, e.g., prefix, suffix
    and friends.
    """
    just_one = just_one == 'yes'
    return get_report_numbers_formatted(bfo, separator, limit, extension,
           skip=['arXiv'], just_one=just_one)


def get_report_numbers_formatted(bfo, separator, limit, extension=" etc.", skip=None, just_one=False, prefix='', suffix=''):
    """
    Prints the report numbers of the record (037__a and 088__a)

    @param separator: the separator between report numbers.
    @param limit: the max number of report numbers to print
    @param extension: a prefix printed when limit param is reached
    @param skip: list or string of report-number patterns to NOT print
    """
    out = []

    if type(skip) == str:
        skip = [skip]

    def _skippable(value):
        if skip:
            for keyword in skip:
                if keyword.lower() in value.get('a', '').lower() or \
                   value.get('9', '').lower() == keyword.lower():
                    return True
        if value.get('a', '').lower().startswith("fermilab") and \
           bfo.field("710__g").lower() in ('atlas collaboration', 'cms collaboration'):
            return True

    numbers = bfo.fields("037__")
    numbers.extend(bfo.fields("088__"))

    # Only display the first one
    if just_one:
        numbers = numbers[:1]

    for x in numbers:
        if _skippable(x):
            continue
        if 'a' in x:
            out.append(x['a'])

    if not out:
        return

    if limit.isdigit() and int(limit) <= len(out):
        return prefix + separator.join(out[:int(limit)]) + extension + suffix
    else:
        return prefix + separator.join(out) + suffix

def build_report_number_link(report_number, link_p=True):
    """
    Build HTML link out of given report number when it make sense (or
    is possible) and/or escape report number.
    @param report_number: the report number to consider
    @param link_p: if True, build link, otherwise just escape
    """
    if link_p and report_number.lower().startswith('arxiv:'):
        return create_html_link('http://arxiv.org/abs/' + report_number,
                                urlargd={}, link_label=report_number)
    else:
        return cgi.escape(report_number)

# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
