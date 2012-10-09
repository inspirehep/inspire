#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ExperimentsCollection_dynamic_KB.py
"""Create a dynamic KB from the experiments collection, and annotate it."""

import sys

from invenio import bibknowledge

kbname = 'ExperimentsCollection'
collection = 'Experiments'
display_field = '119__a'
search_field = '119__a:"*%*" | 119__u:"*%*" | 419__a:"*%*" | 245__a:"*%*"'
kbdesc = "A dynamic KB which searches all 119a fields in the " +\
         "experiments collection, and returns those records' corresponding " + \
         "119a fields."


if __name__ == "__main__":
    bibknowledge.add_dynamic_kb(kbname, display_field, collection, search_field)
    bibknowledge.update_kb_attributes(kbname, kbname, kbdesc)
