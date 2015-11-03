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

"""BibCheck plugin to correct wrong INSPIRE IDs in HEP records"""

import re

# NOTE: restart the rule in case the following list is amended.
CHANGES = [
    #filter             : code, Replace this       , with this
    (('h', 'CCID-682355'), ('i', "INSPIRE-00000419", "INSPIRE-00536572")),
    (('a', 'Kim, Tae Jeong'), ('i', "INSPIRE-00170315", "INSPIRE-00046841")),
    (('a', 'Veres, Gabor Istvan'), ('i', "INSPIRE-00305474", "INSPIRE-00318264")),
    (('h', 'CCID-430246'), ('i', "INSPIRE-00305303", "INSPIRE-00124268")),
    (('h', 'CCID-620319'), ('i', "INSPIRE-00305303", "INSPIRE-00300239")),
    (('h', 'CCID-430246'), ('a', "Schmitt, Michael", "Schmitt, Michael Henry")),
    (('h', 'CCID-620319'), ('a', "Schmitt, Michael", "Schmitt, Michael Houston")),
    (('h', 'CCID-672739'), ('i', 'INSPIRE-00125649', 'INSPIRE-00316081')),
    (('a', 'Hu, Guofan'), ('i', 'INSPIRE-00176709', 'INSPIRE-00176990')),
    (('u', 'Michigan State U.'), ('a', 'Martin, Brian', 'Martin, Brian Thomas')),
    (('u', 'Michigan State U.'), ('i', 'INSPIRE-00227165', 'INSPIRE-00227142')),
    (('a', 'Crépé-Renaudin, Sabine'), ('i', 'INSPIRE-00212936', 'INSPIRE-00074993')),
    (('a', 'Düren, Michael'), ('i', 'INSPIRE-00213763', 'INSPIRE-00078621')),
    (('a', 'Zimmermann, Stephanie'), ('i', 'INSPIRE-00226484', 'INSPIRE-00226472')),
    (('a', 'Moreno Llácer, María'), ('i', 'INSPIRE-00220759', 'INSPIRE-00332523')),
    (('a', 'Tanaka, Satoshi'), ('i', 'INSPIRE-00224249', 'INSPIRE-00339347')),
    (('a', 'Malecki, Piotr'), ('i', 'INSPIRE-00219707', 'INSPIRE-00219719')),
    (('a', 'Beddall, Andrew'), ('i', 'INSPIRE-00211268', 'INSPIRE-00065527')),
    (('a', 'Bendavid, Joshua'), ('i', 'INSPIRE-00305138', 'INSPIRE-00307617')),
    ]


def check_records(records):
    for record in records:
        for subfield_filter, (code, pattern, replace) in CHANGES:
            record.update_subfields(fields=["100__%s" % code, "700__%s" % code],
                                    pattern="^%s$" % re.escape(pattern),
                                    replace=replace,
                                    subfield_filter=subfield_filter)


