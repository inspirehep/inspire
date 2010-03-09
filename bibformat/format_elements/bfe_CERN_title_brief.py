# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints short title
"""
__revision__ = "$Id$"



import re

def format(bfo, highlight="no", force_title_case="no"):
    """
    Prints a short title, suitable for brief format.

    @param highlight highlights the words corresponding to search query if set to 'yes'
    """

    main_corporate_authors = bfo.fields('931__a', 1)
    titles = bfo.fields('245__', 1)
    sections =  bfo.fields('246__', 1)
    field_245_0 = bfo.fields('245_0', 1)
    field_245_1 = bfo.fields('245_1', 1)
    field_245_2 = bfo.fields('245_2', 1)
    field_245_3 = bfo.fields('245_3', 1)
    field_245_4 = bfo.fields('245_4', 1)
    field_245_5 = bfo.fields('245_5', 1)
    field_245_X = []
    field_245_X.extend(field_245_0)
    field_245_X.extend(field_245_1)
    field_245_X.extend(field_245_2)
    field_245_X.extend(field_245_3)
    field_245_X.extend(field_245_4)
    field_245_X.extend(field_245_5)



    alt_titles = bfo.fields('246_1', 1)
    edition_statement = bfo.field('250__a', 1)

    out = ""


    if len(main_corporate_authors) > 0: # Why is this here?
        out += " : ".join(main_corporate_authors) + " : "

    for title in titles:
        out += title.get('a')
        if title.has_key('b'):
            out += ' : ' + title['b']
        if title.has_key('s'):
            out += ' : ' + title['s']

    for section in sections:
        if section.has_key('n'):
            out += " " + section['n']
            if section.has_key('p'):
                out += " : " + section['p']

    for inst in field_245_X:
        out += inst.get('a')
        if inst.has_key('b'):
            out += ' : ' + inst['b']
        if inst.has_key('s'):
            out += ' : ' + inst['s']

    for alt_title in alt_titles:
        out += "<br /><b><i>" + alt_title.get('a') + '</i></b>'
        if alt_title.has_key('b'):
            out += ' : ' + alt_title['b']
        if alt_title.has_key('s'):
            out += ' : ' + alt_title['s']

    #Try to display edition statement if other titles were not found
    if out == '' and edition_statement != '':
        out += " ; " + edition_statement


    if highlight == 'yes':
        from invenio import bibformat_utils
        out = bibformat_utils.highlight(out, bfo.search_pattern,
                                        prefix_tag="<span style='font-weight: bolder'>",
                                        suffix_tag='</style>')


    if force_title_case.lower()=="yes" and (out.upper()==out or re.search('THE ',out)):   #title is allcaps
        out=' '.join([word.capitalize() for word in out.split(' ')])   # should not cap 1 letter words...

    if bfo.field('960__a') == '40':
        out += "<br />"
    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
