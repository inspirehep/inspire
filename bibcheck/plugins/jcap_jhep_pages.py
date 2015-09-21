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

""" Translate codens into short journal names in citations """

import re

from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances

RE_BROKEN_PUBNOTES = re.compile(r'^(?P<journal>JCAP|JHEP),(?P<volume>.*),(?P<id>\d{1,2})$', re.I)

def check_records(records):
    from invenio.bibrank import ConfigParser, CFG_ETCDIR
    from invenio.bibrank_citation_indexer import get_recids_matching_query
    config = ConfigParser.ConfigParser()
    config.read("%s/bibrank/%s.cfg" % (CFG_ETCDIR, "citation"))
    for record in records:
        for field in record_get_field_instances(record, '999', 'C', '5'):
            subfields = field_get_subfield_instances(field)
            subfields_dict = dict(subfields)
            if 's' in subfields_dict:
                old_pubnote = subfields_dict['s']
                g = RE_BROKEN_PUBNOTES.match(old_pubnote)
                if g:
                    new_groupdict = g.groupdict()
                    new_groupdict['id'] = '%03d' % int(new_groupdict['id'])
                    new_pubnote = '%(journal)s,%(volume)s,%(id)s' % new_groupdict
                    if new_pubnote == old_pubnote:
                        # No change, e.g. due to id already well formatted
                        continue
                    subfields.remove(('s', old_pubnote))
                    subfields.append(('s', new_pubnote))
                    recids = get_recids_matching_query(p=new_pubnote,
                                                    f='journal',
                                                    config=config)
                    if len(recids) == 1:
                        recid = recids.pop()
                        if '0' in subfields_dict:
                            if str(recid) == subfields_dict['0']:
                                record.set_amended("Pubnote changed from %s to %s and matched the same known record %s" % (old_pubnote, new_pubnote, recid))
                            else:
                                record.warn("Pubnote changed from %s to %s and matched a different record %s (instead of %s)!" % (old_pubnote, new_pubnote, recid, subfields_dict['0']))
                                record.amended = True
                        else:
                            subfields.append(('0', str(recid)))
                            record.set_amended("Pubnote changed from %s to %s and matched a new record %s: Sam is the best, HURRAY!!!" % (old_pubnote, new_pubnote, recid))
                    else:
                        record.set_amended("Pubnote changed from %s to %s" % (old_pubnote, new_pubnote))
