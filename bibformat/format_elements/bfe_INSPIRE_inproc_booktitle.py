# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015 CERN.
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
"""
 BibFormat element - Prints bibliographic info for bibtex booktitle associated
 with a conference record

"""

from invenio.search_engine import get_fieldvalues, search_pattern


def format_element(bfo):
    """
    Attempt to find a citable conference proceedings "booktitle"
    for a member record specified by bfo
    """
    booktitle = ''
    # 1) recid:[773__0]  (245 $$a: $$b)
    recid = bfo.field('773__0')
    if recid:
        titles = get_fieldvalues(recid, '245__a')
        if titles:
            booktitle = titles[0]
            subtitles = get_fieldvalues(recid, '245__b')
            if subtitles:
                booktitle += ': ' + subtitles[0]
    # 2) reportnumber of parent record and conference acronym
    if not booktitle:
        rn = bfo.field('773__r')
        if rn:
            acronym = bfo.field('773__q')
            if acronym:
                booktitle = "%s: %s" % (rn, acronym,)
            # 2.b) reportnumber:[773__r] (245 $$a: $$b)
            else:
                recids = search_pattern(p="reportnumber:%s" % (rn,))
                if recids:
                    titles = get_fieldvalues(recids[0], '245__a')
                    if titles:
                        booktitle = titles[0]
                        subtitles = get_fieldvalues(recids[0], '245__b')
                        if subtitles:
                            booktitle += ': ' + subtitles[0]
    # 3) 773__w:[773__w] 980:PROCEEDINGS  (245 $$a: $$b)
    if not booktitle:
        cnum = bfo.field("773__w")
        if cnum:
            cnum = cnum.replace("/", "-")
            recids = search_pattern(
                p='773__w:%s 980__a:PROCEEDINGS' % (cnum,))
            if recids:
                titles = get_fieldvalues(recids[0], '245__a')
                if titles:
                    booktitle = titles[0]
                    subtitles = get_fieldvalues(recid, '245__b')
                    if subtitles:
                        booktitle += ': ' + subtitles[0]
            # 3.b) 111__g:[773__w] 980:CONFERENCES 111 fields
            if not booktitle:
                confrecids = search_pattern(
                    p="111__g:%s 980__a:CONFERENCES" % (cnum,))
                if confrecids:
                    # take first match here
                    cr = confrecids[0]
                    titles = get_fieldvalues(cr, '111__a')
                    subtitles = get_fieldvalues(cr, '111__b')
                    acronyms = get_fieldvalues(cr, '111__e')
                    places = get_fieldvalues(cr, '111__c')
                    if titles:
                        booktitle = titles[0]
                        if subtitles:
                            booktitle += ": " + subtitles[0]
                    if acronyms:
                        booktitle += ' %s' % ' '.join(
                            ('(%s)' % x for x in acronyms))
                    if places:
                        booktitle += ' %s' % ', '.join(
                            (str(x) for x in places))
                    # 3.c) no 111? -> 773__x in the conf record
                    if not booktitle:
                        titles = get_fieldvalues(cr, '773__x')
                        if titles:
                            booktitle = ', '.join(titles)
                    # 3.d) cr -> append date
                    if booktitle:
                        from invenio.bibformat_elements import \
                            bfe_INSPIRE_Conference_cite_date as ccdate
                        from invenio.bibformat_engine import BibFormatObject
                        confdate = ccdate.format_element(BibFormatObject(cr))
                        if confdate:
                            booktitle += ', ' + confdate
    # 4) [773__x]
    if not booktitle:
        xtitles = bfo.fields('773__x', repeatable_subfields_p=True)
        if xtitles:
            booktitle = ', '.join(xtitles)

    return booktitle


# we know the argument is unused, thanks
# pylint: disable=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable=W0613
