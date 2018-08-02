#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2018 CERN.
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


from collections import defaultdict


def check_record(record):
    """
    remove standalone duplicate report numbers, i.e. those with
    no other subfields than '037__a'
    """

    repnos = defaultdict(list)
    otherfieldnums = set()

    for pos, val in record.iterfield('037__%'):
        if pos[0] == '037__a':
            repnos[val].append(pos[1])
        else:
            otherfieldnums.add(pos[1])

    todelete = []

    for fieldnums in repnos.values():
        numdups = len(fieldnums) - 1
        if numdups > 0:
            for p in fieldnums:
                if p not in otherfieldnums:
                    todelete.append(p)
                    numdups -= 1
                if numdups <= 0:
                    break

    # remove in reverse order to avoid shift in pos
    for p in sorted(todelete, reverse=True):
        record.delete_field(('037__a', p, None), "deleting standalone field {0}: {1}".format(
            p, [r for r in repnos if p in repnos[r]]))
