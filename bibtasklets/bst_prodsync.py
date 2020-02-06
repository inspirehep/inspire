#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016, 2018, 2019 CERN.
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

"""Continuously synchronizes to Labs via REDIS"""

import datetime
import time
import tarfile
import os

from invenio.config import CFG_TMPSHAREDDIR

try:
    from invenio.config import CFG_REDIS_HOST_LABS
except ImportError:
    CFG_REDIS_HOST_LABS = None

from invenio.dbquery import run_sql

from invenio.dateutils import get_time_estimator

from invenio.bibformat_engine import format_record

from invenio.bibtask import task_update_progress, write_message, task_sleep_now_if_required

from invenio.intbitset import intbitset

from invenio.webuser import collect_user_info, get_uid_from_email, get_email_from_username
from invenio.search_engine import search_pattern, search_unit
import redis

import gzip
import zlib

ADMIN_USER_INFO = collect_user_info(get_uid_from_email(get_email_from_username('admin')))

CFG_OUTPUT_PATH = "/afs/cern.ch/project/inspire/PROD/var/tmp-shared/prodsync"

class run_ro_on_slave_db:
    """
    Force the usage of the slave DB in read-only mode
    """
    def __enter__(self):
        from invenio import dbquery_config
        from invenio import dbquery
        self.old_host = dbquery_config.CFG_DATABASE_HOST
        dbquery_config.CFG_DATABASE_HOST = dbquery_config.CFG_DATABASE_SLAVE
        self.old_site_level = dbquery.CFG_ACCESS_CONTROL_LEVEL_SITE
        dbquery.CFG_ACCESS_CONTROL_LEVEL_SITE = 1

    def __exit__(self, type, value, traceback):
        from invenio import dbquery_config
        from invenio import dbquery
        dbquery_config.CFG_DATABASE_HOST = self.old_host
        dbquery.CFG_ACCESS_CONTROL_LEVEL_SITE = self.old_site_level


def bst_prodsync(method='afs', with_citations='yes', with_claims='yes', skip_collections='', use_end_marker='no'):
    """
    Synchronize to either 'afs' or 'redis'

    with_citations: yes/no, whether records that now cite a record will need to be re-exported.
    with_claims: yes/no, whether record involved in some new claim need to be re-exported.
    skip_collections: comma-separated-lists of values for which records having 980:VALUE should be ignored,
        e.g. skip_collections='HEP,HEPNAMES,HEPHIDDEN'
    use_end_marker: yes/no, whether an explicit end marker should be used to allow atomic migration of the batch.
        This has an effect only if 'method' is 'redis'.
    """
    if not CFG_REDIS_HOST_LABS:
        method = 'afs'

    write_message("Prodsync started using %s method" % method)
    now = datetime.datetime.now()
    future_lastrun = now.strftime('%Y-%m-%d %H:%M:%S')
    lastrun_path = os.path.join(CFG_TMPSHAREDDIR, 'prodsync_%s_lastrun.txt' % method)
    try:
        last_run = open(lastrun_path).read().strip()
        write_message("Syncing records modified since %s" % last_run)
        with run_ro_on_slave_db():
            modified_records = intbitset(run_sql("SELECT id FROM bibrec WHERE modification_date>=%s", (last_run, )))
            compacttime = last_run.replace('-', '').replace(' ', '').replace(':', '')
            notimechangerecs = search_unit("%s->20250101000000" % compacttime, f='005', m='a')
            modified_records += notimechangerecs
            if with_citations.lower() == 'yes':
                modified_records += intbitset(run_sql("SELECT distinct citer FROM rnkCITATIONLOG WHERE action_date>=%s", (last_run, )))
            if with_claims.lower() == 'yes':
                modified_records |= intbitset(run_sql("SELECT bibrec FROM aidPERSONIDPAPERS WHERE last_updated>=%s", (last_run, )))
                modified_records |= intbitset(run_sql('SELECT bibrec FROM aidPERSONIDPAPERS AS p JOIN aidPERSONIDDATA as d'
                                                      ' ON p.personid = d.personid WHERE d.tag = "canonical_name" and d.last_updated>=%s', (last_run, )))
    except IOError:
        # Default to everything
        with run_ro_on_slave_db():
            modified_records = intbitset(run_sql("SELECT id FROM bibrec"))
        write_message("Syncing all records")

    skip_collections = skip_collections.split(',')
    skip_collections.remove('')
    for collection in skip_collections:
        modified_records -= search_pattern(p='980:%s' % collection)

    if not modified_records:
        write_message("Nothing to do")
        return True

    tot = len(modified_records)
    time_estimator = get_time_estimator(tot)
    write_message("Adding %s new or modified records" % tot)
    if method == 'afs':
        afs_sync(reversed(modified_records), time_estimator, tot, now)
        open(lastrun_path, "w").write(future_lastrun)
        write_message("DONE!")
    else:
        end_marker = "END" if use_end_marker.lower() == "yes" else None
        if redis_sync(reversed(modified_records), time_estimator, tot, now, end_marker):
            open(lastrun_path, "w").write(future_lastrun)
            write_message("DONE!")
        else:
            write_message("Skipping prodsync: Redis queue is not yet empty")


def redis_sync(modified_records, time_estimator, tot, now, end_marker=None):
    """Sync to redis."""
    r = redis.StrictRedis.from_url(CFG_REDIS_HOST_LABS)
    if r.llen('legacy_records') != 0:
        return False
    for i, recid in enumerate(modified_records):
        with run_ro_on_slave_db():
            record = format_record(recid, 'xme', user_info=ADMIN_USER_INFO)[0]
        if not record:
            write_message("Error formatting record {0} as 'xme': {1}".format(
                recid, record
            ))
        else:
            r.rpush('legacy_records', zlib.compress(record))
            r.hset("legacy_records_last_sync", recid, now)
        if shall_sleep(recid, i, tot, time_estimator):
            task_sleep_now_if_required()
    if end_marker:
        r.rpush('legacy_records', end_marker)
    return True


def afs_sync(modified_records, time_estimator, tot, now):
    """Sync to AFS."""
    write_message("Appending output to %s" % CFG_OUTPUT_PATH)
    prodsyncname = CFG_OUTPUT_PATH + now.strftime("%Y%m%d%H%M%S") + '.xml.gz'
    r = gzip.open(prodsyncname, "w")
    print >> r, '<collection xmlns="http://www.loc.gov/MARC21/slim">'
    for i, recid in enumerate(modified_records):
        with run_ro_on_slave_db():
            record = format_record(recid, 'xme', user_info=ADMIN_USER_INFO)[0]
        if not record:
            write_message("Error formatting record {0} as 'xme': {1}".format(
                recid, record
            ))
        else:
            print >> r, record
        if shall_sleep(recid, i, tot, time_estimator):
            r.flush()
            task_sleep_now_if_required()
    print >> r, '</collection>'
    r.close()
    prodsync_tarname = CFG_OUTPUT_PATH + '.tar'
    write_message("Adding %s to %s" % (prodsyncname, prodsync_tarname))
    prodsync_tar = tarfile.open(prodsync_tarname, 'a')
    prodsync_tar.add(prodsyncname)
    prodsync_tar.close()
    os.remove(prodsyncname)


def shall_sleep(recid, i, tot, time_estimator):
    """Check if we shall sleep"""
    time_estimation = time_estimator()[1]
    if (i + 1) % 100 == 0:
        task_update_progress("%s (%s%%) -> %s" % (recid, (i + 1) * 100 / tot, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_estimation))))
        return True
    return False
