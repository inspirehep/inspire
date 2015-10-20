## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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

"""Corrects all dates!"""

from invenio.dateutils import strftime, strptime

## List of MARC fields from where to read dates.
CFG_DEFAULT_DATE_FIELDS = ("260__c", "269__c", "542__g", "502__d", "773__y", "111__x", "111__y", "046__%", "371__s", "371__t", "999C5y")
CFG_POSSIBLE_DATE_FORMATS_ONLY_YEAR = ("%Y", "%y")
CFG_POSSIBLE_DATE_FORMATS_ONLY_YEAR_MONTH = ("%Y-%m", "%Y %b", "%b %Y", "%Y %B", "%B %Y", "%y-%m", "%y %b", "%b %y", "%y %B", "%B %y")
CFG_POSSIBLE_DATE_FORMATS = ("%Y-%m-%d", "%d %m %Y", "%x", "%d %b %Y", "%d %B %Y", "%d %b %y", "%d %B %y")
CFG_ONLY_YEAR_FIELDS = ("773__y", "999C5y", "542__g", "371__t", "371__s")


def check_records(records, date_fields=CFG_DEFAULT_DATE_FIELDS):
    """Corrects all dates!"""
    for record in records:
        for position, value in record.iterfields(date_fields):
            for date_format in CFG_POSSIBLE_DATE_FORMATS:
                try:
                    parsed_date = strftime("%Y-%m-%d", (strptime(value, date_format)))
                    if position[0] in CFG_ONLY_YEAR_FIELDS:
                        parsed_date = parsed_date[:4]
                    if parsed_date != value:
                        record.amend_field(position, parsed_date)
                    break
                except ValueError:
                    pass
            else:
                for date_format in CFG_POSSIBLE_DATE_FORMATS_ONLY_YEAR_MONTH:
                    try:
                        parsed_date = strftime("%Y-%m", (strptime(value, date_format)))
                        if position[0] in CFG_ONLY_YEAR_FIELDS:
                            parsed_date = parsed_date[:4]
                        if parsed_date != value:
                            record.amend_field(position, parsed_date)
                        break
                    except ValueError:
                        pass
                else:
                    for date_format in CFG_POSSIBLE_DATE_FORMATS_ONLY_YEAR:
                        try:
                            parsed_date = strftime("%Y", (strptime(value, date_format)))
                            if parsed_date != value:
                                record.amend_field(position, parsed_date)
                            break
                        except ValueError:
                            pass
                    else:
                        record.set_invalid("Cannot recognize date %s in position %s" % (value, position))
