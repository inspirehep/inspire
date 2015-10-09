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
from invenio.dbquery import run_sql

def index(req):
    """
    Return an id-ordered list of citation log entries of at most 10000
    rows.
    """
    res = []
    offset = 0
    while len(res) <= 1000:
        res += [row for row in run_sql("select data, count(p.personid) as d  from aidPERSONIDDATA as d JOIN aidPERSONIDPAPERS as p ON d.personid=p.personid where flag > -2 AND tag='canonical_name' GROUP BY d.personid ORDER BY d.personid DESC LIMIT 1000 OFFSET %s" % offset) if row[1] > 0]
        offset += 1000
    body = "<ul>"
    body += "\n".join(['<li><a href="%(siteurl)s/author/profile/%(personid)s">%(personid)s (%(count)s)</a></li>' % {
        "siteurl": escape(CFG_SITE_URL, True),
        "personid": escape(personid, True),
        "count": count} for (personid, count) in res])
    body += "</ul>"
    return page(req=req, body=body, title="Latest 1000 created non empty profiles")
