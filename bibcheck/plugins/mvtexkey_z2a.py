# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""
Move texkeys from $$z to $$a if there is no $$a
"""
def check_record(record):
    """
    Move texkeys from $$z to $$a if there is no $$a
    """
    from invenio.bibrecord import record_modify_subfield
    message = ""
    all_a_keys = list(record.iterfield_filter("035__a", "9", "SPIRESTeX")) \
               + list(record.iterfield_filter("035__a", "9", "INSPIRETeX"))
    all_z_keys = list(record.iterfield_filter("035__z", "9", "SPIRESTeX")) \
               + list(record.iterfield_filter("035__z", "9", "INSPIRETeX"))

    if all_a_keys:
        pass
    elif all_z_keys:
        position, value = all_z_keys[0]
        message = "Move TexKey from z to a: %s" % value
        record_modify_subfield(record, "035", "a", value,
           position[2], field_position_local=position[1])
        record.set_amended(message)
