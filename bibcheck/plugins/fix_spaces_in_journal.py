# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2016 CERN.
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

"""To amend JINST (and other journal) article IDs in references"""

import re

from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances
from invenio.search_engine import perform_request_search

def check_records(records, field):
    for record in records:
        if field != '999C5s':
            for position, value in record.iterfields([field]):
                newval = value.replace('. ', '.')
                if newval != value:
                    record.amend_field(position, newval)
            continue
        for afield in record_get_field_instances(record, '999', 'C', '5'):
            subfields = field_get_subfield_instances(afield)
            subfields_dict = dict(subfields)
            if  's'in subfields_dict:
                old_pubnote = subfields_dict['s']
                new_pubnote = old_pubnote.replace('. ', '.')
                if old_pubnote != new_pubnote:
                    subfields.remove(('s', old_pubnote))
                    subfields.append(('s', new_pubnote))
                    if not '0' in subfields_dict:
                        recids = perform_request_search(p=new_pubnote, f='journal')
                        if len(recids) == 1:
                            recid = recids.pop()
                            subfields.append(('0', str(recid)))
                            record.set_amended("Pubnote changed from %s to %s and matched a new record %s: Sam is the best, HURRAY!!!" % (old_pubnote, new_pubnote, recid))
                            continue
                    record.set_amended("Pubnote changed from %s to %s" % (old_pubnote, new_pubnote))
