# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2012, 2013, 2014 CERN.
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

"""xtrJOB db layer."""

from invenio.dbquery import run_sql
from datetime import datetime


def fetch_last_updated(name):
    """
    Get the date and ID of last updated records from xtrJOB table for
    given task-name.
    """
    select_sql = "SELECT last_recid, last_updated FROM xtrJOB" \
        " WHERE name = %s LIMIT 1"
    row = run_sql(select_sql, (name,))
    if not row:
        sql = "INSERT INTO xtrJOB (name, last_updated, last_recid) " \
            "VALUES (%s, NOW(), 0)"
        run_sql(sql, (name,))
        row = run_sql(select_sql, (name,))
    # Fallback in case we receive None instead of a valid date
    last_recid = row[0][0] or 0
    last_date = row[0][1] or datetime(year=1, month=1, day=1)
    return last_recid, last_date


def store_last_updated(recid, creation_date, name):
    """
    Update the date and ID of last updated record in xtrJOB table for
    given task-name.
    """
    sql = "UPDATE xtrJOB SET last_recid = %s WHERE name=%s AND last_recid < %s"
    run_sql(sql, (recid, name, recid))
    sql = "UPDATE xtrJOB SET last_updated = %s " \
                "WHERE name=%s AND last_updated < %s"
    iso_date = creation_date.isoformat()
    run_sql(sql, (iso_date, name, iso_date))


def get_all_new_records(since, last_recid):
    """
    Get all the newly inserted records since last run.
    """
    # Fetch all records inserted since last run
    sql = "SELECT `id`, `creation_date` FROM `bibrec` " \
        "WHERE `creation_date` >= %s " \
        "AND `id` > %s " \
        "ORDER BY `creation_date`"
    return run_sql(sql, (since.isoformat(), last_recid))


def get_all_modified_records(since, last_recid):
    """
    Get all the newly modified records since last run.
    """
    sql = "SELECT `id`, `modification_date` FROM `bibrec` " \
        "WHERE `modification_date` >= %s " \
        "AND `id` > %s " \
        "ORDER BY `modification_date`"
    return run_sql(sql, (since.isoformat(), last_recid))


def can_launch_bibupload(taskid):
    """
    Checks if task can be launched.
    """
    if taskid == 0:
        return True

    sql = 'SELECT status FROM schTASK WHERE id = %s'
    status = run_sql(sql, [str(taskid)])[0][0]
    if status not in ("DONE", "WAITING_DELETED"):
        return False
    return True
