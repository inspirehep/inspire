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
from operator import itemgetter

def check_records(records):
    for record in records:
        in_coll = False
        has_rn = False
        slidepost = False
        hep = []
        for pos, value in record.iterfields(['037__a', '037__z', '980__a']):
            if pos[0][0:5] == '037__' and 'fermilab' in value.lower():
                has_rn = True
                if 'slides' in value.lower() or 'poster' in value.lower():
                    slidepost = True
            if pos[0] == '980__a':
                if value == 'Fermilab':
                    in_coll = True
                if value == 'HEP':
                    hep.append(pos)
        if slidepost and hep:
            for pos in sorted(hep, key=itemgetter(1, 2), reverse=True):
                    record.delete_field(pos)
        if has_rn and not in_coll:
            record.add_field('980__', '', subfields=[('a', 'Fermilab')])

