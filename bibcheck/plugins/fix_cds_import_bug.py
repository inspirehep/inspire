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
CDS import of Thesis fills 502 $$a, $$b, $$c instead of $$b, $$c, $$d
Move fields if $$c might be a date and $$a is a degree
"""
def check_record(record):
    """ Move 502 $$a, $$b, $$c to $$b, $$c, $$d """
    from invenio.bibrecord import record_modify_subfield

    degrees = ['Laurea', 'Diploma', 'PhD', 'Bachelor', 'Habilitation', 'Thesis', 'Master']
    new_code = {'a':'b', 'b':'c', 'c':'d'}
    message = ""
    tag = '502'
    if not record.has_key(tag):
        return
    for (local_position, field_obj) in enumerate(record[tag]):
        degree_ok = True
        year_ok = False
        mess = ''
        for subfield_code, value in field_obj[0]:
            if subfield_code == 'a' and not value in degrees:
                degree_ok = False
            if subfield_code == 'c':
                try:
                    year = int(value[:4])
                    if year > 1300 and year < 2050:
                        year_ok = True
                except:
                    pass
        if year_ok and degree_ok:
            for subfield_position, subfield_tuple in enumerate(field_obj[0]):
                subfield_code, value = subfield_tuple
                if new_code.has_key(subfield_code):
                    record_modify_subfield(record, tag,
                                           new_code[subfield_code], value,
                                           subfield_position,
                                           field_position_local=local_position)
                    mess = 'Updated %s , ' % record[tag][local_position][0]
        message += mess
    if message:
        record.set_amended(message)
