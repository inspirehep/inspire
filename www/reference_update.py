# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014, 2019 CERN.
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

"""Receives form requests for reference updates


"""

from invenio.bibcatalog import BIBCATALOG_SYSTEM
from invenio.config import CFG_SITE_SECURE_URL, CFG_SITE_URL
from invenio.urlutils import redirect_to_url, wash_url_argument
from invenio.webpage import page


def _get_report_numbers(record_id):
    from invenio.bibformat_engine import BibFormatObject
    bfo = BibFormatObject(record_id)
    fields = bfo.fields('037__')
    report_numbers = []
    for field in fields:
        if 'a' in field:
            report_numbers.append(field['a'])
    return report_numbers


########### RT TICKET RELATED FUNCTIONS ###########


def submit_ticket(msg, subject, record_id, queue="Test", email=""):
    """
    Submit a ticket to RT with the given subject and body
    """
    if isinstance(msg, unicode):
        msg = msg.encode("utf-8")

    res = BIBCATALOG_SYSTEM.ticket_submit(
        subject=subject,
        recordid=record_id,
        text=subject,
        queue=queue,
        requestor=email
    )
    if res:
        BIBCATALOG_SYSTEM.ticket_comment(None, res, msg)


def submit_reference_arxiv_ticket(record_id, email, comments):
    """ Submit the errors to bibcatalog """

    report_numbers = _get_report_numbers(record_id)

    ticket_elements = {
        "arxiv": {
            "bibedit_link": "%s/record/%s/edit" % (CFG_SITE_SECURE_URL, record_id),
            "comments": comments,
            "extratext": "New version of the record in arXiv - %s" % report_numbers[0] if report_numbers else ""
        }
    }

    msg = """
    Comments:
    %(comments)s

    %(extratext)s

    Open record in BibEdit: %(bibedit_link)s
    """ % ticket_elements['arxiv']

    subject = "updated refs on arXiv: #%s (%s)" % (record_id, " ".join(report_numbers))

    submit_ticket(msg, subject, record_id, queue="HEP_ref_user", email=email)


def submit_reference_new_published_ticket(record_id, references, url, email, comments):
    """ Submit the errors to bibcatalog """

    report_numbers = _get_report_numbers(record_id)

    msg = """
Comments:
%s

References:
%s

URL:
%s

Open record in BibEdit: %s

"""
    msg = msg % (
        comments,
        references,
        url,
        "%s/record/%s/edit" % (CFG_SITE_SECURE_URL, record_id)
    )

    subject = "updated refs in published version: #%s (%s)" % (record_id, " ".join(report_numbers))

    submit_ticket(msg, subject, record_id, queue="HEP_ref_user", email=email)


def submit_reference_add_ticket(record_id, references, url, email, comments):
    """ Submit the errors to bibcatalog """

    report_numbers = _get_report_numbers(record_id)

    msg = """
Comments:
%s

References:
%s

URL:
%s

Open record in BibEdit: %s

"""
    msg = msg % (
        comments,
        references,
        url,
        "%s/record/%s/edit" % (CFG_SITE_SECURE_URL, record_id)
    )

    subject = "new refs: #%s (%s)" % (record_id, " ".join(report_numbers))

    submit_ticket(msg, subject, record_id, queue="HEP_ref_user", email=email)


def submit_reference_modify_ticket(record_id, references, email, realname, comments):
    """ Submit the errors to bibcatalog """

    report_numbers = _get_report_numbers(record_id)

    msg = """
Name:
%s
Comments:
%s

References:
%s

Open record in BibEdit: %s

"""
    msg = msg % (
        realname,
        comments,
        references,
        "%s/record/%s/edit" % (CFG_SITE_SECURE_URL, record_id)
    )
    repnos = ''
    if report_numbers:
        repnos = '(' + " ".join(report_numbers) + ')'

    subject = "CITATION updates form INSPIRE #%s %s" % (record_id, repnos)

    submit_ticket(msg, subject, record_id, queue="HEP_ref_user", email=email)


########### SUCCESS HANDLERS ###########


