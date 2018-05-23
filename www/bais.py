# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015, 2018 CERN.
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

"""Return the list of the latest 1000 created profiles"""

from cgi import escape

from invenio.config import CFG_SITE_SECURE_URL
from invenio.webpage import page
from invenio.urlutils import wash_url_argument
from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances
from invenio.intbitset import intbitset

def index(req, p=""):
    """
    Return an id-ordered list of citation log entries of at most 10000
    rows.
    """
    if not p:
        p = ""

    def get_author_name(record):
        for field in record_get_field_instances(record, '100'):
            subfields = dict(field_get_subfield_instances(field))
            if 'a' in subfields:
                return subfields['a']
        return ''

    def get_bai(record):
        for field in record_get_field_instances(record, '035'):
            subfields = dict(field_get_subfield_instances(field))
            if subfields.get('9', '').upper() == 'BAI':
                return subfields.get('a', '')
        return ''

    body = ['<form>Search query: <input name="p" value="%s" type="text" /><input type="submit" /></form><ol>' % escape(p, True)]

    recids = perform_request_search(req=req, p=p, cc="HepNames", sf="exactfirstauthor", so="a")
    for recid in recids:
        record = get_record(recid)
        author_name = get_author_name(record)
        bai = get_bai(record)
        if bai:
            body.append('<li><a href="%(siteurl)s/record/%(recid)s">%(author_name)s</a> -> <a href="%(siteurl)s/author/profile/%(bai)s">%(bai)s</a></li>' % {
                'siteurl': escape(CFG_SITE_SECURE_URL, True),
                'recid': recid,
                'author_name': escape(author_name, True),
                'bai': escape(bai, True)})
        else:
            body.append('<li><strong><a href="%(siteurl)s/record/%(recid)s">%(author_name)s</a></strong> ->></li>' % {
                'siteurl': escape(CFG_SITE_SECURE_URL, True),
                'recid': recid,
                'author_name': escape(author_name, True)})

    body.append("</ol>")
    body = '\n'.join(body)

    return page(req=req, body=body, title="HepNames and BAIs for %s" % escape(p, True))


def unlinked(req, orcidonly=False):
    """
    Return an id-ordered list of citation log entries of at most 10000
    rows.
    """
    from invenio.dbquery import run_sql
    from invenio.search_engine import get_fieldvalues, get_collection_reclist
    useful_personids1 = intbitset(run_sql("SELECT distinct personid FROM aidPERSONIDDATA WHERE tag LIKE 'extid:%'"))
    useful_personids2 = intbitset()
    if not orcidonly:
        useful_personids2 = intbitset(run_sql("SELECT distinct personid from aidPERSONIDPAPERS where flag=2"))
    linked_personids = intbitset(run_sql("SELECT personid FROM aidPERSONIDDATA WHERE tag='extid:INSPIREID'"))
    names = dict(run_sql("SELECT personid, data FROM aidPERSONIDDATA WHERE tag='canonical_name'"))
    matched_names = [name.lower().strip() for name in get_fieldvalues(get_collection_reclist('HepNames'), '035__a')]
    personid_to_match = (useful_personids1 | useful_personids2) - linked_personids

    body = ['<ol>']
    for personid in personid_to_match:
        name = names.get(personid, str(personid))
        if name.lower().strip() in matched_names:
            continue
        body.append('<li><a href="%(siteurl)s/author/profile/%(bai)s" target="_blank">%(bai)s</a></li>' % {
                'siteurl': escape(CFG_SITE_SECURE_URL, True),
                'bai': escape(name, True)})
    body.append('</ol>')
    body = '\n'.join(body)

    if orcidonly:
        title = "Unlinked BAIs with ORCID"
    else:
        title = "Unlinked useful BAIs"

    return page(req=req, body=body, title=title)


def json(req):
    """
    Returns all BAI information in a JSON friendly way.
    """
    import json
    from invenio.dbquery import run_sql
    from invenio.webuser import collect_user_info
    from invenio.access_control_admin import acc_is_user_in_role, acc_get_role_id
    if not acc_is_user_in_role(collect_user_info(req), acc_get_role_id('cernintranet')):
        from invenio.webinterface_handler_config import HTTP_FORBIDDEN
        req.status = HTTP_FORBIDDEN
        return ""
    bais = run_sql("SELECT personid, tag, data FROM aidPERSONIDDATA WHERE tag in ('canonical_name', 'extid:INSPIREID', 'extid:ORCID', 'uid') ORDER BY personid")
    emails = dict(run_sql("SELECT id, email FROM user"))
    req.content_type = 'application/json'
    old_personid = None
    authors = {}
    person = {}
    canonical_name = ""
    for personid, tag, data in bais:
        if personid != old_personid:
            if not person and canonical_name in authors:
                # We can delete this person
                del authors[canonical_name]
            person = {}
            old_personid = personid
        if tag == 'canonical_name':
            authors[data] = person
            canonical_name = data
        elif tag == 'uid' and int(data) in emails:
            person['email'] = emails[int(data)]
        elif tag == 'extid:INSPIREID':
            person['INSPIREID'] = data
        elif tag == 'extid:ORCID':
            person['ORCID'] = data
    json.dump(authors, req)
    return ""
