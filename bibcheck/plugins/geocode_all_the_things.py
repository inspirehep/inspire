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

"""Add latitude and longitude to all records that should have them.

Some conference and institution records have no latitude or longitude. This
plugin fixes this data issue by assigning a latitude/longitude pair using the
Google Maps geocoding API.

Some records instead have only one of the two, due to a bug introduced in
commit 9202615. This plugin also fixes this issue using the same solution.
"""

import googlemaps

from invenio.bibrecord import record_get_field_value, record_get_field_values
from invenio.config import CFG_GOOGLE_MAPS_API_KEY


GMAPS = googlemaps.Client(key=CFG_GOOGLE_MAPS_API_KEY)


def geocode(record):
    """Uses the Google Maps API to geocode a record."""
    def _get_approximate_address(record):
        def _is_a_conference(record):
            return record_get_field_values(record, '111', code='c')

        if _is_a_conference(record):
            return record_get_field_value(
                record, '111', code='c').split(', ')
        else:
            city = record_get_field_value(record, '371', code='b')
            zipcode = record_get_field_value(record, '371', code='e')
            country = record_get_field_value(record, '371', code='d')
            addresses = record_get_field_values(record, '371', code='a')

            result = [el for el in addresses if zipcode not in el]
            result.extend([city, zipcode, country])
            result = [el for el in result if el]

            return result

    approximate_address = _get_approximate_address(record)
    while approximate_address:
        response = GMAPS.geocode(', '.join(approximate_address))
        if response:
            location = response[0]['geometry']['location']
            return location['lat'], location['lng']

        approximate_address = approximate_address[1:]

    return None, None


def check_record(record):
    def _has_no_latitude_or_longitude(record):
        return (
            len(list(record.iterfield('034__f'))) == 0 or
            len(list(record.iterfield('034__d'))) == 0)

    def _should_have_them(record):
        return (
            len(list(record.iterfield('111__c'))) or
            len(list(record.iterfield('371__d'))))

    def _add_latitude_and_longitude(record, latitude, longitude):
        subfields = [('f', str(latitude)), ('d', str(longitude))]
        record.add_field('034__', '', subfields=subfields)

    def _remove_all_latitudes_and_longitudes(record):
        if '034' in record:
            del record['034']

    if _has_no_latitude_or_longitude(record) and _should_have_them(record):
        _remove_all_latitudes_and_longitudes(record)

        latitude, longitude = geocode(record)
        if latitude and longitude:
            _add_latitude_and_longitude(record, latitude, longitude)
