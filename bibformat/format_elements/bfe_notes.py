# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2012 CERN.
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
"""BibFormat element - Prints notes
"""
__revision__ = "$Id$"

import cgi
from invenio.htmlutils import HTMLWasher


def format_element(bfo, note_suffix, note_prefix='Note: ', separator='; '):
    """
    Displays notes (various note fields)

    @param note_prefix: a prefix before each group of notes
    @param note_suffix: a suffix after each group of notes
    @param separator: a separator between notes of a group
    """
    notes = []
    washer = HTMLWasher()
    wash_and_join = lambda x: separator.join([washer.wash(item, automatic_link_transformation=True) for item in x])

    # Get values from certain fields, wash them (so all links become clickable),
    # join using separator and add to a list
    if bfo.fields('500__a'):
        notes.append(wash_and_join(bfo.fields('500__a')))

    if len(notes) > 0:
        # Split all list elements and add prefixes and suffixes
        notes = [note_prefix + x + note_suffix
                 for x in notes]
        return_notes = "".join(notes)
        return return_notes


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
