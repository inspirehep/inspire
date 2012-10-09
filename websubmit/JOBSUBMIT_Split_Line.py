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
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Split one line into multiple lines on "; " separator
"""
import os


def JOBSUBMIT_Split_Line(parameters, curdir, form, user_info=None):
    """
    Changes some files in which multiple values are separated with '; '
    by removing that separator and puting every value in a new line
    """

    def replace_separator(name):
        element = os.path.join(curdir, name)
        if os.path.exists(element):
            content = open(element, "r").read()
            new_content = '\n'.join([el.strip() for el in content.split(';')])
            open(element, "w").write(new_content)

    replace_separator('JOBSUBMIT_AFFIL')
    replace_separator('JOBSUBMIT_EXP')

    ## Return an empty string:
    return ""
