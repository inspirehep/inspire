#!/usr/bin/env python

##
## This file is part of Invenio.
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

from os.path import exists


AUTHORS = {}


def check_record(record, kb_file=''):
    """Bibcheck plugin to fix author name with a kwoledge base file."""

    if not AUTHORS or not kb_file in AUTHORS:
        if not exists(kb_file):
            return
        else:
            AUTHORS[kb_file] = {}
            with open(kb_file) as input_file:
                for line in input_file:
                    try:
                        key, value = line.split('---')
                        AUTHORS[kb_file][key] = value
                    except ValueError:
                        # wrongly formatted kb line
                        pass

    for position, value in record.iterfields(['100__a', '700__a']):
        if value in AUTHORS[kb_file]:
            value = AUTHORS[kb_file][value]
            record.amend_field(position, value)
