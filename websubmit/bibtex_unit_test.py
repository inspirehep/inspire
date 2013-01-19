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

"""Unit tests for Bibtex"""

__revision__ = \
    "$Id$"

import unittest
import Bibtex
import re
class TestBibtex(unittest.TestCase):
    """Tests for Bibtex."""

    def test_get_references1(self):
        lines = """
\cite{Szczygiel:2012ra}

\cite{Rott:2011zz}"""
        expected = ['Szczygiel:2012ra', 'Rott:2011zz']

        ret = Bibtex.get_references(lines) 
        print '\ntest1\n'
        print lines + '\n'
        print ret
        self.assertEqual(expected, ret)


    def test_get_references2(self):
        lines = """\cite{Szczygiel:2012ra}\n\cite{Rott:2011zz}"""
        expected = ['Szczygiel:2012ra', 'Rott:2011zz']

        ret = Bibtex.get_references(lines) 
        print '\ntest2\n'
        print lines + '\n'
        print ret
        self.assertEqual(expected, ret)

    def test_get_references3(self):
        lines = """\cite{Szczygiel:2012ra}\n\cite{Rott:2011zz, hep-th/9711200}"""
        expected = ['Szczygiel:2012ra', 'Rott:2011zz', 'hep-th/9711200']

        ret = Bibtex.get_references(lines)
        print '\ntest3\n'
        print lines + '\n'
        print ret
        self.assertEqual(expected, ret)

    def test_get_references4(self):
        print '\ntest4\n'
        return
        #f = open('1011.4958.tex')
        f = open('1234.txt')
        lines = f.read()
        #expected = ['delAguila:1990yw', "D'Ambrosio:2002ex", 'hep-th/9711200', 'hep-ph/9501251', 'arXiv:0710.0554', 'PRPLC.110.1', 'Martin:1997ns', 'Lafaye:2004cn', 'Adam:2010uz', 'Baer:2003wx', 'Carena:1996km', 'Carena:2010gr', 'Chattopadhyay:2003xi', 'Ellis:2004bx', 'Battaglia:2003ab', 'Djouadi:2006be', 'Baltz:2006fm', 'Allanach:2007qk', 'Berger:2008cq', 'Kneur:2008ur', 'Kneur:1998gy', 'Blair:2002pg', 'Blair:2005ui', 'Ellis:1981ts', 'Foster:2005wb', 'Giudice:1998bp', 'Wagner:1998vd', 'Meade:2008wd', 'Balazs:2010ha', 'Demir:2004aq', 'Martin:1993zk', 'Rauch:2007xp']
        expected =  ['delAguila:1990yw', "D'Ambrosio:2002ex", 'hep-th/9711200', 'hep-ph/9501251', 'arXiv:0710.0554', 'PRPLC.110.1', 'Martin:1997ns', 'Lafaye:2004cn', 'Adam:2010uz', 'Baer:2003wx', 'Carena:1996km', 'Carena:2010gr', 'Ellis:1981ts', 'Foster:2005wb', 'Giudice:1998bp', 'Wagner:1998vd', 'Meade:2008wd', 'Balazs:2010ha', 'Demir:2004aq', 'Martin:1993zk']
        ret = Bibtex.get_references(lines) 
        print ret
        #self.assertEqual(expected, ret)
        
    def test_process_references(self):
        print '\ntest5\n'
        refs = ['Szczygiel:2012ra', 'Rott:2011zz']
        format = 'hx'
        ret = Bibtex.process_references(refs, format)
        t = '@article{Szczygiel:2012ra,' in ret
        self.assertTrue(t)
        t2 = '@article{Rott:2011zz,' in ret
        self.assertTrue(t2)


    def test_remove_comments_regexp(self):
        print '\ntest6\n'        
        """ strip TeX comments from text strings, possibly multiline"""
        tests = []

        tests.append('% simple comment')
        tests.append('this is 99\% of all')
        tests.append("""
        \documentclass{article}
        % this is my article
        \\begin{document}
        some intro % need to fix
        but 90\% is already ok""")

        tests.append('line1\n%comment1\nline2%comment2\n\%line3\n')

        expected = []
        expected.append('')
        expected.append('this is 99\% of all')
        expected.append("""
        \documentclass{article}
        
        \\begin{document}
        some intro 
        but 90\% is already ok""")  

        expected.append('line1\n\nline2\n\%line3\n')
       
        """ strip TeX comments from text strings, possibly multiline"""
        cstrip = re.compile(r'(?<!\\)%.*$',re.M)
        for i in range(0,4):
            ret = cstrip.sub('',tests[i])
            self.assertEqual(expected[i], ret)
    
    def test_get_ref_regxep(self):
        print '\ntest7\n'
        lines = """


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

def main():
    unittest.main()

if __name__ == '__main__':
    main()
