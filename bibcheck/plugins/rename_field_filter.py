# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013, 2016 CERN.
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

"""
Bibcheck plugin to move (rename) a field
depending on subfield_filter

Example:
[mv_PACS]
check = rename_field_filter
filter_collection = HEP
check.source_field = "6507_"
check.new_field = "084__"
check.subfield_filter = ["2", "PACS"]
"""

def check_record(record, source_field, new_field, subfield_filter):
    """ Changes the code of a field to new_field """
    from collections import namedtuple
    from invenio.bibrecord import (record_add_field, record_delete_field,
                                   record_get_field_instances)

    assert len(source_field) == 5
    assert len(new_field) == 5
    source_field = source_field.replace("_", " ")
    new_field = new_field.replace("_", " ")

    assert len(subfield_filter) == 2
    SubfieldFilter = namedtuple('SubfieldFilter', ['code', 'value'])
    subfield_filter = SubfieldFilter(*subfield_filter)

    def filter_passes(subfield_code, result):
        return subfield_filter.code is None or (
            subfield_filter.code in ('%', subfield_code) and
            subfield_filter.value == result)

    subfields_list = []
    for subfields, ind1, ind2, _, pos in record_get_field_instances(
            record, source_field[:3], source_field[3], source_field[4]):
        if any(filter_passes(*s) for s in subfields):
            subfields_list.append(subfields)
            record_delete_field(record, source_field[:3], ind1, ind2, pos)

    for subfields in subfields_list:
        record_add_field(record, new_field[:3], new_field[3], new_field[4],
                         subfields=subfields)
        record.set_amended('move from %s to %s: %s' %
                           (source_field.replace(" ", "_"),
                            new_field.replace(" ", "_"), subfields))

