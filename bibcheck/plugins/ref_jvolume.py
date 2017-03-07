# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""
For journal reference field 999C5s
move letter in front of volume if volume > vol_min or volume < vol_max
"""
def check_record(record, journal, letter, vol_min=0, vol_max=999999):
    """
    Move volume letter in front of volume
    """
    import re
    jvol = re.compile("^(?P<journal>%s,)(?P<volume>\d+) *%s(?P<pages>,.*)$" %
        (re.escape(journal), re.escape(letter)))

    for position, jref in record.iterfield("999C5s"):
        result = jvol.search(jref)
        if result:
            volume = result.group('volume')
            if vol_min < int(volume) and int(volume) < vol_max:
                new_jref = result.group('journal') + letter + volume + result.group('pages')
                record.amend_field(position, new_jref)

