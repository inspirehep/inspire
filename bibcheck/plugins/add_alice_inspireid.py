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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""BibCheck plugin to add missing INSPIRE IDs to ALICE records"""

import re

from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances

# NOTE: restart the rule in case the following list is amended.
CHANGES = {
    "Ahmad, Shakeel": "INSPIRE-00560210",
    "Silva De Albuquerque, Danilo": "INSPIRE-00560229",
    "Cabala, Jan": "INSPIRE-00560262",
    "Danisch, Meike Charlotte": "INSPIRE-00560270",
    "Sanchez Gonzalez, Andres": "INSPIRE-00560286",
    "Hellbar, Ernst": "INSPIRE-00560290",
    "Kostarakis, Panagiotis": "INSPIRE-00560306",
    "Lapidus, Kirill": "INSPIRE-00560319",
    "Lehner, Sebastian": "INSPIRE-00560343",
    "Saarinen, Sampo": "INSPIRE-00560357",
    "Sadhu, Samrangy": "INSPIRE-00560369",
    "Sarkar, Nachiketa": "INSPIRE-00560376",
    "Schmidt, Martin": "INSPIRE-00560380",
    "Sheikh, Ashik Ikbal": "INSPIRE-00560398",
    "Sumowidagdo, Suharyo": "INSPIRE-00129750",
    "Thakur, Dhananjaya": "INSPIRE-00560404",
    "Tikhonov, Anatoly": "INSPIRE-00560412",
    "Vazquez Doce, Oton": "INSPIRE-00560426"}


def check_records(records):
    for record in records:
        for field in record_get_field_instances(record, '100') + record_get_field_instances(record, '700'):
            subfields = field_get_subfield_instances(field)
            subfields_dict = dict(subfields)
            if 'a' in subfields_dict and subfields_dict['a'] in CHANGES:
                if 'i' in subfields_dict and subfields_dict['i'] != CHANGES[subfields_dict['a']]:
                    record.set_invalid("Author %s should have INSPIRE ID %s but has already INSPIRE ID %s" % (subfields_dict['a'], CHANGES[subfields_dict['a']], subfields_dict['i']))
                elif not 'i' in subfields_dict:
                    subfields.append(('i', CHANGES[subfields_dict['a']]))
                    record.set_amended("Added INSPIRE ID %s to author %s" % (CHANGES[subfields_dict['a']], subfields_dict['a']))
