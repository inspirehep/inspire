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
Move additional texkeys from $$a to $$z 
"""
def check_record(record):
    """
    Move additional texkeys from $$a to $$z 
    """
    from invenio.bibrecord import record_modify_subfield
    message = ""
    all_a_keys = list(record.iterfield_filter("035__a", "9", "SPIRESTeX")) \
               + list(record.iterfield_filter("035__a", "9", "INSPIRETeX"))

    if len(all_a_keys)>1:
        message = "Move additional TexKeys from a to z:"
        for this_key in all_a_keys[:-1]:
            message = "%s %s" % (message, this_key[1])
            record_modify_subfield(record, "035", "z", this_key[1], 
                this_key[0][2], field_position_local=this_key[0][1])
            record.set_amended(message)
