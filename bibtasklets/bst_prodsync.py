#!/usr/bin/env python
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

"""Continuously synchronizes to Labs via REDIS"""

import datetime
import time

import os

from invenio.config import CFG_TMPSHAREDDIR

try:
    from invenio.config import CFG_REDIS_HOST_LABS
except ImportError:
    CFG_REDIS_HOST_LABS = None

from invenio.dbquery import run_sql

from invenio.dateutils import get_time_estimator

from invenio.bibformat_engine import format_record

from invenio.bibtask import task_update_progress, write_message

from invenio.intbitset import intbitset

import redis

import gzip


CFG_OUTPUT_PATH = "/afs/cern.ch/project/inspire/PROD/var/tmp-shared/prodsync.xml.gz"

def bst_prodsync():
    if CFG_REDIS_HOST_LABS:
        r = redis.StrictRedis.from_url(CFG_REDIS_HOST_LABS)
    else:
        write_message("Redis disabled, appeding output to %s" % CFG_OUTPUT_PATH)
        r = gzip.open(CFG_OUTPUT_PATH, "a")
    future_lastrun = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lastrun_path = os.path.join(CFG_TMPSHAREDDIR, 'prodsync_lastrun.txt')
    try:
        last_run = open(lastrun_path).read().strip()
        modified_records = intbitset(run_sql("SELECT id FROM bibrec WHERE modification_date>=%s", (last_run, )))
        for citee, citer in run_sql("SELECT citee, citer FROM rnkCITATIONDICT WHERE last_updated>=%s", (last_run, )):
            modified_records.add(citee)
            modified_records.add(citer)
        modified_records |= intbitset(run_sql("SELECT bibrec FROM aidPERSONIDPAPERS WHERE last_updated>=%s", (last_run, )))
    except IOError:
        # Default to the epoch
        modified_records = intbitset(run_sql("SELECT id FROM bibrec"))
    tot = len(modified_records)
    time_estimator = get_time_estimator(tot)
    for i, recid in enumerate(modified_records):
        if CFG_REDIS_HOST_LABS:
            r.rpush('records', [format_record(recid, 'xme')[0]])
            # Client should simply use http://redis.io/commands/blpop
        else:
            # NOTE: just for debugging purposes
            print >> r, format_record(recid, 'xme')[0]
        task_update_progress("%s (%s%%) -> %s" % (recid, (i + 1) * 100 / tot, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_estimator()[1]))))
    write_message("Pushed %s records" % tot)
    open(lastrun_path, "w").write(future_lastrun)
