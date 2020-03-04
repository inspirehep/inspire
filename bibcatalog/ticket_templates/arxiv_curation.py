# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2013, 2014, 2020 CERN.
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
BibCatalog template. This templates is for the INSPIRE arXiv curation.

Requirements to create ticket:
* Record must have 980__$aCORE
* Needs to be younger than 6 months in the system

subject
    arXiv:XXXX.YYYY
body
    Curate record here: <bibedit-link>
queue
    HEP_curation
"""

from invenio.bibcatalog_utils import (record_id_from_record,
                                      record_in_collection)
from invenio.bibrecord import (field_get_subfield_values,
                               record_get_field_instances)
from invenio.config import CFG_LABS_HOSTNAME, CFG_SITE_SECURE_URL


def check_record(ticket, record):  # pylint: disable-msg=W0613
    """
    Requirements to create ticket:
    * Record must have 980__$aCORE
    * Needs to be younger than 6 months in the system
    * Must be an arXiv paper

    Returns True if all above is true.

    @param ticket: a ticket object as created by BibCatalogTicket() containing
                   the subject, body and queue to create a ticket in.
    @type ticket: record object of BibCatalogTicket.

    @param record: a recstruct object as created by bibrecord.create_record()
    @type record: record object of BibRecord.

    @return: True if ticket should be created.
    @rtype: bool
    """
    # It has to be a CORE record
    if not record_in_collection(record, "CORE"):
        return False

    # Finally it has to be an arXiv record
    if not record_in_collection(record, "ARXIV"):
        return False

    # We are arXiv!
    return True


def generate_ticket(ticket, record):
    """
    Generates a ticket to be created, filling subject, body and queue values
    of the passed BibCatalogTicket object. The enriched object is returned.

    @param ticket: a ticket object as created by BibCatalogTicket() containing
                   the subject, body and queue to create a ticket in.
    @type ticket: record object of BibCatalogTicket.

    @param record: a recstruct object as created by bibrecord.create_record()
    @type record: record object of BibRecord.

    @return: the modified ticket object to create.
    @rtype: BibCatalogTicket
    """
    recid = record_id_from_record(record)
    subject = []

    # Add report number in the subjecet
    report_number = ""
    for report_tag in record_get_field_instances(record, "037"):
        for report_number in field_get_subfield_values(report_tag, 'a'):
            subject.append(report_number)
            break

    subject.append("(#%s)" % (recid,))
    text = """
Curate record here: https://%s/workflows/edit_article/%s

                    %s/record/edit/#state=edit&recid=%s
""" % (CFG_LABS_HOSTNAME, recid, CFG_SITE_SECURE_URL, recid)

    ticket.subject = " ".join(subject)
    ticket.body = text.replace('%', '%%')
    ticket.queue = "HEP_curation"
    return ticket
