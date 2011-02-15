# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
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
"""BibFormat element - Prints texkey with string mods for harvmac
"""
__revision__ = "$Id$"
from invenio.config import CFG_SITE_LANG
def format_element(bfo,harvmac="FALSE"):
    #Print Tex key harvmac variable set to true in harvmac.bfo in format_templates.
    #
    key = ''
    for external_keys in bfo.fields("035"):
        if external_keys['9'] == "SPIRESTeX" and external_keys['z']:
            key = external_keys['z']
    if not key:
        #contruct key in spires like way  need to store an make unique
        ####FIXME
        key = bfo.field("100a").split(' ')[0].lower() + ":" + \
              bfo.field("269c").split('-')[0] + \
              chr((recID % 26) + 97) + chr(((recID / 26) % 26) + 97)
    if harvmac:
        #split the texkey brooks:2010zza to be brooksZZA
        var1 = key.split(':')
        for i in range(0,10):
           var1[1] = var1[1].replace(str(i),'')
        key = var1[0] + var1[1].upper()
    return key
