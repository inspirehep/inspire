# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
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
"""BibFormat element - Prints HTML link to talk
"""
__revision__ = "$Id$"


def format_element(bfo, separator=', ', link="yes"):
    """
    Prints Conference info as best is possible.

    @param link if yes (default) prints link to SPIRES conference info
    @param separator  separates multiple conferences

    """

    from invenio.bibformat_config_inspire import CFG_BIBFORMAT_INSPIRE_CONF_LINK

    confs = []
    confs = bfo.fields('773')
    output = []
    for conf in confs:
        note = ''
        if conf.has_key('w'):
            cnum = conf['w'].replace("/", "-")
            if cnum.count('-') == 0:
                # This is probably an ECONF pub note, which are all messed
                # up  likely that there is another, better note on the record
                string = cnum[:3] + '-' + cnum[3:5] + '-'
                if len(cnum) == 8:
                    day = cnum[5:7]
                    nr = cnum[7]
                    cnum = string + day + '.' + nr
                else:
                    day = cnum[5:]
                    cnum = string + day
            if link.lower() == 'yes' :
                conf_name = '<a class="conflink" href = "' + \
                            CFG_BIBFORMAT_INSPIRE_CONF_LINK + \
                            cnum + '&of=hd">' + \
                            cnum + '</a>'
            else:
                conf_name = cnum
            if conf.has_key('t'):
                note += conf['t'] + ' Conference: ' + conf_name
            else:
                note += 'Conference: ' + conf_name
            if conf.has_key('x'):
                note += ' (' + conf['x'] +')'
            if conf.has_key('c'):
                note += ', p.' + conf['c']

        if len(note)>0:
            output.append(note)

    return separator.join(output)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
