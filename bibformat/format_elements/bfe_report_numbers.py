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
"""BibFormat element - Prints report numbers"""


def format_element(bfo, separator=',', limit='9999', extension=" etc."):
    """
    Print the report numbers of the record (037__a and 088__a)

    Call get_report_numbers_formatted to do the heavy lifting so that it can
    be re-used inside other BFEs easily.  Retaining the magic function
    format_element is still handy for magic parameters, e.g., prefix, suffix
    and friends.
    """
    return get_report_numbers_formatted(bfo, separator, limit, extension)


def get_report_numbers_formatted(bfo, separator, limit, extension=" etc."):
    """
    Prints the report numbers of the record (037__a)

    @param separator the separator between report numbers.
    @param limit the max number of report numbers to print
    @param extension a prefix printed when limit param is reached
    """

    report_numbers = bfo.fields("037__")
    numbers = []
    for report_number_datafield in report_numbers:
        # We dont want arXiv numbers in there
        if '9' in report_number_datafield and report_number_datafield['9'].lower() == 'arxiv':
            continue
        numbers.append(report_number_datafield['a'])
    if limit.isdigit() and int(limit) <= len(numbers):
        return separator.join(numbers[:int(limit)]) + extension
    else:
        return separator.join(numbers)


# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
