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
from invenio.search_engine import print_record
from invenio.bibtask import write_message, task_update_progress
from invenio.bibdocfile import calculate_md5

CFG_EXPORTED_COLLECTIONS = ['HEP', 'HepNames', 'Institutions', 'Conferences',
                            'Jobs', 'Experiments']

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
        for recid in get_collection_reclist(collection):
            print >> output, print_record(recid, 'xme', user_info={})
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
