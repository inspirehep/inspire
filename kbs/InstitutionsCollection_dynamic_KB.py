#!/usr/bin/env python
# -*- coding: utf-8 -*-
# InstitutionsCollection_dynamic_KB.py
"""Create a dynamic KB from the instutions collection, and annotate it."""

import sys

from invenio import bibknowledge

kbname = 'InstitutionsCollection'
collection = 'Institutions'
display_field = '110__u'
search_field = '371__a:*%* | 110__u:*%*'
kbdesc = "A dynamic KB which searches all 371a and 110u fields in the " +\
         "institutions collection, and returns those records' corresponding " + \
         "110u fields."


if __name__ == "__main__":
    bibknowledge.add_dynamic_kb(kbname, display_field, collection, search_field)
    bibknowledge.update_kb_attributes(kbname, kbname, kbdesc)
