# -*- coding: utf-8 -*-
##
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
"""Testing SPIRES search syntax in Invenio
"""


import re
import unittest
from invenio.search_engine import perform_request_search
from invenio.search_engine_query_parser import SpiresToInvenioSyntaxConverter 
from invenio.search_engine_query_parser import SearchQueryParenthesisedParser 
spires=SpiresToInvenioSyntaxConverter()
parser=SearchQueryParenthesisedParser()

class filterTestclass(unittest.TestCase):        


        #test operator searching
        def test_operators(self):    
            self.inv_search="author:ellis and title:muon"
            self.spi_search="find a ellis and t muon"
            self._compare_searches()

        def test_parens(self):    
            self.inv_search="author:ellis and not (title:muon or title:kaon)"
            self.spi_search="find a ellis and not t muon and not t kaon "
            self._compare_searches()

        def test_author_simple(self):    
            self.inv_search='author:"brooks,t" or author:"brooks,t*"'
            self.spi_search="find a brooks, t"
            self._compare_searches()

        def test_author_reverse(self):    
            self.inv_search='author:"brooks,t"'
            self.spi_search="find a t. brooks"
            self._compare_searches()

        def test_author_full_first(self):    
            self.inv_search="author:'brooks, travis' or author:'brooks, t'"
            self.spi_search="find a brooks, travis"
            self._compare_searches()







        def _compare_searches(self):
            print "\n"+self.inv_search+" vs. "+self.spi_search
            self.assertTrue(len(perform_request_search(p=self.spi_search))>0)
            print "non zero result:good"
            self.assertEqual(perform_request_search(p=self.inv_search),perform_request_search(p=self.spi_search))
            print "equal results: better"
            if parser.parse_query(self.inv_search)==parser.parse_query(spires.convertQuery(self.spi_search)):
                print "identically parsed: best"
            else:
                print "non-identical parsing...otherwise ok"
    
            
unittest.main()




