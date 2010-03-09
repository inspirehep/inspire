# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element test - Prints a custom field
"""



import re
import unittest
from invenio.testutils import make_test_suite, run_test_suite
from invenio.bibformat_engine import BibFormatObject




class TestInspireFormatElements(unittest.TestCase):        #
        # Test case depends on inspires test records

        #test CERN_authors
        def testField(self):
            print """testing bfeField"""
            self.bfo=BibFormatObject('7374')
            self.assertEqual(self.bfo.field('100a'),"Farhi, E.")
        def testAff(self):
            """testing Affs"""
            from bfe_CERN_authors import format
            self.bfo=BibFormatObject('7374')
            string =  format(self.bfo,limit="5",print_affiliations="yes")

            self.assert_(re.search(r'Farhi, E.</a>',string))
            self.assert_(re.search(r'</a> \(<a.*MIT',string))




        #test INSPIRE_arXiv
        def testarX(self):
            """testing arXiv"""
            from bfe_INSPIRE_arxiv import format
            self.bfo=BibFormatObject('37650')
            string=format(self.bfo)
            print string
            self.assert_(re.search(r'3066',string))
            self.assert_(not re.search(r'CERN',string))
            self.assert_(re.search(r'hep-ph',string))


                    #test INSPIRE_date
        def testDate(self):
            """testing date"""
            from bfe_INSPIRE_date import format
            self.bfo=BibFormatObject('6194')
            string=format(self.bfo)
            print string
            string2=format(self.bfo,us="no")
            print string2
#            self.assert_(re.search(r'Jun 1, 1974',string))
#            self.assert_(re.search(r'01 Jun 1974',string2))

            #test INSPIRE_links
        def testLinks(self):
            """testing Links"""
            from bfe_INSPIRE_links import format
            self.bfo=BibFormatObject('37650')
            string= format(self.bfo, separator='</li>\n<li>', prefix="<ul><li>",suffix="</li></ul>")
            print string
            self.assert_(re.search(r'065201">Journal',string))
            self.assert_(re.search(r'\?bibcode=2004',string))


TEST_SUITE = make_test_suite(TestInspireFormatElements)


if __name__ == "__main__":
    run_test_suite(TEST_SUITE)



