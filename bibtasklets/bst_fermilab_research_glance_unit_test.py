#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
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

"""Here is the test file for insuring the script under test functions
as expected.  It executes the script, removes varying characters (numbers)
from the html file produced, converts that to a SHA224 hash and applies
assertTrue method to the hash and the expected hash.  If the two are the
same, the script passes the test.

"""

import unittest


class ResearchGlanceTests(unittest.TestCase):
    """Set of unit tests for fermilab_research_glance.py."""
    def test_dependencies(self):
        """verify that required modules can be imported"""
        modules = ('lxml', 'lxml.html', 'lxml.html.builder',
                   'datetime', 'dateutil.relativedelta', 'pytz',
                   'invenio.bibsched_tasklets.bst_fermilab_research_glance')
        module_import_err = []
        for module in modules:
            try:
                __import__(module)
            except ImportError:
                module_import_err.append('failed to import %s' % (module,))
        self.assertEqual(module_import_err, [],
                         "dependency errors: %s" %
                         (', '.join(module_import_err),))

    def test_output_directory_exists(self):
        """verify that the destination directory for the report exists"""
        import os.path
        from invenio.bibsched_tasklets.bst_fermilab_research_glance \
            import CFG_FERMILAB_PATH
        self.assertTrue(os.path.isdir(CFG_FERMILAB_PATH),
                        "The output destination is not a directory")

    def test_research_glance(self):
        """Compare expected output with actual output of
        fermilab_research_glance.py.

        """
        from invenio.bibsched_tasklets.bst_fermilab_research_glance \
            import create_table
        report = create_table()
        from lxml import html
        can_parse = True
        try:
            doc = html.document_fromstring(report)
        except:
            can_parse = False
        self.failUnless(can_parse,
                        "failed to parse the report with lxml.html")

        rootinfo = doc.getroottree().docinfo
        self.assertEqual(rootinfo.doctype, u'<!DOCTYPE html>',
                         "report has wrong doctype, should be html, "
                         + "found instead %s" % (rootinfo.doctype,))
        self.assertEqual(rootinfo.encoding.lower(), 'utf-8',
                         "report has wrong encoding, should be utf-8, "
                         + "found instead %s" % (rootinfo.encoding,))
        self.assertEqual(rootinfo.root_name, 'html',
                         "report has wrong root name, should be html, "
                         + "found instead %s" % (rootinfo.root_name,))
        tables = doc.xpath('body/table')
        self.assertEqual(len(tables), 2,
                         "did not find 2 top level tables")
        self.assertEqual(len(tables[0].xpath('tr')), 7,
                         "main table doesn't have 7 rows")
        self.assertEqual(len(tables[0].xpath('tr/td')), 105,
                         "main table doesn't have 105 td elements")
        rowlabels = ['', 'All', 'PUB', 'THESIS', 'CONF', 'TM', 'FN', 'SLIDES', 'POSTER']
        self.assertEqual([r.getchildren()[0].text_content()
                          for r in tables[0].xpath('tr')],
                         rowlabels,
                         "the row labels are not as expected")
        collabels = ['', 'Date', 'All', 'E', 'CMS', 'T', 'AT', 'AE', 'PPD',
                     'AD/APC', 'TD', 'CD', 'ND', 'LBN', 'Other']
        self.assertEqual([c.text_content()
                          for c in tables[0].xpath('tr')[0].getchildren()],
                         collabels,
                         "the column labels are not as expected")

if __name__ == '__main__':
    unittest.main()
