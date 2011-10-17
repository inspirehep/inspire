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
"""BibFormat element - Prints job deadline date
"""

import time
import datetime
from invenio.dateutils import convert_datestruct_to_datetext

__revision__ = "$Id$"

def format_element(bfo, warnings="0000=EXPIRED,8888=OPEN UNTIL FILLED,9999=ALWAYS OPEN"):
    """
    Prints the deadline date for an INSPIRE Job record.

    If the deadline is passed a warning will be displayed. The
    same warning will be displayed if certain patterns are matched.

    @param bfo: BibFormatObject for current record
    @type nfo: object

    @param warnings: specially formatted string of patterns which maps a certain date-code
        to a warning which is displayed if date is equal to the code. 
        Syntax: "CODE=MESSAGE,CODE=MESSAGE"
    @type warnings: str

    @return: warning or properly formed ISO date
    @rtype: str
    """
    # Check if any warnings should be displayed instead
    deadline = bfo.field('046__i').strip()
    for warning in warnings.split(","):
        code, message = warning.split("=")
        if deadline == code:
            return message
    # We have these variants: 12/15/11 12/12/2012
    # as well as properly formed ones
    if '/' in deadline:
        format = "%d/%m/%Y %H:%M"
        if len(deadline) == 8:
            # Assume 12/15/11
            format = "%m/%d/%y %H:%M"
        # Add dummy time
        deadline += " 23:59"
        try:
            datestruct = time.strptime(deadline, format)
            date = convert_datestruct_to_datetext(datestruct)
        except ValueError, e:
            # Something went wrong. Do not display date
            return ""
        now = datetime.datetime.now().date().isoformat()
        if date > now:
            return date.split()[0]
        else:
            return "%s (PASSED)" % (date.split()[0],)
    return ""

