# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""
 If 710__g contains 'for the' or 'on behalf of'
 check whether there is an author name.
 Split and clean collaboration.
"""


def cleancoll(coll):
    """ Cleanup collaboration, try to find author """
    import re
    author = None
    on_behalf_of = re.compile('ON BEHALF OF', re.IGNORECASE)
    for_the = re.compile('FOR THE ', re.IGNORECASE)
    coll = on_behalf_of.sub('FOR THE', coll)
    coll = for_the.sub('FOR THE ', coll)
    if re.search('FOR THE ', coll) or re.search('FOR THE$', coll):
        if re.search('ASSOCIATION FOR THE', coll, flags=re.IGNORECASE) or \
            re.search('CENTER FOR THE', coll, flags=re.IGNORECASE) or \
            re.search('INSTITUTE FOR THE', coll, flags=re.IGNORECASE):
            return None, None
        else:
            (l, t) = re.split(' *FOR THE *', coll, maxsplit=1)
            if re.search(r'\w', l):
                lead = re.split(' ', l)
            else:
                lead = []
            if re.search(r'\w', t):
                tail = re.split(' ', t)
            else:
                tail = []
            if len(tail) == 0:
                if len(lead) == 0:
                    coll = ''
                else:
                    coll = lead[0]
                    if len(lead) > 1:
                        author = ' '.join(lead[1:])
            else:
                coll = ' '.join(tail)
                if re.search(r'collaboration$', coll, flags=re.IGNORECASE) or \
                    re.search(r' team$', coll, flags=re.IGNORECASE):
                    if len(lead) > 0:
                        author = ' '.join(lead)
                else:
                    if len(lead) > 0:
                        coll = coll + ' ' + lead[0]
                        if len(lead) > 1:
                            author = ' '.join(lead[1:])
            if author:
                author = re.sub(r'^ *([\w.-]+) (.+)$', r'\2, \1', author)
            return coll, author
    else:
        return None, None


def check_record(record):
    """
    If 710__g contains 'for the' or 'on behalf of'
    check whether there is an author name.
    Split and clean collaboration.
    """
    from invenio.bibrecord import record_modify_subfield
    from invenio.bibrecord import record_add_field
    message = ""
    rec_modified = False
    rec_holdingpen = False
    for position, coll in record.iterfield("710__g"):
        new, author = cleancoll(coll)
        if new:
            message = "%s changed %s -> %s\n" % (message, coll, new)
            record_modify_subfield(record, "710", "g", new,
                position[2], field_position_local=position[1])
            rec_modified = True
            if author:
                message = "%s found author: %s in %s\n" % (message, author, coll)
                if record.has_key("100"):
                    akey = "700"
                else:
                    akey = "100"
                record_add_field(record, akey, ' ', ' ', '', [('a', author)])
                rec_holdingpen = True
    if rec_modified:
        record.set_amended(message)
        if rec_holdingpen:
            record.holdingpen = True
