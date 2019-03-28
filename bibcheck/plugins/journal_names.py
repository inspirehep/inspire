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
normalized short name is in name variants (730__a)
all codens (030__a) and name variants are unique
Option sort_variants will sort 730 fields by length.
"""
def normalize_name(name):
    """No dots, all-caps"""
    return name.replace('. ', ' ').replace('.', ' ').strip().upper()

def searchforothervariant(name, recid):
    """Search INSPIRE for other journals with name variant."""
    from invenio.search_engine import perform_request_search

    norm_name = normalize_name(name)

    pattern = '730__a:"%s" or 030__a:"%s"' % (norm_name, norm_name)
    result = perform_request_search(req=None, cc='Journals', p=pattern)
    try:
        result.remove(int(recid))
    except ValueError:
        pass
    return result

def check_variants(record, sort_variants):
    """
    are variants unique?
    list variants only once, delete more fields if no other subfield (e.g. $$b), set_invalid otherwise
    normalize variants
    option to sort variants
    """
    from invenio.bibrecord import record_delete_field, record_add_field
    from operator import itemgetter
    import copy

    all_variants = []
    recid = record.record_id

    for field in record['730']:
        # get info for field
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
            record.set_amended('normalized name variant: "%s" ' % name)
            field[0][position_name] = ('a', norm_name)
        if norm_name in all_variants:
            # avoid adding variants multiple times
            if othersubfields:
                # let a human do this
                record.set_invalid('variant is listed twice: "%s" ' % name)
            else:
                record.set_amended('deleted already existing variant: "%s" ' % name)
                record_delete_field(record, '730', field_position_global=field[4])
        else:
            all_variants.append(norm_name)
            result = searchforothervariant(norm_name, recid)
            if result:
                record.set_invalid('Name variant "%s" exists in other record %s. ' % (norm_name, result))

    if sort_variants:
        # sort by letter ($$b), length (longest first), name
        sort_index = {}
        for num_f, field in enumerate(record['730']):
            # get info for field
            name = ''
            letter = ' '
            for code, value in field[0]:
                if code == 'a':
                    name = value
                elif code == 'b':
                    letter = value    
            sort_index[num_f] = (letter, len(name)*-1, name)
        
        m730 = copy.deepcopy(record['730'])
        sorted_keys = [k for k, _ in sorted(sort_index.items(), key=itemgetter(1))]
        m730_sort = [m730[num_f] for num_f in sorted_keys]
        if m730_sort != m730:
            # we have to get rid of global positions to really sort it
            record.set_amended('Name variants sorted. ')
            record_delete_field(record, '730')
            for field in m730_sort:
                record_add_field(record, '730', ind1=' ', ind2=' ', subfields=field[0], controlfield_value='')

    return all_variants

def check_record(record, sort_variants=False):
    """
    Checking journal names
    """
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

    # are the codens unique?
    for pos, name in record.iterfield('030__a'):
        result = searchforothervariant(name, recid)
        if result:
            record.set_invalid('CODEN "%s" exists in other record %s. ' % (name, result))

    if '730' in record:
        all_variants = check_variants(record, sort_variants)
    else:
        all_variants = []

    # normalized short_names should be in name variants
    for name in short_names:
        norm_name = normalize_name(name)
        if not norm_name in all_variants:
            record.add_field('730__a', '', [('a', norm_name),])

    return
