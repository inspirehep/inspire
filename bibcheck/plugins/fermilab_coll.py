# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2018 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Add 980__a:Fermilab to HEP records with a Fermilab report number
"""

def check_records(records):
    for record in records:
        in_coll = False
        has_rn = False
        for (tag, _, _), value in record.iterfields(['037__a', '037__z', '980__a']):
            if tag[0:5] == '037__' and 'fermilab' in value.lower():
                has_rn = True
            if tag == '980__a' and value == 'Fermilab':
                in_coll = True
        if has_rn and not in_coll:
            record.add_field('980__', '', subfields=[('a', 'Fermilab')])
