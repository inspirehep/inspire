# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2013, 2014 CERN.
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

"""Inspire Arxiv Harvest Notification

An alarm system to notify the appropriate person if the daily
Arxiv harvest has not ran.
"""
from invenio.search_engine import perform_request_search
from invenio.config import CFG_SITE_ADMIN_EMAIL, CFG_WEBALERT_ALERT_ENGINE_EMAIL


def bst_arxiv_harvest_notification(admin_email=CFG_SITE_ADMIN_EMAIL):
    """
    Checks if Arxiv harvesting has ran today and emails the
    admin if it has not. This task should be scheduled to run
    at the end of the day.

    @param admin_email: The person who should be notified
    @type admin_email: string
    """
    # Search string lists all records harvested today from Arxiv
    if not perform_request_search(p="find da today and eprint arxiv"):
        from invenio.mailutils import send_email
        message = """
            The Arxiv harvest does not appear to have ran
            today (No new records have been harvested)."""

        send_email(admin_email, CFG_WEBALERT_ALERT_ENGINE_EMAIL,
            "Notice: Arxiv harvest has not ran today", message)
