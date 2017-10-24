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

"""Continuously synchronizes ORCID tokens to Labs via REDIS"""

import redis

try:
    from invenio.config import CFG_REDIS_HOST_LABS
except ImportError:
    CFG_REDIS_HOST_LABS = None

from invenio.dbquery import run_sql
from invenio.webuser import collect_user_info
from invenio.bibtask import write_message

CFG_REDIS_ORCID_SYNC_KEY = 'legacy_orcid_tokens'

def orcid_data_to_sync():
    """Returns an iterator of data to sync."""
    rows = run_sql("SELECT personid, data, token FROM aidPERSONIDDATA NATURAL JOIN aidTOKEN WHERE tag='extid:ORCID';")
    for personid, orcid, token in rows:
        uid = run_sql("SELECT data FROM aidPERSONIDDATA WHERE personid=%s AND tag='uid'", (personid, ))
        if uid:
            uid = int(uid[0][0])
            user_info = collect_user_info(uid)
            if user_info.get('external_firstname') and user_info.get('external_familyname'):
                name = u'%s %s' % (user_info['external_firstname'].decode('utf8'), user_info['external_familyname'].decode('utf8'))
            else:
                name = user_info['nickname'].decode('utf8')
            yield orcid.decode('utf8'), token.decode('utf8'), user_info['email'].decode('utf8'), name


def bst_orcidsync():
    """Sync to redis."""
    r = redis.StrictRedis.from_url(CFG_REDIS_HOST_LABS)
    # We first empty the information
    r.ltrim(CFG_REDIS_ORCID_SYNC_KEY, -1, 0)
    for orcid, token, email, name in orcid_data_to_sync():
        r.lpush(CFG_REDIS_ORCID_SYNC_KEY, (orcid, token, email, name))
    write_message("%s ORCID entries pushed to Labs" % r.llen(CFG_REDIS_ORCID_SYNC_KEY))
    return True

