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


""" ensure that 999C5s is standard form """


from invenio.refextract_api import search_from_reference


def check_record(record):
    """
    ensure that 999C5s is in standard form "p,v,c"
    fix if possible, otherwise flag
    """
    for pos, val in record.iterfield('999C5s'):
        if val.count(',') < 2:
            val = val.decode('utf-8')
            field, pubnote = search_from_reference(val)
            if pubnote and field == 'journal':
                if abs(len(pubnote) - len(val)) < 3:
                    record.amend_field(pos, pubnote)
                else:
                    record.warn("fix ref 999C5s: '{0}' ==> '{1}'".format(val, pubnote))
            elif field == 'report':
                record.warn("report number in 999C5s, should move '{0}' ==> '999C5r:{1}'".format(
                    val, pubnote))
            else:
                record.warn("999C5s in non-standard form: '{0}'".format(
                    val))
