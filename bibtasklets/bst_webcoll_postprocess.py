#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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

"""Interact with Labs site to continue submissions when webcoll has run."""

import requests

from invenio.bibtask import write_message
from invenio.redisutils import get_redis

try:
    from invenio.config import CFG_WEBCOLL_POST_REQUEST_URL
except ImportError:
    CFG_WEBCOLL_POST_REQUEST_URL = None


def bst_webcoll_postprocess(recids=[]):
    """Parse recids to POST to remote server to alert that records are visible."""
    if isinstance(recids, str):
        recids = recids.split(",")
    cache = get_redis()
    cached_ids = cache.get("webcoll_pending_recids") or []
    if cached_ids and not cached_ids == "[]":
        if isinstance(cached_ids, str):
            cached_ids = eval(cached_ids)
        recids += cached_ids

    if not CFG_WEBCOLL_POST_REQUEST_URL:
        write_message("CFG_WEBCOLL_POST_REQUEST_URL is not set.")
        return

    if recids and len(recids) > 0 and not recids == "[]":
        write_message("Going to POST callback to {0}: {1} (total: {2})".format(
            CFG_WEBCOLL_POST_REQUEST_URL,
            recids[:10],
            len(recids))
        )
        cache.set("webcoll_pending_recids", recids)
        session = requests.Session()
        try:
            addapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount(CFG_WEBCOLL_POST_REQUEST_URL, addapter)
            response = session.post(CFG_WEBCOLL_POST_REQUEST_URL,
                                    data={'recids': recids})
        except Exception as err:
            write_message("Post request failed!")
            write_message(err)
            return
        finally:
            session.close()

        if response.ok:
            write_message("Post request sent successfully")
            cache.set("webcoll_pending_recids", [])
        else:
            write_message("Post request failed!")
            write_message(response.text)
            cache.set("webcoll_pending_recids", recids)
    else:
        write_message("No recids to POST callback for to {0}.".format(
            CFG_WEBCOLL_POST_REQUEST_URL,
        ))
