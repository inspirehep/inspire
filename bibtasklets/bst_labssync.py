#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Continuously synchronizes from Labs via REDIS"""

import sys
import redis
import requests

from invenio.config import CFG_REDIS_HOST_LABS, CFG_LABS_HOSTNAME
from invenio.bibtaskutils import ChunkedBibUpload
from invenio.bibtask import write_message
from invenio.bibrecord import create_record, record_xml_output
from invenio.urlutils import make_user_agent_string
from invenio.errorlib import register_exception


CFG_REDIS_KEY = 'records_to_sync_into_legacy'


def bst_labssync():
    """
    Synchronizes from Labs via redis.

    """
    r = redis.StrictRedis.from_url(CFG_REDIS_HOST_LABS)
    user_agent = make_user_agent_string('labssync')
    s = requests.Session()
    s.headers['User-Agent'] = user_agent
    s.headers['Accept'] = 'application/marcxml+xml'

    tot = r.SCARD(CFG_REDIS_KEY)
    if tot == 0:
        write_message("Nothing to do")
        return
    else:
        write_message("At least %s records to synchronize from labs" % tot)

    errors = []
    final_total = 0
    uploader = ChunkedBibUpload(mode='r', user='labssync')
    while True:
        elem = r.spop(CFG_REDIS_KEY)
        if not elem:
            break
        final_total += 1
        try:
            record = s.get("https://%s/api/%s" % (CFG_LABS_HOSTNAME, elem)).text

            # Let's strip collection/XML header
            record = record_xml_output(create_record(record)[0])
            uploader.add(record)
        except Exception as err:
            register_exception()
            write_message("ERROR: when retrieving %s: %s" % (elem, err), stream=sys.stderr)
            errors.append(elem)

    write_message("Finally synced %s records from labs" % final_total)
    if errors:
        write_message("All those %s records had errors and might need to be resynced: %s" % (len(errors), ', '.join(errors)))
