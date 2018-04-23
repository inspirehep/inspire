# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2017, 2018 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""BibCheck plugin to canonicalize ISBNs"""


def check_record(record):
    """ scan a string and attempt to find an ISBN in it
        strips all forms of dashes or other separators from ISBN
        it also strips all text, so it is essential to verify the ISBN

        examples from test run:
          changed 978-0-8218-1241-9 to 9780821812419
          changed ISBN/0-521-35753-5 to 0521357535
          changed 3-540-56425-X to 354056425X
          changed isbn-9783527407415 to 9783527407415
          changed ISBN 0 - 19 - 852682 - 2 to 0198526822

    """

    for pos, isbnlike in record.iterfields(['020__a', '999C5i']):
        numb = [c for c in isbnlike if c in '0123456789Xx']
        if numb and numb[-1] == 'x':
            numb[-1] = 'X'
        isbn = ''.join(numb)
        verified = isbnchecksum(isbn)
        if not verified:
            record.warn("{0} invalid ISBN: '{1}' '{2}'".format(pos, isbnlike, isbn))
        else:
            record.amend_field(pos, isbn,
                               "changed {0} to {1}".format(isbnlike, isbn))

def isbnchecksum(isbn):
    """ verify checksum of isbnlike string (adapted from isbnlib) """

    try:
        int(isbn[:-1])
    except ValueError:
        return False

    if len(isbn) == 10:
        checkval = sum((i + 2) * int(x)
                       for i, x in enumerate(reversed(isbn[:9])))
        remainder = int(checkval % 11)
        if remainder == 0:
            tenthdigit = 0
        else:
            tenthdigit = 11 - remainder
        if tenthdigit == 10:
            tenthdigit = 'X'
        if isbn[-1] == str(tenthdigit):
            return True

    elif len(isbn) == 13:
        checkval = sum((i % 2 * 2 + 1) * int(x)
                       for i, x in enumerate(isbn[:12]))
        thirteenthdigit = 10 - int(checkval % 10)
        if thirteenthdigit == 10:
            thirteenthdigit = '0'
        if isbn[-1] == str(thirteenthdigit):
            return True

    return False
