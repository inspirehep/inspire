# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015 CERN.
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

"""BibFormat element - Prints INSPIRE Conference Date or Date Range
                       suitable for use in citations
"""

import re

MONTH = {'01': 'January',
         '02': 'February',
         '03': 'March',
         '04': 'April',
         '05': 'May',
         '06': 'June',
         '07': 'July',
         '08': 'August',
         '09': 'September',
         '10': 'October',
         '11': 'November',
         '12': 'December'}

# FIXME: requires python 2.7
# SHORTMONTH = {m[:3]: m for m in MONTH.values()}

SHORTMONTH = {}
for m in MONTH.values():
    SHORTMONTH[m[:3]] = m

monre = re.compile(r'\b(%s)\b' % '|'.join(SHORTMONTH.keys()))


def short2long(matchobj):
    """
    return the full name of a month for 3 characer abbreviation
    matchobj is the regular expression macth object
    """
    return SHORTMONTH.get(matchobj.group(0))


def format_element(bfo, separator='-'):
    """
    return string containing conference date formatted for citation
    or empty string
    """

    date = bfo.field('111__d')
    if date:
        date = date.rstrip()
        date = date.lstrip()

        date = monre.sub(short2long, date)

        # convert to "Month Day, Year" form
        date = re.sub(r'^([0-9 -]+)\s+([a-zA-Z]+),?\s+([0-9]+)$',
                      r'\2 \1, \3',
                      date)
        # convert range with common Year, e.g.
        # '24 August, 27 September 2013'
        # '24 August - 27 September 2013'
        # => 'August 24-September 27, 2013'
        date = re.sub((r'^([0-9]+)\s+([a-zA-Z]+)'
                       r'\s*\W\s*'
                       r'([0-9]+)\s+([a-zA-Z]+)'
                       r',?\s+([0-9]+)$'),
                      r'\2 \1-\4 \3, \5',
                      date)

        return date

    # start and end date should be "YYYY-MM-DD"
    fdate = bfo.field('111__x')
    if fdate:
        fdate = fdate.rstrip()
        try:
            fyear, fmonth, fday = fdate.split('-')
        except ValueError:
            date = fdate
            fdate = None

        # get enddate if there is a startdate
        ldate = bfo.field('111__y')
        if ldate:
            ldate = ldate.rstrip()
            try:
                lyear, lmonth, lday = ldate.split('-')
            except ValueError:
                ldate = None

    if fdate:
        date = '%s %s, %s' % (MONTH.get(fmonth, ''),
                              fday.lstrip('0'),
                              fyear)
        if ldate and (fday != lday or fmonth != lmonth):
            start = '%s %s' % (MONTH.get(fmonth, ''),
                               fday.lstrip('0'))
            end = '%s, %s' % (lday.lstrip('0'), lyear)

            if fmonth != lmonth:
                end = '%s %s' % (MONTH.get(lmonth, ''), end)
            if fyear != lyear:
                start = ' %s, %s' % (start, fyear)

            date = '%s%s%s' % (start, separator, end)

    return date


# pylint: disable=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable=W0613
