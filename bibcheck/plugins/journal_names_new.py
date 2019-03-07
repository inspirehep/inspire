# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
Checking records in journals collection
exactly one full name (130__a)
exactly one short name (711__a)
all full names, short names, codens (030__a) and name variants (730__a) are unique
Option sort_variants will sort 730 fields by length.
"""
def normalize_name(name):
    return name.replace('. ', ' ').replace('.', ' ').strip().upper()

def sorted_keys(dd):
    """return keys of a dict sorted by list of values"""
    def by_value(a,b):
        for i in range(len(dd[a])):
            comp = cmp(dd[a][i], dd[b][i])
            if comp != 0:
               return comp
        return comp
    ll = dd.keys()
    ll.sort(cmp=by_value)
    return ll

from invenio.search_engine import get_collection_reclist, get_fieldvalues, get_record
from invenio.bibcheck_task import AmendableRecord

JNAMES = {}
for recid in get_collection_reclist('Journals'):
    for name in set(get_fieldvalues(recid, '711__a') + get_fieldvalues(recid, '130__a')):
        norm_name = normalize_name(name)
        if norm_name in JNAMES:
            if JNAMES[norm_name] != recid: # short and long name can be identical
                record = AmendableRecord(get_record(recid))
                record.set_invalid('Normalized name "%s" (%s) exists in other record %s.' % (norm_name, recid, JNAMES[norm_name]))
        else:
            JNAMES[norm_name] = recid

def searchforothervariant(name, recid):
    """Search INSPIRE for other journals with name variant or CODEN."""
    from invenio.search_engine import perform_request_search

    norm_name = normalize_name(name)

    pattern = '730__a:"%s" or 030__a:"%s"' % (name, name)
    result = perform_request_search(req=None, cc='Journals', p=pattern)
    try:
        result.remove(int(recid))
    except ValueError:
        pass
    return result

def check_record(record, sort_variants=False):
    """
    Checking journal names
    """
    from invenio.bibrecord import record_delete_field
    import copy
    recid = record.record_id

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
    for name in full_names + short_names:
        norm_name = normalize_name(name)
        all_names.append(norm_name)
        result = searchforothervariant(norm_name, recid)
        if result:
            record.set_invalid('Name "%s" exists in other record %s. ' % (name, result))

    # are the codens unique?
    for pos, name in record.iterfield('030__a'):
        if not name in all_names:
            all_names.append(name)
            result = searchforothervariant(name, recid)
            if result:
                record.set_invalid('CODEN "%s" exists in other record %s. ' % (name, result))
            # check codens against all normalized names
            if name in JNAMES and JNAMES[name] != recid:
                record.set_invalid('CODEN "%s" is name of other record %s. ' % (name, JNAMES[name]))


    # are variants unique?
    # list variants only once, delete more fields if no other subfield (e.g. $$b), set_invalid otherwise
    # normalize variants
    # option to sort variants
    if not '730' in record:
       return
    del_fields = []
    sort_index = {}
    for num_f, field in enumerate(record['730']):
        name = ''
        othersubfields = False
        position_name = None
        letter = ' '
        for num_sf, (code, value) in enumerate(field[0]):
            if code == 'a':
                name = value
                position_name = num_sf
            else:
                othersubfields = True
                if code == 'b':
                    letter = value
        if not name:
            record.set_invalid('field 730 without $$a subfield: %s. ' % (field, ))
            sort_variants = False
            continue

        norm_name = normalize_name(name)
        # is it normalized?
        if not name == norm_name:
            record.set_invalid('normalized name variant: "%s" ' % name)
            field[0][position_name] = ('a', norm_name)
        if norm_name in all_names:
            # avoid adding variants multiple times
            if othersubfields:
                # let a human do this
                record.set_invalid('variant is listed twice: "%s" ' % name)
            else:
                record.set_invalid('deleted already existing variant: "%s" ' % name)
                del_fields.append(field[4])
        else:
            all_names.append(norm_name)
            result = searchforothervariant(norm_name, recid)
            if result:
                record.set_invalid('Name variant "%s" exists in other record %s. ' % (norm_name, result))
            # check variants against normalized names
            if norm_name in JNAMES and JNAMES[norm_name] != recid:
                record.set_invalid('Name variant "%s" is name of other record %s. ' % (norm_name, JNAMES[norm_name]))
        if sort_variants:
            # sort by letter ($$b), lenght (longest first), name
            sort_index[num_f] = (letter, len(norm_name)*-1, norm_name)

    if sort_variants:
        m730 = copy.deepcopy(record['730'])
        record['730'] = [m730[num_f] for num_f in sorted_keys(sort_index)]
        if record['730'] != m730:
            record.set_invalid('Name variants sorted. ')

    for position in del_fields:
        record_delete_field(record, '730', field_position_global=position)

    return
