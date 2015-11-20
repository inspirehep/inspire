# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""BibCheck plugin to correct wrong INSPIRE IDs in HEP records"""

from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances

def check_records(records):
    """
    Update field 700__i:
        * Replace substring INSPIRE-00227069 with INSPIRE-00341324
          When subfield __a is equal to Yang, Yi AND __u is equal to Beijing,
          Inst. High Energy Phys.
        * Update field 700  ADD subfield __i INSPIRE-00341324 When subfield __a
          is equal to Yang, Yi AND __u is equal to Beijing, Inst. High Energy
          Phys. IF subfield __i Does not exist
    """
    for record in records:
        for field in record_get_field_instances(record, tag="100") + record_get_field_instances(record, "700"):
            subfields = field_get_subfield_instances(field)
            subfields_dict = dict(subfields)
            if subfields_dict.get('a') == 'Yang, Yi' and subfields_dict.get('u') == 'Beijing, Inst. High Energy Phys.':
                if 'i' not in subfields_dict:
                    subfields.append(('i', 'INSPIRE-00341324'))
                    record.set_amended('Added INSPIRE-00341324 to Yang, Yi')
                else:
                    for i, (code, value) in enumerate(subfields):
                        if code == 'i' and 'INSPIRE-00227069' in value:
                            subfields[i] = ('i', 'INSPIRE-00341324')
                            record.set_amended('Corrected INSPIRE-00227069 with INSPIRE-00341324 for Yang, Yi')




