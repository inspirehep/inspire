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
Checking records in journals collection
exactly one full name (130__a)
exactly one short name (711__a)
all full names, short names and name variants (730__a) are unique
"""
from invenio.search_engine import perform_request_search
def searchforotherjournal(name, recid):
    """Search INSPIRE for other journals with name."""
    pattern = '130__a:"%s" or 730__a:"%s" or 711__a:"%s"' % (name, name, name)
    result = perform_request_search(req=None, cc='Journals', p=pattern)
    try:
        result.remove(int(recid))
    except ValueError:
        pass  #not indexed yet??
    return result
def check_record(record):
    """
    Checking journal names
    """
    recid = record['001'][0][3]

    full_names = []
    short_names = []
    for pos, value in record.iterfield('130__a'):
        full_names.append(value)
    for pos, value in record.iterfield('711__a'):
        short_names.append(value)

# exactly one full_name and short name
    if not len(full_names) == 1:
        record.set_invalid('Number of jounal names: %s. ' % len(full_names))
    if not len(short_names) == 1:
        record.set_invalid('Number of jounal short names: %s. ' % len(short_names))

    all_names = []
# are the names unique?
    for name in full_names:
        all_names.append(name.upper())
        result = searchforotherjournal(name, recid)
        if result:
            record.set_invalid('Full name "%s" exists in other record %s. ' % (name, result))
    for name in short_names:
        all_names.append(name.upper())
        result = searchforotherjournal(name, recid)
        if result:
            record.set_invalid('Short name "%s" exists in other record %s. ' % (name, result))

    for pos, name in reversed(list(record.iterfield('730__a'))):
        if name.upper() in all_names:
# avoid adding variants multiple times
            record.delete_field(pos, 'deleting already existing variant: "%s"' % name)
        else:
            all_names.append(name.upper())
            result = searchforotherjournal(name, recid)
            if result:
                record.set_invalid('Name variant "%s" exists in other record %s. ' % (name, result))
