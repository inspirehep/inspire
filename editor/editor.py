# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.  
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
""" editor  -  CLI interface for editing records, just ecapsulates the
steps of getting the record out of the db, editing it using $EDITOR and
uploading it.

@param recID  the recID of record to edit



"""


#
# Note that this should eventually allow multiple record editing and other
#fancy things and prompt for searching if nothing passed in.
#



import tempfile
import readline
import sys
import getopt
import os
from invenio.bibformat import format_record
from invenio.bibupload import xml_marc_to_records, bibupload


def main(argv):

    recID=0
    opts,pargs=getopt.getopt(argv,'i:')
    for opt, arg in opts:
        if opt == '-i':
            recID=arg

    result=format_record(recID=recID,of='xm')
    tmpfile=tempfile.NamedTemporaryFile()

    print tmpfile.name
    tmpfile.write(result)
    tmpfile.seek(0)
    os.system("pico "+ tmpfile.name)
    tmpfile.seek(0)
    new=[]
    for line in tmpfile:
        new.append(line)  
    if raw_input("Save to DB Y/N:") =='Y':        
         recs=xml_marc_to_records(''.join(new))
         response=bibupload(recs[0],opt_mode='replace')
         if response[0]:print "Error updating record: "+response[0]
    tmpfile.close

if __name__ == "__main__":
    main(sys.argv[1:])

1 	
