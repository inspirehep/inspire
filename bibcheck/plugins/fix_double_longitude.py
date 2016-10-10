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

"""Amend institution records with no latitude and two longitudes.

Some institution records have no latitude and two longitudes.
This plugin fixes this data issue by deleting the longitudes
and assigning a new latitude/longitude pair using the Google
Maps geocoding API.

We expect to run this plugin only once; moreover, we expect
to call the Google Maps API at most a couple hundred times,
well under the limit of a thousand requests per day.
"""

import os

import googlemaps

from invenio.config import CFG_GOOGLE_MAPS_API_KEY
from invenio.bibrecord import record_get_field_value, record_get_field_values


GMAPS = googlemaps.Client(key=CFG_GOOGLE_MAPS_API_KEY)


def geocode(record):
    """Uses the Google Maps API to geocode an institution."""
    def _get_approximate_address(record):
        city = record_get_field_value(record, '371', code="b")
        zipcode = record_get_field_value(record, '371', code="e")
        country = record_get_field_value(record, '371', code="d")
        address = [value for value in record_get_field_values(record, '371', code='a') if zipcode not in value]
        address.extend([city, zipcode, country])
        return [elem for elem in address if elem]

    approximate_address = _get_approximate_address(record)
    while approximate_address:
        response = GMAPS.geocode(', '.join(approximate_address))
        if response:
            location = response[0]['geometry']['location']
            return location['lat'], location['lng']
        # Progressively making the address more approximate
        approximate_address = approximate_address[1:]

    return None, None


def check_record(record):
    def _has_no_latitude(record):
        return len(list(record.iterfield('034__f'))) == 0

    def _has_two_longitudes(record):
        return len(list(record.iterfield('034__d'))) == 2

    def _delete_longitudes(record):
        for pos, _ in record.iterfield('034__d'):
            record.delete_field(pos)

    def _add_latitude_and_longitude(record, latitude, longitude):
        subfields = [('f', str(latitude)), ('d', str(longitude))]
        record.add_field('034__', '', subfields=subfields)

    if _has_no_latitude(record) and _has_two_longitudes(record):
        _delete_longitudes(record)

        latitude, longitude = geocode(record)
        if latitude and longitude:
            _add_latitude_and_longitude(record, latitude, longitude)
