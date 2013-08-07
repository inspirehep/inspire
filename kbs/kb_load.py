# -*- coding: utf-8 -*-
##
## This file is part of Inspire.
## Copyright (C) 2013 CERN.
##
## Inspire is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Inspire is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Inspire; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""INSPIRE KB loader."""

from invenio.bibknowledge_dblayer import add_kb, \
                                         add_kb_mapping, \
                                         kb_exists, \
                                         update_kb
import getopt
import sys
import os


def add_kb_values(kbname, kbfile):
    """
    Given a KB name and path to a tab-delimited KB file, this
    function will insert all entries in the file into to the corresponding
    KB table in the database.
    """
    num_added = 0
    kb_fd = open(kbfile)
    for line in kb_fd:
        splitted_line = line.split('---')
        pair = []
        for part in splitted_line:
            if not part.strip():
                # We can ignore this one
                continue
            pair.append(part.strip())
        if len(pair) != 2:
            print "Error: %s" % (str(pair),)
        add_kb_mapping(kbname, pair[0], pair[1])
        num_added += 1
    kb_fd.close()
    return num_added


def main():
    """
    Main function that executes on launch.
    """
    usage = """Usage: %s KB-FILE KB-NAME [-d DESCRIPTION]""" % (sys.argv[0],)
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hd:", ["help", "description="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        print usage
        sys.exit(2)

    description = ""
    for opt, opt_value in opts:
        if opt in ("-h", "--help"):
            print usage
            sys.exit()
        if opt in ("-d", "--description"):
            description = opt_value

    if len(args) < 2:
        sys.stderr.write("Missing kb-file or kb-name\n")
        print usage
        sys.exit(1)

    kbfile = args[0].strip()
    if not os.path.exists(kbfile):
        sys.stderr.write("Path to non-existing file\n")
        print usage
        sys.exit(1)

    kbname = args[1].strip()
    if kb_exists(kbname):
        update_kb(kbname, kbname, description)
    else:
        add_kb(kbname, description)
    num_added = add_kb_values(kbname, kbfile)
    print "Added %i entries to %s" % (num_added, kbname)

if __name__ == "__main__":
    main()
