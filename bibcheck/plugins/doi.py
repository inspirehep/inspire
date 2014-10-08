# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" Bibcheck plugin add the DOIs (from crossref) """

from invenio.bibrecord import record_add_field
from invenio.crossrefutils import get_doi_for_records
from invenio.bibupload import find_record_from_doi
from invenio.bibcatalog import BIBCATALOG_SYSTEM
from invenio.config import CFG_SITE_URL


def check_records(records, doi_field="0247_a", extra_subfields=(("2", "DOI"), ("9", "bibcheck")), create_ticket=False):
    """
    Find the DOI for the records using crossref and add it to the specified
    field.

    This plugin won't ask for the DOI if it's already set.
    """
    records_to_check = {}
    for record in records:
        check_record = True
        for position, value in record.iterfield("0247_2"):
            if value.lower() == "doi":
                check_record = False
                break
        # Do not consider records in the proceedings collection
        for position, value in record.iterfield("980__a"):
            if value.lower() == "proceedings":
                check_record = False
                break
        if check_record:
            records_to_check[record.record_id] = record

    dois = get_doi_for_records(records_to_check.values())
    for record_id, doi in dois.iteritems():
        record = records_to_check[record_id]
        dup_doi_recid = find_record_from_doi(doi)
        if dup_doi_recid:
            record.warn("DOI %s to be added to record %s already exists in record/s %s" % (doi, record_id, dup_doi_recid))
            if create_ticket:
                subject = "DOI conflict record #%s" % str(record_id)
                res = BIBCATALOG_SYSTEM.ticket_submit(
                    subject=subject,
                    recordid=record_id,
                    text=subject,
                    queue="Bibcheck"
                )
                if res:
                    msg = """
                        DOI %s to be added to record %s already exists in record/s %s

                        Record with conflict: %s
                        Record with original DOI: %s

                        Merge both records: %s
                    """
                    dup_doi_recid = int(dup_doi_recid)
                    record_id = int(record_id)
                    msg = msg % (
                        doi,
                        record_id,
                        dup_doi_recid,
                        "%s/record/%s" % (CFG_SITE_URL, record_id),
                        "%s/record/%s" % (CFG_SITE_URL, dup_doi_recid),
                        "%s/record/merge/?#recid1=%s&recid2=%s" % (CFG_SITE_URL, min(dup_doi_recid, record_id), max(dup_doi_recid, record_id))
                    )
                    if isinstance(msg, unicode):
                        msg = msg.encode("utf-8")
                    BIBCATALOG_SYSTEM.ticket_comment(None, res, msg)
            continue
        subfields = [(doi_field[5], doi.encode("utf-8"))] + map(tuple, extra_subfields)
        record_add_field(record, tag=doi_field[:3], ind1=doi_field[3],
                ind2=doi_field[4], subfields=subfields)
        record.set_amended("Added DOI in field %s" % doi_field)
