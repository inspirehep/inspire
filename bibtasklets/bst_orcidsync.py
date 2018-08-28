#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Continuously synchronizes ORCID tokens to Labs via REDIS.

Note: a aidPERSONIDDATA.personid can be associated with multiple identifiers (eg. tag='extid:ORCID', tag='uid').
On 2018.02.23 15:05:27 in legacy there are 14058 personid with 1 identifier, 6726 personid with 2 and 1 personid with 3 identifier, as per:

SELECT cnt, count(*) FROM (
SELECT personid, count(*) as cnt FROM aidPERSONIDDATA WHERE tag='uid' OR tag='extid:ORCID' GROUP BY personid
) AS Q1 GROUP BY cnt;

'1', '14058'
'2', '6726'
'3', '1'
"""

import re
import redis
import json

try:
    from invenio.config import CFG_REDIS_HOST_LABS
except ImportError:
    CFG_REDIS_HOST_LABS = None

from invenio.dbquery import run_sql
from invenio.webuser import collect_user_info
from invenio.bibtask import write_message
from invenio.bibauthorid_webapi import get_hepnames

CFG_REDIS_ORCID_SYNC_KEY = 'legacy_orcid_tokens'
CFG_REDIS_ORCID_SYNC_KEY_COUNT = 'legacy_orcid_tokens_count'


def orcid_data_to_sync():
    """
    Collect all available OAuth tokens for ORCID and their related data:
    (orcid, token, email, name)
    Orcid and token are mandatory data.
    Email and name can be empty strings.
    In order to collect the email and the name, the strategy is:
    - if a uid is found, then try to get them from the user table.
    - if the email or the name are empty, then try to get them from HepNames.

    Note regarding account types.
    There are 2 different types of account involved.
    1. The Inspire user account that requires an email and name and assigns
    a uid (in particular when users log in via arXiv). The BAI system personid
    is separate and independent of the Inspire user accounts uid, but if a
    connection can be made to a user account the uid is associated with the
    personid in the aidPERSONIDDATA table.
    2. HepNames which has personal data like name and email and is associated
    with the BAI via MARC: 000996436 035__ $$9BAI$$aSimona.Murgia.1
    There are some convenience methods to get info from HepNames:
    from invenio.bibauthorid_webapi import get_hepnames
    """
    rows = run_sql("SELECT personid, data, token FROM aidPERSONIDDATA NATURAL JOIN aidTOKEN WHERE tag='extid:ORCID';")
    for personid, orcid, token in rows:
        orcid = orcid.decode('utf8')
        token = token.decode('utf8')
        email = u''
        name = u''

        uid = run_sql("SELECT data FROM aidPERSONIDDATA WHERE personid=%s AND tag='uid'", (personid, ))

        # If uid, then collect name and email from the user table.
        if uid:
            uid = int(uid[0][0])
            user_info = collect_user_info(uid)
            email = _validate_email(user_info['email'].decode('utf8'))
            if user_info.get('external_firstname') and user_info.get('external_familyname'):
                name = u'%s %s' % (user_info['external_firstname'].decode('utf8'), user_info['external_familyname'].decode('utf8'))
            else:
                name = user_info['nickname'].decode('utf8')

        # If name or email are empty, then try to collect them from HepNames.
        hepnames = {}
        if not email or not name:
            hepnames = get_hepnames(personid)

        # hepnames['have_hep'] is true if an exact match was found.
        # Otherwise it is a dictionary of possible choices (useless in this
        # context).
        have_hep = hepnames.get('have_hep')

        if have_hep and not email:
            emails = hepnames.get('record', {}).get('emails')  # 'emails' can be an empty list.
            email = _validate_email(emails[0].decode('utf8')) if emails else u''

        if have_hep and not name:
            name = hepnames.get('record', {}).get('display_name', '').decode('utf8')

        yield orcid, token, email, name


def _validate_email(email):
    """
    Basic validation for email addresses.
    """
    email_regex = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    if not email_regex.match(email):
        return u''
    return email


def count_orcid_data_to_sync():
    """
    Count the number of ORCID tokens (and relative data) to be synch'ed (and
    thus sent to Redis). This is used at Lab's side to check whether the right
    number of token has been processed.

    Returns (int): a number.
    """
    query = """
        SELECT count(*) FROM (
            SELECT personid, count(*) AS cnt FROM aidPERSONIDDATA WHERE tag='uid' AND personid IN (
                SELECT personid FROM aidPERSONIDDATA NATURAL JOIN aidTOKEN WHERE tag='extid:ORCID'
            ) GROUP BY personid
        ) AS Q1;    
    """
    count = run_sql(query)
    return int(count[0][0])


def bst_orcidsync():
    """Sync to redis."""
    r = redis.StrictRedis.from_url(CFG_REDIS_HOST_LABS)
    # We first empty the information
    r.ltrim(CFG_REDIS_ORCID_SYNC_KEY, -1, 0)
    for orcid, token, email, name in orcid_data_to_sync():
        r.lpush(CFG_REDIS_ORCID_SYNC_KEY, json.dumps((orcid, token, email, name)))
    write_message("%s ORCID entries pushed to Labs" % r.llen(CFG_REDIS_ORCID_SYNC_KEY))

    # Store the total number of tokens to be synch'ed.
    count = count_orcid_data_to_sync()
    r.set(CFG_REDIS_ORCID_SYNC_KEY_COUNT, count)

    return True
