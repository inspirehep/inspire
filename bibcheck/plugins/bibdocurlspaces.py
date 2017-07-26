#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2017 CERN.
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

""" Bibcheck plugin to correctly escape URLs
"""

from urllib import quote
from urllib2 import URLError, urlopen
from urlparse import urlsplit, urlunsplit


def check_record(record):
    """
    replace URL in 8564_u containing literal space with an escaped version
    since in general this requires different quoting in different URL parts,
    only apply to local (https?://inspirehep.net/) PDF URLs
    """
    for pos, val in record.iterfield('8564_u'):
        if not (' ' in val and 'inspirehep.net/' in val and val.endswith('pdf')):
            continue

        (scheme, netloc, path, query, fragment) = urlsplit(val)
        newval = urlunsplit((scheme, netloc, quote(path), query, fragment))

        if newval == val:
            record.warn("URL with space not in path part: {0}".format(val))
            continue

        try:
            goodurl = urlopen(newval, timeout=10)
        except URLError:
            goodurl = False

        if goodurl:
            record.amend_field(pos, newval, 'changed\n\t{0}\nto\n\t{1}'.format(val, newval))
        else:
            record.warn("URL does not appear to be correct: {0}".format(newval))

