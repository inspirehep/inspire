#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2016 CERN, SLAC.
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

""" Bibcheck plugin updating recids in 999C50 which point to superseeded records
    (deleted records) with the superseeding recid
"""


from invenio.search_engine import get_fieldvalues, search_pattern


def superseeded_recids_cache(cache={}):
    """ return intbitset of recids which are marked superseeded """
    if 'superseeded' not in cache:
        cache['superseeded'] = search_pattern(p='^[0-9]+$', f='970__d', m='r')
    return cache['superseeded']


def check_record(record):
    """ replace old ids in 999C50 with superseeding ids """

    for pos, val in record.iterfield('999C50'):
        if val:
            try:
                val = int(val)
            except ValueError:
                record.warn("invalid non-digit id in %r" % (pos,))
                continue

            if val in superseeded_recids_cache():
                newrecs = set(get_fieldvalues(val, '970__d'))
                if len(newrecs) == 1:
                    newid = newrecs.pop()
                    try:
                        int(newid)
                    except ValueError:
                        record.warn("non digit value in 970__d for %r" % (pos,))
                        continue
                    record.amend_field(pos, newid, "replaced %s with %s" % (val, newid))

                elif len(newrecs) > 1:
                    record.warn("more than one 970__d for %r" % (pos,))
