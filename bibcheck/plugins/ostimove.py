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

""" Bibcheck plugin to take URLs with OSTI identifiers from 8564_u marked
    with 8564_y:OSTI, store the identifiers in 035__a with 035__9:OSTI
    and delete the corresponding tag 856
"""

import re

from invenio.bibrecord import record_add_field

provenance = 'OSTI'

ostiidre = re.compile(r'^https?://www\.osti\.gov/.*?\D(\d+)$')



def check_record(record):
    """ move 8564_u/y to 035__a/9 """
    delcount = 0
    ostiids = set()
    for pos, val in record.iterfield('8564_u',
                                     subfield_filter=('y', provenance)):
        if val:
            ostiidmatch = ostiidre.match(val)
            if ostiidmatch:
                ostiid = ostiidmatch.group(1)
                if ostiid in ostiids:
                    continue
                else:
                    ostiids.add(ostiid)
                subfields_to_add = (('9', 'OSTI'),
                                    ('a', ostiid))
                record_add_field(record, tag='035', ind1='_', ind2='_',
                                 subfields=subfields_to_add)
                record.delete_field((pos[0][0:3], pos[1] - delcount, None))
                delcount += 1
                record.set_amended(
                    "moved link for %s:%s" % (provenance, ostiid))
            else:
                record.warn('no match for [%s]' % val)

