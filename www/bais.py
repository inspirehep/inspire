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

"""Return the list of the latest 1000 created profiles"""

from cgi import escape

from invenio.config import CFG_SITE_URL
from invenio.webpage import page
from invenio.urlutils import wash_url_argument
from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances

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
        body.append('<li><a href="%(siteurl)s/record/%(recid)s">%(author_name)s</a> -> <a href="%(siteurl)s/author/profile/%(bai)s">%(bai)s</a></li>' % {
            'siteurl': escape(CFG_SITE_URL, True),
            'recid': recid,
            'author_name': escape(author_name, True),
            'bai': escape(bai, True)})
    body.append("</ol>")
    body = '\n'.join(body)

    return page(req=req, body=body, title="HepNames and BAIs for %s" % escape(p, True))
