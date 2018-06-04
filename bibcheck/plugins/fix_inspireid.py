# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015, 2018 CERN.
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
    (('a', 'De La Cruz, Begona'), ('i', 'INSPIRE-00091968', 'INSPIRE-00075124')),
    (('a', 'Meyer, Joerg'), ('i', 'INSPIRE-00220381', 'INSPIRE-00107296')),
    (('a', 'Pastore, Fernanda'), ('i', 'INSPIRE-00221618', 'INSPIRE-00221629')),
    (('a', 'Kumar, Vineet'), ('i', 'INSPIRE-00170162', 'INSPIRE-00536498')),
    (('a', 'Thompson, Paul'), ('i', 'INSPIRE-00224430', 'INSPIRE-00185894')),
    (('a', 'Giorgi, Francesco Michelangelo'), ('i', 'INSPIRE-00214779', 'INSPIRE-00537048')),
    (('a', 'Mohanty, Ajit Kumar'), ('i', 'INSPIRE-00170359', 'INSPIRE-00170162')),
    (('a', 'Liang, Zhihua'), ('i', 'INSPIRE-00219122', 'INSPIRE-00219104')),
    (('a', 'Navarro, Jose Enrique Garcia'), ('i', 'INSPIRE-00083629', 'INSPIRE-00022084')),
    (('a', 'Kim, Hyunchul'), ('i', 'INSPIRE-00317156', 'INSPIRE-00350129')),
    (('a', 'Duren, Michael'), ('i', 'INSPIRE-00213763', 'INSPIRE-00078621')),
    (('a', 'Ferrando, Belen Salvachua'), ('i', 'INSPIRE-00222878', 'INSPIRE-00222882')),
    (('a', 'Llacer, Maria Moreno'), ('i', 'INSPIRE-00220759', 'INSPIRE-00332523')),
    (('a', 'Llacer, Maria Moreno'), ('a', 'Llacer, Maria Moreno', 'Moreno Llácer, María')),
    (('a', 'Wilson, A.'), ('i', 'INSPIRE-00154108', 'INSPIRE-00301349')),
    (('a', 'Kim, Hyeon Jin'), ('i', 'INSPIRE-00019770', 'INSPIRE-00020720')),
    (('a', 'Yu, Jaehoon'), ('i', 'INSPIRE-00226216', 'INSPIRE-00137749')),
    (('a', 'Tasevsky, Marek'), ('i', 'INSPIRE-00226974', 'INSPIRE-00224260')),
    (('a', 'Grynyov, Boris'), ('i', 'INSPIRE-00204440', 'INSPIRE-00245887')),
    (('a', 'Richter, Robert'), ('i', 'INSPIRE-00120014', 'INSPIRE-00120026')),
    (('a', 'Richter, Rainer Helmut'), ('i', 'INSPIRE-00120026', 'INSPIRE-00120014')),
    (('a', 'Richter, R.H.'), ('i', 'INSPIRE-00120026', 'INSPIRE-00120014')),
    (('a', 'Beddall, A.J.'), ('i', 'INSPIRE-00211268', 'INSPIRE-00065527')),
    (('a', 'Smith, Mark'), ('i', 'INSPIRE-00261920', 'INSPIRE-00342046')),
    (('a', 'Han, Liang'), ('i', 'INSPIRE-00468525', 'INSPIRE-00037384')),
    (('a', 'Han, L.'), ('i', 'INSPIRE-00468525', 'INSPIRE-00037384')),
    (('a', 'Wang, Dong-Gang'), ('i', 'INSPIRE-00037384', 'INSPIRE-00468525')),
    (('a', 'Stan, Ionel'), ('i', 'INSPIRE-00291820', 'INSPIRE-00434447')),
    (('a', 'Deng, Jianrong'), ('i', 'INSPIRE-00046433', 'INSPIRE-00624635')),
    (('a', 'Martin, Andrew'), ('i', 'INSPIRE-00219939', 'INSPIRE-00105075')),
    (('a', 'Golovanov, Georgy Anatolievich'), ('i', 'INSPIRE-00038818', 'INSPIRE-00018415')),
    (('a', 'Shou, Qi-Ye'), ('i', 'INSPIRE-00538694', 'INSPIRE-00565745')),
    (('u', 'Mainz U.'), ('i', 'INSPIRE-00320516', 'INSPIRE-00336767')),
    (('a', 'Mc Kee, Shawn Patrick'), ('i', 'INSPIRE-00106342', 'INSPIRE-00260714')),
    (('a', 'Parodi, Fabrizio'), ('i', 'INSPIRE-00214233', 'INSPIRE-00339598')),
    (('a', 'Ferretto Parodi, Andrea'), ('i', 'INSPIRE-00339598', 'INSPIRE-00214233')),
    (('a', 'Liu, Jie'), ('i', 'INSPIRE-00447072', 'INSPIRE-00450250')),
    (('u', 'U. Zurich'), ('i', 'INSPIRE-00453848', 'INSPIRE-00640989')),
    (('u', 'Zurich U.'), ('i', 'INSPIRE-00453848', 'INSPIRE-00640989')),
    (('a', 'Unverdorben, Christopher'), ('i', 'INSPIRE-00333620', 'INSPIRE-00530015')),
    (('a', 'Lumb, Debra'), ('i', 'INSPIRE-00219481', 'INSPIRE-00509017')),
    (('a', 'Lumb, D.'), ('i', 'INSPIRE-00219481', 'INSPIRE-00509017')),
    (('a', 'Skovpen, Yuri'), ('i', 'INSPIRE-00517102', 'INSPIRE-00042992')),
    (('a', 'Kennedy, Elizabeth'), ('i', 'INSPIRE-00389170', 'INSPIRE-00389690')),
    (('u', 'Duke U.'), ('i', 'INSPIRE-00046433', 'INSPIRE-00624635')),
    (('u', 'UC, Irvine'), ('i', 'INSPIRE-00046433', 'INSPIRE-00624635')),
    (('u', 'Michigan Tech. U.'), ('i', 'INSPIRE-00150592', 'INSPIRE-00255332')),
    (('a', 'Cabrera Urbán, Susana'), ('i', 'INSPIRE-00307975', 'INSPIRE-00211900')),
    (('a', 'Cabrera Urban, Susana'), ('i', 'INSPIRE-00307975', 'INSPIRE-00211900')),
    (('u', 'CERN'), ('i', 'INSPIRE-00023123', 'INSPIRE-00493662')),
    (('u', 'IRFU, Saclay'), ('i', 'INSPIRE-00220215', 'INSPIRE-00657399')),
    (('u', 'DAPNIA, Saclay'), ('i', 'INSPIRE-00220215', 'INSPIRE-00657399'))
    ]


def check_records(records):
    for record in records:
        for subfield_filter, (code, pattern, replace) in CHANGES:
            record.update_subfields(fields=["100__%s" % code, "700__%s" % code],
                                    pattern="^%s$" % re.escape(pattern),
                                    replace=replace,
                                    subfield_filter=subfield_filter)


