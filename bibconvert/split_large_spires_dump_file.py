# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2007, 2008, 2010, 2013 CERN.
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

"""
Input: one big file specified by -f (default: "large_test.xml") containing
dump from SPIRES.

-f:  filename (default: large-test.xml)
-X:  erase all previously created split files (otherwise pick up
-numbering where you left off)
-n:  number of records in a chunk (default 1000)
-c:  (deprecated) run clean-spires-data.sh

Output: many small "<input_filename>_000234" files
"""

import getopt
import sys
import re
import os


def main(argv):
    """Split large SPIRES dump file."""
    erase = 0
    input_filename = "large_test.xml"
    nb_records_in_chunk = 1000
    try:
        opts, args = getopt.getopt(argv, "f:n:Xc")
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    opts.sort()
    clean = 0
    for opt, val in opts:
        if opt == '-f':
            input_filename = val
        if opt == '-c':
            clean = 1
        if opt == '-X':
            erase = 1
        if opt == '-n':
            nb_records_in_chunk = int(val)

    lastnum = 0
    directory = os.path.dirname(input_filename)
    file_name = os.path.basename(input_filename)
    print directory + "  " + file_name
    if directory == '':
        directory = '.'
    for file_name in os.listdir(directory):
        match = re.search(input_filename + '_(\d+)$', file_name)
        if match:
            if erase:
                os.unlink(file_name)
            else:
                lastnum = int(match.group(1))

        nb_records = lastnum

    f = open(input_filename, "r")
    out = open("%s_%09d" %
               (input_filename, nb_records + nb_records_in_chunk), "w")
    for line in f:
        out.write(line)
        if line.startswith(" </goal_record>"):
            nb_records += 1
            if nb_records % nb_records_in_chunk == 0:
                out.write("\n</records>")
                out.close()
                if clean:
                    os.system(
                        "sh clean-spires-data.sh<" + out.name + ">" + out.name + ".clean")
                out = open(
                    "%s_%09d" % (input_filename, nb_records + nb_records_in_chunk), "w")
                out.write("<records>")
                print nb_records

    f.close()
    out.close()


def usage():
    print __doc__


if __name__ == "__main__":
    main(sys.argv[1:])