def arxivsuccess(req, record_id):
    body = """
        <p>
        <b>Thanks for your submission!</b><br/>
        </p>
        <p>
        We will notify you as soon as the references have been reextracted from the newest arXiv version.
        </p>
        <p>
        <a href='%s/record/%s'>Back to the record</a>
        </p>
        """ % (CFG_SITE_URL, record_id)
    return page(req=req, title="References submitted", body=body)


def reference_add_success(req, record_id):
    body = """
    <br/><b>Thanks for your submission!</b><br/>

    <p>We will now try to extract the references.</p>
    <p>A notification will be sent to you as soon as the references have been checked by our staff.</p>
    <p>You will then have the possibility to correct any references we might have failed to identify.<p>
    <p><a href='%s/record/%s'>Back to the record</a></p>
    """ % (CFG_SITE_URL, record_id)

    return page(req=req, title="References submitted", body=body)


########### POST HANDLERS FROM REFERENCE UPDATE FORMS ###########


def reference_correction(req, record_id, email, comments, problem):
    """
    Form handler for requests coming from HRU format

    Used when there is a new arxiv version

    @param problem: value of radio select on the form
    possible values are: arxiv, published, or wrong
    @type name: str
    """
    email = wash_url_argument(email, "str")
    problem = wash_url_argument(problem, "str")
    comments = wash_url_argument(comments, "str")
    record_id = wash_url_argument(record_id, "int")

    if problem == "wrong":
        # Send users to the old reference update form
        return redirect_to_url(req, "%s/record/%s/export/hrf" % (CFG_SITE_URL, record_id))
    elif problem == "arxiv":
        submit_reference_arxiv_ticket(record_id, email, comments)
        return redirect_to_url(req, "%s/reference_update.py/arxivsuccess?record_id=%s" % (CFG_SITE_URL, record_id))
    else:
        # Newly published version
        return redirect_to_url(req, "%s/record/%s/export/hrn" % (CFG_SITE_URL, record_id))


def reference_new_published(req, record_id, references, url, email, comments):
    """
    Form handler for requests coming from HRN format

    Used when there is a new published version

    """
    record_id = wash_url_argument(record_id, "int")
    references = wash_url_argument(references, "str")
    url = wash_url_argument(url, "str")
    email = wash_url_argument(email, "str")
    comments = wash_url_argument(comments, "str")

    submit_reference_new_published_ticket(record_id, references, url, email, comments)

    return redirect_to_url(req, "%s/reference_update.py/reference_add_success?record_id=%s" % (CFG_SITE_URL, record_id))


def reference_add(req, record_id, references, url, email, comments):
    """
    Form handler for requests coming from HRA format

    Used when the record has no references

    """
    record_id = wash_url_argument(record_id, "int")
    references = wash_url_argument(references, "str")
    url = wash_url_argument(url, "str")
    email = wash_url_argument(email, "str")
    comments = wash_url_argument(comments, "str")

    submit_reference_add_ticket(record_id, references, url, email, comments)

    return redirect_to_url(req, "%s/reference_update.py/reference_add_success?record_id=%s" % (CFG_SITE_URL, record_id))


def references_modify(req, recid=-1, cite='', username='', realname='',
                      usercomment='', *args, **kwargs):
    """
    Form handler for requests coming from HRF format

    Used to update/modify existing references
    """

    record_id = wash_url_argument(recid, "int")
    email = wash_url_argument(username, "str")
    realname = wash_url_argument(realname, "str")
    comments = wash_url_argument(usercomment, "str")

    cites = cite
    cites = [c.replace('**', '\t.......... <== modified/changed') for c in cites]
    cites = [c + '\t.......... <== modified/added' if c.startswith('$$')
             else c for c in cites]
    cites = ['--' if c == '' else c for c in cites]

    citelist = ''
    for count, ref in enumerate(cites, 1):
        citelist += "%3d:\t%s\n" % (count, ref)

    submit_reference_modify_ticket(record_id, citelist, email,
                                   realname, comments)

    return redirect_to_url(
        req, "%s/reference_update.py/reference_add_success?record_id=%s" %
        (CFG_SITE_URL, record_id))
