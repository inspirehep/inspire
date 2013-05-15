# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2009, 2010, 2011 CERN.
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

"""Unit tests for Bibtex

"""

__revision__ = \
    "$Id$"

import re
import unittest
import Bibtex

class TestBibtex(unittest.TestCase):
    """Tests for Bibtex.

    """

    def test_get_references1(self):
        """ test get_references

        """
        lines = r"""
\cite{Szczygiel:2012ra}

\cite{Rott:2011zz}"""
        expected = ['Szczygiel:2012ra', 'Rott:2011zz']

        ret = Bibtex.get_references(lines) 
        print '\ntest1\n'
        print lines + '\n'
        print ret
        self.assertEqual(expected, ret)


    def test_get_references2(self):
        """ test get_references

        """
        lines = r"\cite{Szczygiel:2012ra}\n\cite{Rott:2011zz}"
        expected = ['Szczygiel:2012ra', 'Rott:2011zz']

        ret = Bibtex.get_references(lines) 
        print '\ntest2\n'
        print lines + '\n'
        print ret
        self.assertEqual(expected, ret)

    def test_get_references3(self):
        """ test get_references

        """
        lines = r"""\cite{Szczygiel:2012ra}\n\cite{Rott:2011zz, hep-th/9711200}"""
        expected = ['Szczygiel:2012ra', 'Rott:2011zz', 'hep-th/9711200']

        ret = Bibtex.get_references(lines)
        print '\ntest3\n'
        print lines + '\n'
        print ret
        self.assertEqual(expected, ret)

    def test_get_references4(self):
        """ test get_references

        """
        print '\ntest4\n'
        return
        latex_file = open('1234.txt')
        lines = latex_file.read()
        latex_file.close()
        expected =  ['delAguila:1990yw', "D'Ambrosio:2002ex", 'hep-th/9711200',
                    'hep-ph/9501251', 'arXiv:0710.0554', 'PRPLC.110.1', 
                    'Martin:1997ns', 'Lafaye:2004cn', 'Adam:2010uz', 
                    'Baer:2003wx', 'Carena:1996km', 'Carena:2010gr', 
                    'Ellis:1981ts', 'Foster:2005wb', 'Giudice:1998bp', 
                    'Wagner:1998vd', 'Meade:2008wd', 'Balazs:2010ha', 
                    'Demir:2004aq', 'Martin:1993zk']
        ret = Bibtex.get_references(lines) 
        print ret
        self.assertEqual(expected, ret)
        
    def test_process_references(self):
        """ test get_references

        """
        print '\ntest5\n'
        refs = ['Szczygiel:2012ra', 'Rott:2011zz']
        ret = Bibtex.process_references(refs, 'hx')
        is_true = '@article{Szczygiel:2012ra,' in ret
        self.assertTrue(is_true)
        is_true2 = '@article{Rott:2011zz,' in ret
        self.assertTrue(is_true2)


    def test_remove_comments_regexp(self):
        """ test get_references

        """
        print '\ntest6\n'        
        #strip TeX comments from text strings, possibly multiline
        tests = []
        comment1 = r'% simple comment'
        comment2 = r'this is 99\% of all'
        comment3 = """
        \documentclass{article}
        % this is my article
        \\begin{document}
        some intro % need to fix
        but 90\% is already ok"""

        comment4 = 'line1\n%comment1\nline2%comment2\n\%line3\n'
        tests.append(comment1)
        tests.append(comment2)
        tests.append(comment3)
        tests.append(comment4)
        expected = []
        expected.append('')
        expected.append('this is 99\% of all')
        expected.append("""
        \documentclass{article}
        
        \\begin{document}
        some intro 
        but 90\% is already ok""")  

        expected.append('line1\n\nline2\n\%line3\n')
       
        #strip TeX comments from text strings, possibly multiline
        cstrip = re.compile(r'(?<!\\)%.*$', re.M)
        for i in range(0, 4):
            ret = cstrip.sub('', tests[i])
            self.assertEqual(expected[i], ret)
    
    def test_get_ref_regxep(self):
        """ Test for finding all references with a regexp

        """
        print '\ntest7\n'
        lines = r"""


        \begin{itemize}

        \item Electroweak physics \begin{itemize}

        \item Composite Higgs \cite{Foadi:2012ga,Frandsen:2012rj,Andersen:2011nk,Frandsen:2011hj,Hapola:2011sd,

        Jarvinen:2010ks,Frandsen:2009fs,Chivukula:2010qy,Antipin:2010it
        ,Antipin:2011aa,DiChiara:2010xb,Sannino:2010fh,Sannino:2010ca,Dietrich:2009af}.

        """
        expected = """Foadi:2012ga,Frandsen:2012rj,Andersen:2011nk,Frandsen:2011hj,Hapola:2011sd,

        Jarvinen:2010ks,Frandsen:2009fs,Chivukula:2010qy,Antipin:2010it
        ,Antipin:2011aa,DiChiara:2010xb,Sannino:2010fh,Sannino:2010ca,Dietrich:2009af"""

        cites = re.findall(r'\\cite\s*\{(.*?)\}', lines, re.M|re.DOTALL)

        self.assertEqual(expected, str(cites[0]))


    def test_search_texkey(self):
        """ test case for a texkey

        """
        print '\ntest8\n'
        lines = r"""
	        \cite{Schneider:2013iba}
        """
        refs = Bibtex.get_references(lines)
        ret = Bibtex.process_references(refs, 'hx')
        self.assertTrue(ret.index(r'@article'))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
