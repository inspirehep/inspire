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

""" Bibcheck plugin to add 980__a type-codes to records from journals that always
    contain published, conference, or review papers
"""
from invenio.bibcheck_task import AmendableRecord
from invenio.bibedit_utils import get_bibrecord
from invenio.search_engine import perform_request_search


JOURNAL_PUBLISHED_DICT = {"Ann.Rev.Nucl.Part.Sci.": None,
                          "Ann.Rev.Astron.Astrophys.": "10.1146/annurev-astro",
                          "Ann.Rev.Phys.Chem.": None,
                          "Ann.Rev.Fluid Mech.": None,
                          "Ann.Rev.Earth Planet.Sci.": None,
                          "Ann.Rev.Psych.": None,
                          "Ann.Rev.Mater.Sci.": None,
                          "Ann.Rev.Physiol.": None,
                          "Ann.Rev.Biophys.Biomol.Struct.": None,
                          "Ann.Rev.Condensed Matter Phys.": None,
                          "Ann.Rev.Biophys.": None,
                          "Ann.Rev.Biophys.Bioeng.": None,
                          "Astron.Astrophys.": "10.1051/0004-6361/",
                          "Astron.J.": "10.1088/0004-6256/",
                          "Astron.Astrophys.Suppl.Ser.": None,
                          "Astrophys.J.": "10.1088/0004-637X/",
                          "Astrophys.J.Suppl.": "10.1088/0067-0049/",
                          "Bull.Lebedev Phys.Inst.": None,
                          "Europhys.Lett.": "10.1209/0295-5075",
                          "JHEP": "10.1007/JHEP",
                          "Mon.Not.Roy.Astron.Soc.": "10.1093/mnras",
                          "Nature": "10.1038/nature",
                          "Nature Phys.": "10.1038/nphys",
                          #"Nucl.Phys.": "10.1016/j.nuclphysb.",
                          "Phys.Lett.": "10.1016/j.physletb.",
                          "Phys.Rept.": "10.1016/j.physrep.",
                          "Phys.Rev.": "10.1103/PhysRevD.",
                          "Phys.Rev.Lett.": "10.1103/PhysRevLett.",
                          "Rev.Mod.Phys.": "10.1103/RevModPhys.",
                          "Science": "10.1126/science"}

CONFERENCE_DICT = {"AIP Conf.Proc.": None,
                   "ASP Conf.Ser.": None,
                   "EPJ Web Conf.": "10.1051/epjconf",
                   "J.Phys.Conf.Ser.": "10.1088/1742-6596",
                   "Int.J.Mod.Phys.Conf.Ser.": None,
                   "Nucl.Phys.Proc.Suppl.": "10.1016/j.nuclphysbps."}

REVIEW_DICT = {"Prog.Part.Nucl.Phys.": "10.1016/j.ppnp.",
               "Phys.Rept.": "10.1016/j.physrep.",
               "Cambridge Monogr.Math.Phys.": None,
               "Ann.Rev.Nucl.Part.Sci.": None,
               "Ann.Rev.Astron.Astrophys.": None,
               "Ann.Rev.Phys.Chem.": None,
               "Ann.Rev.Fluid Mech.": None,
               "Ann.Rev.Earth Planet.Sci.": None,
               "Ann.Rev.Psych.": None,
               "Ann.Rev.Mater.Sci.": None,
               "Ann.Rev.Physiol.": None,
               "Ann.Rev.Biophys.Biomol.Struct.": None,
               "Ann.Rev.Condensed Matter Phys.": None,
               "Ann.Rev.Biophys.": None,
               "Ann.Rev.Biophys.Bioeng.": None,
               "Rept.Prog.Phys.": "10.1088/0034-4885",
               "Rev.Phys.": "10.1016/j.revip.",
               "Living Rev.Sol.Phys.": None,
               "Living Rev.Rel.": None,
               "Space Sci.Rev.": "10.1007/s11214",
               "Rev.Mod.Phys.": "10.1103/RevModPhys.",
               "Astron.Astrophys.Rev.": "10.1007/s00159",
               "Rev.Accel.Sci.Tech.": "10.1142/S17936268"}



type_codes = (('Published', JOURNAL_PUBLISHED_DICT), ('Review', REVIEW_DICT),
              ('ConferencePaper', CONFERENCE_DICT))


def try_dict(mapping, type_code=None, journals=None, dois=None, codes=None):
    """check if information matches the criteria from mapping"""
    if type_code not in codes:
        for key, val in mapping.iteritems():
            if key in journals:
                return True

            if val:
                if any(val in d for d in dois):
                    return True


def check_record(record):
    """check that record has proper type code based on pubnote and doi"""

    journals = []
    dois = []
    codes = []
    for key, val in record.iterfields(['001___', '0247_a', '773__p', '980__a']):
        if key[0] == '001___':
            recid = val
        if key[0] == '0247_a':
            dois.append(val)
        if key[0] == '773__p':
            journals.append(val)
        if key[0] == '980__a':
            codes.append(val)

    for type_code, mapping in type_codes:
        if try_dict(mapping, type_code=type_code, journals=journals, dois=dois, codes=codes):
            record.add_field('980__', '', subfields=[('a', type_code)])
            record.set_amended('adding type code %s to record %s' % (type_code, recid))
