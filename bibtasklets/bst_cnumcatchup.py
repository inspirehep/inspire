# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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

"""Refresh cached HB format for specific HEP records

Ensure that cached brief format of HEP records is updated when secondary
information in Conferences collection or in Proceedings records are modified.
The common connection is a cnum.
"""

from invenio.bibtaskutils import task_low_level_submission
from invenio.dbquery import run_sql
from invenio.intbitset import intbitset
from invenio.search_engine import get_collection_reclist, \
    get_fieldvalues, \
    perform_request_search


def bst_cnumcatchup():
    modrecs = intbitset([x[0] for x in
                         run_sql('select id from bibrec where ' +
                                 'modification_date >' +
                                 'DATE_SUB(CURDATE(), INTERVAL 3 DAY)')])

    confupd = intbitset(get_collection_reclist('Conferences')) \
        & modrecs
    procupd = intbitset(perform_request_search(p="980__a:Proceedings")) \
        & modrecs

    cnums = []
    for r in confupd:
        for c in get_fieldvalues(r, '111__g'):
            if len(c) > 3:
                cnums.append(c)
    for r in procupd:
        for c in get_fieldvalues(r, '773__w'):
            if len(c) > 3:
                cnums.append(c)

    recs = intbitset()
    for cn in cnums:
        recs += intbitset(perform_request_search(p="find cnum %s" % cn))

    if recs:
        while len(recs) > 500:
            nextchunk = recs[:500]
            recs = recs[500:]
            task_low_level_submission('bibreformat',
                                      'bibreformat:bstcnumcatchup',
                                      '-o', 'HB', '-i',
                                      ','.join([str(r) for r in nextchunk]))
        if recs:
            task_low_level_submission('bibreformat',
                                      'bibreformat:bstcnumcatchup',
                                      '-o', 'HB', '-i',
                                      ','.join([str(r) for r in recs]))

if __name__ == '__main__':
    bst_cnumcatchup()
