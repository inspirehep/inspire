# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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
Add 980__a:USEFUL to HepNames that contains actual valuable information.

That is they have some fields than: 001, 005, 100__a,q,g, 670__a different than
eprint, 909C0%, 961__%, 970__%, 980__%, more than one 371__a, 65017
"""

def is_records_useful(record):
    tag_371__a_already_found = False
    for (tag, dummy, dummy), value in record.iterfields(["%%%%%%", "%%%%%_"]):
        if not value.strip():
            continue
        if tag in ('001___', '005___', '100__a', '100__q', '100__g', '371__z'):
            continue
        if tag[:5] in ('909CO', '961__', '970__', '980__', '65017'):
            continue
        if tag == '371__a':
            if tag_371__a_already_found:
                return True
            tag_371__a_already_found = True
            continue
        if tag == '670__a' and value == 'eprint':
            continue
        return True
    return False


def check_records(records):
    for record in records:
        if is_records_useful(record):
            record.add_field('980__', '', subfields=[('a', 'USEFUL')])

