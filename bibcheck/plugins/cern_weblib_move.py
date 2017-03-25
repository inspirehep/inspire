#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015, 2016 CERN.
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

""" Bibcheck plugin to take URLs with KEK identifiers from 8564_u marked
    with 8564_y:KEKSCAN, store the identifiers in 035__a with 035__9:KEKSCAN (if
    not yet present) and delete the corresponding tag 856
"""

import re

from invenio.bibrecord import record_add_field, record_get_field_values

provenance = 'CERNREP'
weblibre = re.compile(r'^https?://weblib.cern.ch/abstract\?([^\d][\w-]*)$')


def check_record(record):
    """ get report numbers from weblib links and remove those links"""
    delcount = 0
    report_nums = set()
    for report_number in record_get_field_values(
            record, '037', code='a'):
        report_nums.add(report_number)
    for pos, val in record.iterfield('8564_u',
                                     subfield_filter=('y', provenance)):
        if val:
            weblibmatch = weblibre.match(val)
            if weblibmatch:
                report_number = weblibmatch.group(1)
                # only add new non-empty report numbers
                if report_number != '' and report_number not in report_nums:
                    report_nums.add(report_number)
                    subfields_to_add = ('a', report_number),
                    record_add_field(record, tag='037', ind1='_', ind2='_',
                                     subfields=subfields_to_add)
                record.delete_field((pos[0][0:3], pos[1] - delcount, None))
                delcount += 1
                record.set_amended(
                    "(re)moved weblib link for %s:%s" % (provenance, report_number))
            else:
                record.warn('no match for [%s]' % val)
