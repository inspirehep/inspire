# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015, 2016 CERN.
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

"""
Dump all INSPIRE records so that they are available via HTTP.
"""

import os
import gzip
import time

from invenio.search_engine import get_collection_reclist
from invenio.config import CFG_WEBDIR, CFG_SITE_URL
from invenio.bibformat_engine import format_record
from invenio.dateutils import get_time_estimator
from invenio.bibtask import write_message, task_update_progress, task_sleep_now_if_required
from invenio.bibdocfile import calculate_md5

CFG_EXPORTED_COLLECTIONS = ['HEP', 'HepNames', 'Institutions', 'Conferences',
                            'Jobs', 'Experiments', 'Journals', 'Data']


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


def bst_dump_records():
    try:
        os.makedirs(os.path.join(CFG_WEBDIR, 'dumps'))
    except OSError:
        pass
    html_index = open(os.path.join(CFG_WEBDIR, 'dumps', '.inspire-dump.html'), "w")
    print >> html_index, "<html><head><title>INSPIRE Dump</title></head><body><ul>"
    for collection in CFG_EXPORTED_COLLECTIONS:
        task_update_progress(collection)
        print >> html_index, """
<li><a href="%(prefix)s/dumps/%(collection)s-records.xml.gz">%(collection)s</a>
(<a href="%(prefix)s/dumps/%(collection)s-records.xml.gz.md5">MD5</a>): %(date)s</li>""" % {
    'prefix': CFG_SITE_URL,
    'collection': collection,
    'date': time.ctime()
}
        write_message("Preparing %s-records.xml.gz" % collection)
        output_path = os.path.join(CFG_WEBDIR, 'dumps', '.%s-records.xml.gz' % collection)
        output = gzip.open(output_path, "w")
        print >> output, "<collection>"
        reclist = get_collection_reclist(collection)
        tot = len(reclist)
        time_estimator = get_time_estimator(tot)
        for i, recid in enumerate(reclist):
            with run_ro_on_slave_db():
                print >> output, format_record(recid, 'xme', user_info={})[0]
            time_estimation = time_estimator()[1]
            if (i + 1) % 100 == 0:
                task_update_progress("%s %s (%s%%) -> %s" % (collection, recid, (i + 1) * 100 / tot, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_estimation))))
                task_sleep_now_if_required()
        print >> output, "</collection>"
        output.close()
        write_message("Computing checksum")
        print >> open(output_path + '.md5', "w"), calculate_md5(output_path)
        os.rename(output_path, os.path.join(CFG_WEBDIR, 'dumps', '%s-records.xml.gz' % collection))
        os.rename(output_path + '.md5', os.path.join(CFG_WEBDIR, 'dumps', '%s-records.xml.gz.md5' % collection))
        write_message("DONE")
    print >> html_index, "</ul></body></html>"
    html_index.close()
    os.rename(os.path.join(CFG_WEBDIR, 'dumps', '.inspire-dump.html'), os.path.join(CFG_WEBDIR, 'dumps', 'inspire-dump.html'))
