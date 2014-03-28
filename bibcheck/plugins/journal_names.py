#!/usr/bin/env python
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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

from invenio.bibcheck_task import AmendableRecord
from invenio.refextract_kbs import get_kbs


def check_records(records):
    """ Bibcheck plugin to check if the journal names are in
        Inspires short form and if the field 999C5s is in
        the form jnl,vol,page """
    journals = get_kbs()['journals'][1].values()
    for record in records:
        for position, value in record.iterfield('999C5s'):
            values = value.split(',')
            name = values[0]
            if len(values) != 3:
                record.set_invalid('value in field 999C5s is not in the form jnl,vol,page')
            if name not in journals:
                record.set_invalid('value in field 999C5s: %s not a valid journal short name' % name)
        for position, value in record.iterfield('773__p'):
            if value not in journals:
                record.set_invalid('value in field 773__p: %s not a valid journal short name' % value)
