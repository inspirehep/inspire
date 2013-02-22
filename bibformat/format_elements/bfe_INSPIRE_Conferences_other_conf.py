# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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
"""BibFormat element - Prints BAI link
"""
__revision__ = "$Id$"

def format_element(bfo):
    """
    This is the default format for formatting full-text URLs.
    @param separator: the separator between urls.
    @param style: CSS class of the link
    """
    conferences = bfo.fields('411__')
    out = ""

    for item in conferences:
        if item.has_key('a'):
            link = '<a href ="/search?ln=en&amp;cc=Conferences&amp;p=411__a%3A%22' + item['a'] + '%22">' + item['a'] + '</a>'
            if item.has_key('n'):
                ##anything *11
                if item['n'][-1] == '1':
                    if len(item['n']) > 1 and item['n'][-2] == '1':
                        out += item['n'] + "th conference in the " + \
                        link + " series"
                    else:
                        out += item['n'] + "st conference in the " + \
                        link + " series"
                ##anything *12
                elif item['n'][-1] == '2':
                    if len(item['n']) > 1 and item['n'][-2] == '1':
                        out += item['n'] + "th conference in the " + \
                        link + " series"
                    else:
                        out += item['n'] + "nd conference in the " + \
                        link + " series"
                ##anything *13
                elif item['n'][-1] == '3':
                    if len(item['n']) > 1 and item['n'][-2] == '1':
                        out += item['n'] + "th conference in the " + \
                        link + " series"
                    else:
                        out += item['n'] + "rd conference in the " + \
                        link + " series"
                ##everything else
                else:
                    out += item['n'] + "th conference in the " + \
                    link + " series"
            else:
                out += "Part of the " + link + " series"
            out += "<br />"
    # Removing last line break
    out = out[:-6]

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
