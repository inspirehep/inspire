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

provenance = 'KEKSCAN'
kekidre = re.compile(r'^https?://www-lib.kek.jp/cgi-bin/img_index\?(\d{2})?(\d{7})$')


def check_record(record):
    """ move 8564_u/y to 035__a/9 """
    delcount = 0
    kekids = set()
    #  look up IDs already present in 035
    for kekid in record_get_field_values(
            record, '035', code='a',
            filter_subfield_code='9',
            filter_subfield_value=provenance):
        # normalize the ID
        kekids.add(re.sub(r'-', '', kekid))
    for pos, val in record.iterfield('8564_u',
                                     subfield_filter=('y', provenance)):
        if val:
            kekidmatch = kekidre.match(val)
            if kekidmatch:
                kekid = (kekidmatch.group(1) or '') + kekidmatch.group(2)
                if kekid not in kekids:
                    kekids.add(kekid)
                    subfields_to_add = (('9', provenance),
                                        ('a', kekid))
                    record_add_field(record, tag='035', ind1='_', ind2='_',
                                     subfields=subfields_to_add)
                record.delete_field((pos[0][0:3], pos[1] - delcount, None))
                delcount += 1
                record.set_amended(
                    "moved link for %s:%s" % (provenance, kekid))
            else:
                record.warn('no match for [%s]' % val)
    if len(kekids) > 1:
        record.warn('more than 1 KEK id present')

