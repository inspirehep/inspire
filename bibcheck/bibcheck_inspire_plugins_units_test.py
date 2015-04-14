# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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


"""BibTask Inspires plugins Test Suite."""

__revision__ = "$Id$"

from invenio.testutils import make_test_suite, run_test_suite, InvenioTestCase
from invenio.bibcheck_plugins import atlas_authors, \
                                     journal_names
from invenio.bibcheck_task import AmendableRecord
from invenio.bibrecord import record_add_field

MOCK_RECORD = {
    '001': [([], ' ', ' ', '1', 7)],
    '005': [([], ' ', ' ', '20130621172205.0', 7)],
    '100': [([('a', 'Photolab '),
              ('c', '')], ' ', ' ', '', 7)],  # Trailing spaces
    '245': [([('a', ''), ('b', '')], ' ', ' ', '', 7)],  # remove-empty-fields
    '260': [([('c', '2000-06-14')], ' ', ' ', '', 7)],
    '261': [([('c', '14 Jun 2000')], ' ', ' ', '', 7)],
    '262': [([('c', '14 06 00')], ' ', ' ', '', 7)],
    '263': [([('c', '2000 06 14')], ' ', ' ', '', 7)],
    '264': [([('c', '1750 06 14')], ' ', ' ', '', 7)],
    '265': [([('c', '2100 06 14')], ' ', ' ', '', 7)],
    '340': [([('a', 'FI\xc3\x28LM')], ' ', ' ', '', 7)],  # Invalid utf-8
    '595': [([('a', ' Press')], ' ', ' ', '', 7)],  # Leading spaces
    '653': [([('a', 'LEP')], '1', ' ', '', 7)],
    '700': [([('a', 'Bella, Ludovica Aperio'),
              ('c', '')], ' ', ' ', '', 7)],  # remove-empty-fields
    '856': [([('f', 'neil.calder@cern.ch')], '0', ' ', '', 7)],
    '994': [([('u', 'http://httpstat.us/200')], '4', ' ', '', 7)],  # Url that works
    '995': [([('u', 'www.google.com/favicon.ico')], '4', ' ', '', 7)],  # url without protocol
    '996': [([('u', 'httpstat.us/301')], '4', ' ', '', 7)],   # redirection without protocol
    '997': [([('u', 'http://httpstat.us/404')], '4', ' ', '', 7)],  # Error 404
    '998': [([('u', 'http://httpstat.us/500')], '4', ' ', '', 7)],  # Error 500
    '999': [([('u', 'http://httpstat.us/301')], '4', ' ', '', 7)],  # Permanent redirect
    '999': [([('a', '5345435'),
              ('i', '52345235'),
              ('r', '4243424'),
              ('s', 'fsdf.gfdfgsdfg.'),
              ('0', '2')], 'C', '5', '', 7),
            ([('a', 'mplampla')], 'C', '5', '', 8)]
}

RULE_MOCK = {
    "name": "test_rule",
    "holdingpen": True
}


class BibCheckInspirePluginsTest(InvenioTestCase):
    """ Bibcheck default plugins test """

    def assertAmends(self, test, changes, **kwargs):
        """
        Assert that the plugin "test" amends the mock record when called with
        params kwargs.
        """
        record = AmendableRecord(MOCK_RECORD)
        record.set_rule(RULE_MOCK)
        test.check_record(record, **kwargs)
        self.assertTrue(record.amended)
        self.assertEqual(len(record.amendments), len(changes))
        for field, val in changes.iteritems():
            if val is not None:
                self.assertEqual(
                    ((field, 0, 0), val),
                    list(record.iterfield(field))[0]
                )
            else:
                self.assertEqual(len(list(record.iterfield(field))), 1)

    def test_atlas_authors(self):
        """ atlas_authors plugin test """
        self.assertAmends(atlas_authors, {'700__a': 'Aperio Bella, Ludovica'})

    def test_journal_names(self):
        """ journal_names plugin test """
        rec = {}
        record_add_field(rec, '773', subfields=[('p', 'JHEP')])
        record_add_field(rec, '001', controlfield_value='111')
        record_add_field(rec, '999', ind1='C', ind2='5', subfields=[('s', 'JHEP,a,b')])
        rec = AmendableRecord(rec)
        rec.set_rule(RULE_MOCK)
        journal_names.check_records([rec])
        self.assertEqual(rec.valid, True)

        #773__p JHEP2 journal does not exist
        rec = {}
        record_add_field(rec, '773', subfields=[('p', 'JHEP2')])
        record_add_field(rec, '001', controlfield_value='111')
        record_add_field(rec, '999', ind1='C', ind2='5', subfields=[('s', 'JHEP,a,b')])
        rec = AmendableRecord(rec)
        rec.set_rule(RULE_MOCK)
        journal_names.check_records([rec])
        self.assertEqual(rec.valid, False)

        #999C5s has 3 commas
        rec = {}
        record_add_field(rec, '773', subfields=[('p', 'JHEP')])
        record_add_field(rec, '001', controlfield_value='111')
        record_add_field(rec, '999', ind1='C', ind2='5', subfields=[('s', 'JHEP,a,b,c')])
        rec = AmendableRecord(rec)
        rec.set_rule(RULE_MOCK)
        journal_names.check_records([rec])
        self.assertEqual(rec.valid, False)

        #999C5s JHEP2 journal does not exist
        rec = {}
        record_add_field(rec, '773', subfields=[('p', 'JHEP')])
        record_add_field(rec, '001', controlfield_value='111')
        record_add_field(rec, '999', ind1='C', ind2='5', subfields=[('s', 'JHEP2,a,b')])
        rec = AmendableRecord(rec)
        rec.set_rule(RULE_MOCK)
        journal_names.check_records([rec])
        self.assertEqual(rec.valid, False)

        #773__p only the journal name must be in this field
        rec = {}
        record_add_field(rec, '773', subfields=[('p', 'JHEP,a,b')])
        record_add_field(rec, '001', controlfield_value='111')
        record_add_field(rec, '999', ind1='C', ind2='5', subfields=[('s', 'JHEP,a,b')])
        rec = AmendableRecord(rec)
        rec.set_rule(RULE_MOCK)
        journal_names.check_records([rec])
        self.assertEqual(rec.valid, False)

TEST_SUITE = make_test_suite(BibCheckInspirePluginsTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
