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


GMAPS = googlemaps.Client(key=CFG_GOOGLE_MAPS_API_KEY)


def geocode(record):
    """Uses the Google Maps API to geocode an institution.

    Uses only information about the city the institution is in
    because it's the only one which is reliably there. In fact,
    the queries

        034__d:** and not 034__f:**

    and

        371__b:** and 034__d:** and not 034__f:**

    return the same set of results.
    """
    def _get_approximate_address(record):
        return record.iterfield('371__b')[0]

    approximate_address = _get_approximate_address(record)

    response = GMAPS.geocode(approximate_address)
    if response:
        location = response[0]['geometry']['location']
    else:
        location = {'lat': None, 'lng': None}

    return location['lat'], location['lng']


def check_record(record):
    def _has_no_latitude(record):
        return len(list(record.iterfield('034__f'))) == 0

    def _has_two_longitudes(record):
        return len(list(record.iterfield('034__d'))) == 2

    def _delete_longitudes(record):
        for pos, _ in record.iterfield('034__d'):
            record.delete_field(pos)

    def _add_latitude_and_longitude(record, latitude, longitude):
        subfields = [('f', latitude), ('d', longitude)]
        record.add_field('034__', '', subfields=subfields)

    if _has_no_latitude(record) and _has_two_longitudes(record):
        _delete_longitudes(record)

        latitude, longitude = geocode(record)
        if latitude and longitude:
            _add_latitude_and_longitude(record, latitude, longitude)
