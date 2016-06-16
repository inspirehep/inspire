# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" BibCheck plugin to remove a field matching one of patterns """


def check_record(record, fields, patterns=None, subfield_filter=None):
    """
    check if a particular field matches one of the patterns
    and remove the entire MARC tag if it does
    """

    if patterns is None:
        return

    if subfield_filter is None:
        subfield_filter = (None, None)

    for field in fields:
        assert len(field) == 6

        for pos, val in record.iterfield(field, subfield_filter):
            if val in patterns:
                record.delete_field((pos[0][0:3], pos[1], None))
                record.set_amended("removed %s matching %r" %
                                   (field[:3], patterns))
