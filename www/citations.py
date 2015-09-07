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

"""Expose INSPIRE citation log via JSON"""


from json import dumps
from invenio.dbquery import run_sql

def index(req, id=0):
    """
    Return an id-ordered list of citation log entries of at most 10000
    rows.
    """
    req.content_type = 'application/json'
    return dumps(run_sql("""SELECT id, citer, citee, type,
        DATE_FORMAT(action_date, '%%Y-%%m-%%d %%H:%%i:%%s')
        FROM rnkCITATIONLOG WHERE id>%s ORDER BY id LIMIT 10000""", (id, )))
