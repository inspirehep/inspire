# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
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
"""BibFormat element - Prints references
"""
__revision__ = "$Id$"

def format(bfo, reference_prefix, reference_suffix):
    """
    Prints the references of this record

    @param reference_prefix a prefix displayed before each reference
    @param reference_suffix a suffix displayed after each reference
    """

    from invenio.search_engine import search_unit
    from invenio.bibformat import format_record
    references = bfo.fields("999C5", escape=1)
    out = ""

    for reference in references:
        ref_out = ''

        if reference.has_key('o'):
            if out != "":
                ref_out = '</li>'
            ref_out += '<li><small>'+\
                       reference['o']+ "</small> "
#  LEAVE out full ref while we have spires import which does not store
#  useful things here
#        if reference.has_key('m'):
#            ref_out += "<small>"+ reference['m']+ "</small> "



        display_journal = ''
        display_report = ''
        clean_report = ''
        clean_journal = ''
        hits = []
        if reference.has_key('s'):
            display_journal = reference['s']
            clean_journal = reference['s']
        if reference.has_key('r'):
            display_report = reference['r']
            clean_report = reference['r']
        if clean_report:
            hits = search_unit(f='reportnumber', p=clean_report)
        if clean_journal and len(hits)!=1:
            hits = search_unit(f='journal', p=clean_journal)
        if len(hits) == 1:
            ref_out += '<small>' +\
                       format_record(list(hits)[0],'hs') + '</small>'

#  Silly stuff that can be used if there are a lot of multiple hits
#
#        elif len(hits)>1:
#            if display_journal:
#                ref_out += '<small><a href="'+CFG_SITE_URL+\
#                           '/search?f=journal&amp;p='+ \
#                           reference['s']+ \
#                           '&amp;ln=' + bfo.lang + \
#                           '">'+display_journal+"</a></small>"
#            if display_report:
#                ref_out += ' <small><a href="'+CFG_SITE_URL+\
#                           '/search?f=reportnumber&amp;p='+ \
#                           reference['r']+ \
#                           '&amp;ln=' + bfo.lang + \
#                           '">'+display_report+"</a></small>"

        else:
            ref_out = '<small>'
            if display_journal:
                ref_out += display_journal
            if display_report:
                ref_out += ' '+display_report
            ref_out += ' (not in Inspire)</small>'



        ref_out += "<br />"



        if reference_prefix is not None and ref_out != '':
            ref_out = reference_prefix + ref_out
        if reference_suffix is not None and ref_out != '':
            ref_out += reference_suffix

        out += ref_out

    if out != '':
        out += '</li>'

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
