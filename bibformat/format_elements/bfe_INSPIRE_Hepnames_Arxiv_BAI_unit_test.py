#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from invenio.testutils import make_test_suite, \
    run_test_suite
from invenio.bibformat_engine import BibFormatObject
from invenio.bibformat_elements import bfe_INSPIRE_Hepnames_Arxiv_BAI

TESTREC1 = """<collection><record><controlfield tag="001">981878
              </controlfield><datafield tag="035" ind1=" " ind2=" ">
              <subfield code="a">zwirner_f_1</subfield><subfield 
              code="9">arXiv</subfield></datafield></record></collection>
           """

TESTREC2 = """<collection><record><controlfield tag="001">982445
              </controlfield><datafield tag="035" ind1=" " ind2=" ">
              <subfield code="9">ARXIV</subfield>
              <subfield code="a">ARXIV-ZACHOS-C-1</subfield>
              </datafield></record></collection>
           """

TESTREC3 = """<collection><record><controlfield tag="001">1017924
              </controlfield></record></collection>
           """

TESTREC4 = """<collection><record><controlfield tag="001">982447
              </controlfield><datafield tag="035" ind1=" " ind2=" ">
              <subfield code="9">ARXIV</subfield>
              <subfield code="a"></subfield>
              </datafield></record></collection>
           """

ARXIV_BAI_TEST = {
    TESTREC1: '<a href="http://arxiv.org/a/zwirner_f_1">zwirner_f_1</a>',
    TESTREC2: '<a href="http://arxiv.org/a/ARXIV-ZACHOS-C-1">ARXIV-ZACHOS-C-1</a>',
    TESTREC3: None,
    TESTREC4: None,
}

class HepNames_arxiv_BAI_format_test(unittest.TestCase):
    def test4BAI_link(self):
        for key in ARXIV_BAI_TEST:
            bfo = BibFormatObject(None, xml_record=key)
            out = bfe_INSPIRE_Hepnames_Arxiv_BAI.format_element(bfo)
            self.assertEqual(ARXIV_BAI_TEST[key], out)

TEST_SUITE = make_test_suite(HepNames_arxiv_BAI_format_test)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
