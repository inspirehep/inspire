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

"""
Propagate ORCID information into HEPNames
"""

import sys

from invenio.config import CFG_SITE_URL
from invenio.dbquery import run_sql
from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import record_add_field, record_get_field_instances, field_get_subfield_instances, record_xml_output
from invenio.bibtask import write_message
from invenio.bibtaskutils import ChunkedBibUpload

def bst_hepnames_orcid_sync():
    bai_orcids = run_sql("SELECT bai.data, orcid.data FROM aidPERSONIDDATA as bai JOIN aidPERSONIDDATA as orcid ON bai.personid=orcid.personid WHERE orcid.tag='extid:ORCID' AND bai.tag='canonical_name'")

    recs = []

    not_matched_profiles = 0
    enhanced_records = 0
    conflicting_orcids = 0

    for bai, orcid in bai_orcids:
        recids = perform_request_search(p="035:%s" % bai, cc="HepNames")
        if len(recids) > 1:
            write_message("WARNING: %s/author/profile/%s, %s matches more than one HepNames: %s" % (CFG_SITE_URL, bai, orcid, recids), stream=sys.stderr)
            not_matched_profiles += 1
        elif not recids:
            write_message("WARNING: %s/author/profile/%s, %s does not match any HepName" % (CFG_SITE_URL, bai, orcid), stream=sys.stderr)
            not_matched_profiles += 1
        else:
            recid = recids[0]
            record = get_record(recid)
            for field in record_get_field_instances(record, tag="035"):
                subfields = field_get_subfield_instances(field)
                subfields_dict = dict(subfields)
                if subfields_dict.get('9') == 'ORCID':
                    if subfields_dict.get('a') != orcid:
                        if not subfields_dict.get('a', '').strip():
                            write_message("WARNING: record %s/record/%s has an empty ORCID" % (CFG_SITE_URL, recid), stream=sys.stderr)
                            continue
                        write_message("WARNING: record %s/record/%s matched by BAI %s/author/profile/%s has a different ORCID %s than the profile one: %s" % (CFG_SITE_URL, recid, CFG_SITE_URL, bai, subfields_dict.get('a'), orcid), stream=sys.stderr)
                        conflicting_orcids += 1
                    break
            else:
                new_record = {}
                record_add_field(new_record, tag="001", controlfield_value=str(recid))
                record_add_field(new_record, tag="035", subfields=[('a', orcid), ('9', 'ORCID')])
                recs.append(new_record)
                write_message("INFO: adding ORCID %s to record %s/record/%s matched by BAI %s/author/profile/%s" % (orcid, CFG_SITE_URL, recid, CFG_SITE_URL, bai))
                enhanced_records += 1
    if recs:
        write_message("INFO: initiating uploads")
        bibupload = ChunkedBibUpload(mode="a", user='bst_hepnames_orcid_sync')
        for record in recs:
            bibupload.add(record_xml_output(record))
        bibupload.cleanup()
    else:
        write_message("INFO: no modification are necessary")
    write_message("INFO: not_matched_profiles: %s, enhanced_records: %s, conflicting_orcids: %s" % (not_matched_profiles, enhanced_records, conflicting_orcids))
