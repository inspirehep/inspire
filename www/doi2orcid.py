# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

import csv

from invenio.search_engine import perform_request_search, get_fieldvalues
from invenio.dbquery import run_sql
from invenio.webpage import page
from invenio.bibsched_tasklets.bst_prodsync import run_ro_on_slave_db


def _get_data(doi_prefix):
    with run_ro_on_slave_db():
        recids = perform_request_search(p='0247_a:"%s/*"' % doi_prefix)
        personid_orcid_mapping = dict(run_sql("SELECT personid, data FROM aidPERSONIDDATA where tag='extid:ORCID'"))
        for recid in recids:
            dois = get_fieldvalues([recid], '0247_a', sort=False)
            personids = run_sql("SELECT personid, name FROM aidPERSONIDPAPERS WHERE bibrec=%s AND flag=2", (recid, ))
            for doi in dois:
                if doi.startswith(doi_prefix):
                    for personid, name in personids:
                        orcid = personid_orcid_mapping.get(personid)
                        if orcid:
                            yield doi, orcid, name

def index(req, doi_prefix=""):
    if not doi_prefix:
        body = """
<p>Given a DOI prefix (e.g. <tt>10.1088</tt>) this utility will generate in output a <tt>.CSV</tt> file with the following columns:
<table border="1">
<tr>
<td>DOI</td><td>ORCID</td><td>Corresponding signature</td>
</tr>
<table>
</p>
<p>For example this is a possible output for the <tt>doi_prefix=10.1088</tt>:
<pre>
10.1088/0305-4616/1/2/005,0000-0001-8064-9632,"McKellar, Bruce H.J."
10.1088/0305-4470/9/8/028,0000-0001-9526-1833,"Vayonakis, C.E."
10.1088/0305-4616/2/8/001,0000-0001-8064-9632,"McKellar, Bruce H.J."
10.1088/0305-4470/10/9/002,0000-0001-9285-9434,"Deser, Stanley"
10.1088/0305-4616/4/6/001,0000-0002-2563-9826,"Wetterich, C."
10.1088/0305-4616/5/6/002,0000-0002-0885-1868,"Weiler, Thomas J."
10.1088/0305-4616/4/7/001,0000-0002-3708-8283,"Davis, A.C."
10.1088/0305-4616/5/1/004,0000-0002-5330-6789,"Jarvis, Peter D."
10.1088/0305-4470/12/5/005,0000-0001-9285-9434,"Deser, Stanley"
...
</pre>
</p>
<p>The <tt>doi_prefix</tt> can be provided directly as a URL query argument. E.g.:
<a href="/doi2orcid.py?doi_prefix=10.1088">https://inspirehep.net/doi2orcid.py?doi_prefix=10.1088</a>.
</p>
<form>
<label for="doi_prefix">Enter the DOI Prefix: </label><input type="text" name="doi_prefix" placeholder="e.g. 10.1088" />
<input type="submit" />
"""
        return page(req=req, title="DOI 2 ORCID tool", body=body)
    req.content_type = 'text/csv; charset=utf-8'
    req.headers_out['content-disposition'] = 'attachment; filename=%s.csv' % doi_prefix
    csv_writer = csv.writer(req)
    csv_writer.writerows(_get_data(doi_prefix))
    return ""
