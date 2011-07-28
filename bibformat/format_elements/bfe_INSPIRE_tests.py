# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""
BibFormat element tests - Prints a custom field
"""

import re
import unittest
from invenio.testutils import make_test_suite, run_test_suite
from invenio.bibformat_engine import BibFormatObject

class TestInspireFormatElements(unittest.TestCase):
    """Test cases for INSPIRE format elements. 
    Depends on default inspire test records (~1000)"""

    def testFieldRetrieval(self):
        """bfeField retrieval"""
        self.bfo = BibFormatObject('1')
        self.assertEqual(self.bfo.field('100a'),"Sachdev, Subir")

    def testarXiv(self):
        """INSPIRE arXiv format"""
        from bfe_INSPIRE_arxiv import format_element
        self.bfo = BibFormatObject('1')
        string = format_element(self.bfo)
        self.assert_(re.search(r'0299',string))
        self.assert_(not re.search(r'CERN',string))
        self.assert_(re.search(r'hep-th',string))

    def testDate(self):
        """INSPIRE date format"""
        from bfe_INSPIRE_date import format_element, parse_date
        # Test parse date function
        self.assert_(not parse_date(None))
        self.assert_(not parse_date(""))
        self.assert_(not parse_date("This is bad input"))
        self.assert_(not parse_date([1,2,4,"test"]))
        self.assert_(parse_date("2003-05-02") == (2003,5,2))
        self.assert_(parse_date("20030502") == (2003,5,2))
        self.assert_(parse_date("2003-05") == (2003,5))
        self.assert_(parse_date("200305") == (2003,5))
        self.assert_(parse_date("2003") == (2003,))
        # Expect date from 269__$$c
        self.bfo = BibFormatObject('1')
        string = format_element(self.bfo)
        self.assert_(re.search(r'Dec 2010',string))

    def testLinks(self):
        """testing INSPIRE Links"""
        from bfe_INSPIRE_links import format_element
        self.bfo=BibFormatObject('1')
        string = format_element(self.bfo, separator='</li>\n<li>', prefix="<ul><li>",suffix="</li></ul>")
        self.assert_(re.search(r'1012.0299">Abstract<',string))
        self.assert_(re.search(r'arXiv:1012.0299">PDF</a> from arXiv.org',string))

TEST_SUITE = make_test_suite(TestInspireFormatElements)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)



