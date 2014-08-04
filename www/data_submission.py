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

"""
Receives data submission requests, generates an email for manual curation
"""

from invenio.urlutils import wash_url_argument
from invenio.config import CFG_SITE_URL
from invenio.webpage import page
from invenio.urlutils import redirect_to_url
from invenio.config import CFG_TMPSHAREDDIR


def new_dataset(req, title=None, paper=None, authors=None, description=None, dataset_file=None, doi="", submitter_name=None, submitter_email=None, comments=None):
    """
    Form handler for dataset submissions
    """
    import uuid

    title = wash_url_argument(title, "str")
    paper = wash_url_argument(paper, "str")
    authors = wash_url_argument(authors, "str")
    description = wash_url_argument(description, "str")
    submitter_name = wash_url_argument(submitter_name, "str")
    submitter_email = wash_url_argument(submitter_email, "str")
    comments = wash_url_argument(comments, "str")

    dataset_file = wash_url_argument(dataset_file, "str")
    tmp_id = str(uuid.uuid1())
    if dataset_file:
        f = open(CFG_TMPSHAREDDIR + 'dataset-submission-' + tmp_id, 'wb')
        f.write(req.form["dataset_file"].file.read())
        f.close()

    res = submit_email_ticket(title, paper, authors, description, tmp_id, req.form["dataset_file"].filename, doi, submitter_name, submitter_email, comments)

    if res:
        return redirect_to_url(req, "%s/data_submission.py/data_submission_success?title=%s" % (CFG_SITE_URL, title))
    else:
        return redirect_to_url(req, "%s/data_submission.py/data_submission_fail?title=%s" % (CFG_SITE_URL, title))


def submit_email_ticket(title, paper, authors, description, dataset_file, dataset_name, doi, submitter_name, submitter_email, comments):
    """
    Submits a multipart email containing the metadata and the dataset file
    """
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.mime.text import MIMEText
    from email import Encoders
    from invenio.config import CFG_MISCUTIL_SMTP_HOST, CFG_MISCUTIL_SMTP_PORT

    curators = ("laura.rueda@cern.ch", "particia.herterich@cern.ch", "sunje.dallmeier-tiessen@cern.ch")
    
    msg = MIMEMultipart()
    msg['Subject'] = "New dataset submission from %s" % (submitter_name) 
    msg['From'] = submitter_email
    msg['To'] = ', '.join(curators)

    text = """
    Title: %s
    Original paper: %s
    Author list: %s
    Description: %s
    Wants a DOI: %s

    Submitter: %s
    E-mail: %s
    Comments: %s
    """ % (title, paper, authors, description, doi, submitter_name, submitter_email, comments)
    part1 = MIMEText(text, 'plain')

    part2 = MIMEBase('application', 'octet-stream')
    part2.set_payload(open(CFG_TMPSHAREDDIR + 'dataset-submission-' + dataset_file, "rb").read())
    Encoders.encode_base64(part2)
    part2.add_header('Content-Disposition', 'attachment; filename="' + dataset_name + '"')

    msg.attach(part1)
    msg.attach(part2)

    server = smtplib.SMTP(CFG_MISCUTIL_SMTP_HOST, CFG_MISCUTIL_SMTP_PORT)
    server.sendmail(submitter_email, curators, msg.as_string())
    server.quit()

    return True


def data_submission_success(req, title, ticketres=None):
    """
    Submission confirmation message
    """

    body = """
    <br/><b>Thanks for your submission!</b><br/>
    <p>We will get back to you as soon as the the submission of the dataset <i>%s</i> is processed!</p>
    """ % (wash_url_argument(title, "str"))

    return page(req=req, title="Dataset submitted", body=body)

def data_submission_fail(req, title, ticketres=None):
    """
    Submission error message
    """

    body = """
    <br/><b>Your submission of "%s" failed!</b><br/>
    <p>We are sorry for this inconvenience, please try again.</p>
    """ % (wash_url_argument(title, "str"))

    return page(req=req, title="Dataset submitted", body=body)