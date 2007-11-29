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



import unittest
from bfe_field import format
from invenio.bibformat_engine import BibFormatObject
class filterTestclass(unittest.TestCase):
        #
        # Test case depends on inspires test records

        def setUp(self):
            self.bfo=BibFormatObject('001')
            print self.bfo.field('035a')
        def testField(self):
            self.assertEqual(self.bfo.field('100a'),"Delbourgo, R.")

        def testFilterVal(self):
            ##filters for bourgo,
            self.assertEqual(format(self.bfo,'100a',limit="2",filter_value=r'bourgo'),
                             "Delbourgo, R.")
            
        def testFilterSub(self):
            ## has affil, so should print author name
            self.assertEqual(format(self.bfo,'100a',limit="2",filter_subcode='u'),
                             "Delbourgo, R.")
            ## doesn't have 'b' should should print nothing
            self.assertEqual(format(self.bfo,'100a',limit="2",filter_subcode='b'),
                             '')
        def testFilterBoth(self):
               ## has affil of ICTP, so should print author name
            self.assertEqual(format(self.bfo,'100a',limit="2",filter_subcode='u',filter_value=r'ICTP, T'),
                             "Delbourgo, R.")
                           ## has affil of ICTP, so should not print author name
            self.assertEqual(format(self.bfo,'100a',limit="2",filter_subcode='u',filter_value=r'SLAC'),
                             '')
            
unittest.main()




