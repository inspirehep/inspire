#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2016 CERN.
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

""" Bibcheck plugin checking that reference info in 999C50 agrees with
    citation info in 999C5r and 999C5s
"""

import re
from collections import defaultdict, namedtuple

from invenio.intbitset import intbitset
from invenio.search_engine import (get_collection_reclist, search_pattern,
                                   search_unit)

Reftags = namedtuple('Reftags', 'pubnote repno DOI citedrecid curatorflag')
FIELDS = Reftags('999C5s', '999C5r', '999C5a', '999C50', '999C59')


HEPRECS = get_collection_reclist('HEP')

CATEGORY = re.compile(ur'^(.*)\[[^\]]+\]')
ARXIVPREFIX = re.compile(ur'^(arXiv:(\s+)?)\D', re.I)


class Reference(object):
    """ container for various ref info """
    def __init__(self):
        self._fields = defaultdict(list)


    @staticmethod
    def normalize_repno(repno):
        """ cast repno into standard form """

        # normalize "arXiv:1612.12345 [hep-th]"
        categorymatch = CATEGORY.match(repno)
        if categorymatch:
            repno = categorymatch.group(1).strip()
        # strip arXiv prefix from old identifiers
        prefixmatch = ARXIVPREFIX.match(repno)
        if prefixmatch:
            repno = repno[len(prefixmatch.group(1)):]

        return repno

    @staticmethod
    def normalize_doi(doi):
        """ strip 'doi:' prefix from DOIs """
        if doi.lower().startswith('doi:'):
            return doi[len('doi:'):]
        return doi


    def add_info(self, key, value):
        """ add info from subfield to list of values """
        if key == 'repno':
            value = self.normalize_repno(value)
        elif key == 'DOI':
            value = self.normalize_doi(value)
        self._fields[key] += [value]


    def get_info(self, key, pos=0):
        """ return value of subfield at position pos """
        if self._fields[key]:
            return self._fields[key][pos]


    def get_all_info(self, key):
        """ return all subfield values for key """
        return self._fields[key]


    def get_hitset(self, key, pos=None):
        """ perform key appropriate search and return hitlist """
        if not self._fields[key]:
            return intbitset()
        if pos is None:
            pos = slice(None, None)
        hits = intbitset()
        if key == 'pubnote':
            for val in self._fields[key][pos]:
                hits |= search_pattern(f='journal', p=val, ap=1)
        elif key == 'repno':
            for val in self._fields[key][pos]:
                hits |= search_unit(f='reportnumber', p=val)
        elif key == 'DOI':
            for val in self._fields[key][pos]:
                hits |= search_unit(f='doi', p=val, m='a')

        return hits & HEPRECS


    def stringify(self):
        """ serialize ref info to string """
        refstring = []
        for key in FIELDS._fields:
            refstring.extend(['${0}{1}'.format(FIELDS.__getattribute__(key)[-1], val)
                              for val in self.get_all_info(key)])
        return ', '.join(refstring)


def check_record(record):
    """ check internal consistency of references """

    references = defaultdict(Reference)

    for pos, val in record.iterfield('999C5%'):
        for name in FIELDS._fields:
            if pos[0] == FIELDS.__getattribute__(name):
                references[pos[1]].add_info(name, val)

    for pos, ref in references.iteritems():
        allhits = [(k, ref.get_hitset(k)) for k in FIELDS._fields[:3]]
        for k, hits in allhits:
            if len(hits) > 1 and len(hits) > len(ref.get_all_info(k)):
                record.warn('more matches than values for refno %d %s "%s"'
                            % (pos, k, ' '.join(ref.get_all_info(k),)))

        hits = intbitset()
        for res in allhits:
            hits |= res[1]
        if hits and len(hits) != 1:
            abbrv = len(hits) > 8 and ', ...' or ''
            record.warn('multiple hits for refno %d [%s%s]\n\t%s'
                        % (pos, ', '.join((str(id) for id in hits[:8])), abbrv,
                           ref.stringify()))

        citedrecid = ref.get_info('citedrecid')
        if citedrecid:
            try:
                citedrecid = int(citedrecid)
            except ValueError:
                record.warn('non-numeric value in 999C50, should be recid: "%s"'
                            % (citedrecid,))
                continue
            if hits and citedrecid not in hits:
                abbrv = len(hits) > 8 and ', ...' or ''
                record.warn('mismatching info for refno %d "999C50:%s" not in [%s%s]\n\t%s'
                            % (pos, citedrecid, ', '.join((str(id) for id in hits[:8])),
                               abbrv, ref.stringify()))
