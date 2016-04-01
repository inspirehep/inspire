# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Amend author name split between family name and first name, by looking up into
HepNames
"""

from invenio.search_engine import perform_request_search
from invenio.search_engine_utils import get_fieldvalues

import re

RE_SPACES = re.compile("\s+", re.U)

NAME_CACHE = {}

def check_records(records, amend_case=False):
    for record in records:
        for position, value in record.iterfields(['100__a', '700__a']):
            value = value.decode('utf8')
            new_value = NAME_CACHE.get(value)
            if new_value is None:
                search_value = value
                if ',' in value:
                    splitted_values = search_value.split(',', 1)
                    search_value = u"%s %s" % (splitted_values[1].strip(), splitted_values[0].strip())
                original_family_name = value.split(',')[0].strip()
                search_value = RE_SPACES.sub(' ', search_value).strip()
                if len(search_value.split()) < 3:
                    # Simple name
                    continue
                i = perform_request_search(p=u'author:"%s"' % search_value, cc='HepNames')
                possible_values = get_fieldvalues(i, '100__a', sort=False) + get_fieldvalues(i, '400__a', sort=False)
                for correct_value in possible_values:
                    correct_value = correct_value.decode('utf8')
                    if search_value.lower().endswith(" " + correct_value.lower().split(',')[0]):
                        family_name = correct_value.split(',')[0].strip()
                        if len(family_name) < len(original_family_name):
                            continue
                        first_name = search_value[:-(len(family_name) + 1)].strip()
                        new_value = u'%s, %s' % (family_name, first_name)
                        NAME_CACHE[value] = new_value
                        break
                else:
                    NAME_CACHE[value] = value
            if new_value:
                if amend_case and new_value == value:
                    continue
                elif new_value.lower() == value.lower():
                    continue
                record.amend_field(position, new_value.encode('utf8'))

