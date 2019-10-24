# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013, 2019 CERN.
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
"""Bibcheck plugin to convert institution IDs from GRID to ROR."""

import json
import sys

from invenio.bibsched import write_message

GRID_TO_ROR_PATH = '/opt/cds-invenio/var/data/grid_to_ror.json'

try:
    with open(GRID_TO_ROR_PATH) as f:
        grid_to_ror = json.load(f)
except IOError:
    grid_to_ror = {}
    write_message(
        "Can't convert GRIDs to RORs, couldn't read mapping at '%s'" % GRID_TO_ROR_PATH,
        stream=sys.stderr
    )
except ValueError:
    grid_to_ror = {}
    write_message(
        "Can't convert GRIDs to RORs, invalid data in '%s'" % GRID_TO_ROR_PATH,
        stream=sys.stderr
    )

def check_record(record):
    rors_in_record = set(ror for (_, ror) in record.iterfield('035__a', ('9', 'ROR')))
    for _, grid in record.iterfield('035__a', ('9', 'GRID')):
        ror = grid_to_ror.get(grid)
        if not ror:
            record.warn('No ROR found for {0}'.format(grid))
            continue
        if ror in rors_in_record:
            continue
        record.add_field('035__', '', [('9', 'ROR'), ('a', ror)])
        record.add_field('595__', '', [('a', '{0} from {1}'.format(ror, grid))])
