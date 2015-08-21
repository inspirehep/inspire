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

"""To amend JINST (and other journal) article IDs in references"""

import re

from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances

RE_BROKEN_PUBNOTES = re.compile(r'(?P<journal>JINST|J\.Stat\.Mech\.|J\.Phys\.Math\.),(?P<volume>.*),(?P<id>\d{5}\d*)')

def check_records(records):
    from invenio.bibrank import ConfigParser, CFG_ETCDIR
    from invenio.bibrank_citation_indexer import get_recids_matching_query
    config = ConfigParser.ConfigParser()
    config.read("%s/bibrank/%s.cfg" % (CFG_ETCDIR, "citation"))
    for record in records:
        for field in record_get_field_instances(record, '999', 'C', '5'):
            subfields = field_get_subfield_instances(field)
            subfields_dict = dict(subfields)
            if '0' not in subfields_dict and 's' in subfields_dict:
                old_pubnote = subfields_dict['s']
                g = RE_BROKEN_PUBNOTES.match(old_pubnote)
                if g:
                    new_pubnote = '%(journal)s,%(volume)s,P%(id)s' % g.groupdict()
                    subfields.remove(('s', old_pubnote))
                    subfields.append(('s', new_pubnote))
                    recids = get_recids_matching_query(p=new_pubnote,
                                                    f='journal',
                                                    config=config)
                    if len(recids) == 1:
                        recid = recids.pop()
                        subfields.append(('0', str(recid)))
                        record.set_amended("Pubnote changed from %s to %s and matched a new record %s: Sam is the best, HURRAY!!!" % (old_pubnote, new_pubnote, recid))
                    else:
                        record.set_amended("Pubnote changed from %s to %s" % (old_pubnote, new_pubnote))

