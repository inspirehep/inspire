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
Expand single letter subjects - get mapping from KB
"""
from invenio.bibknowledge import get_kb_mappings
from invenio.config import CFG_BIBEDIT_KB_SUBJECTS
subjects = {}
for item in get_kb_mappings(kb_name=CFG_BIBEDIT_KB_SUBJECTS):
    subjects[item['key']] = item['value']

def check_record(record):
    """
    Expand single letter subjects
    """
    for position, value in record.iterfield("65017a", ("2", "INSPIRE")):
        if len(value) == 1:
            if subjects.has_key(value):
                record.amend_field(position[:3], subjects[value])
            else:
                record.warn('single letter subject without mapping: %s' % value)
