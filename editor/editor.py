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
import re
from string import upper
from invenio.bibformat import format_record
from invenio.bibupload import xml_marc_to_records, bibupload
from invenio import bibconvert
from invenio import bibconvert_xslt_engine
from invenio.dbquery import run_sql

def main(argv):

    recID=0
    opts,pargs=getopt.getopt(argv,'di:')
    verbose = False
    for opt, arg in opts:

        if opt == '-i':
            recID=arg
        if opt == '-d':
            verbose = True

    result=format_record(recID=recID,of='xm')

    if result:
	    #change the result to MARC by applying a template
            if verbose:
                print result
                raw_input("go on?")
	    result = bibconvert_xslt_engine.convert(result, "marcxmltoplain.xsl")
            #call a sub that changes the stuff to editable form, calls editor,
	    #returns a string
	    new = convert_edit(result)
	    newr = to_marc(new)
            if verbose:
                #debug
                f=open('/tmp/debug', 'w')
                f.write(new)
                f.write(newr)
                f.close()
                print newr
	    if upper(raw_input("Save to DB Y/N:")) =='Y':
        	 recs=xml_marc_to_records(''.join(newr))
	         response=bibupload(recs[0],opt_mode='replace')
	         if response[0]:print "Error updating record: "+response[0]

def convert_edit(result):
	    #get tag names from DB
	    tags = run_sql("select name, value from tag");
	    #print result
	    #print str(tags)
	    for t in tags:
		(human, tag) = t
		#remove % in tag if needed
		tag = tag.replace("%",'')
		#check the converted result, replace matching tags w values
		result = result.replace("\n"+tag,"\n"+human)

	    print result
	    tmpfile=tempfile.NamedTemporaryFile()
	    print tmpfile.name

	    tmpfile.write(result)
	    tmpfile.seek(0)
            if len(os.environ['EDITOR']) > 0:
                editor= os.environ['EDITOR']
            else:
                editor="pico"
            try:
                os.system(editor+' '+tmpfile.name)
            except OSError, e:
                print "Editor Failed", e
                sys.exit



	    tmpfile.seek(0)

	    new = tmpfile.read()

	    #reverse the tag replacement
	    for t in tags:
		(human, tag) = t
		#remove % in tag if needed
		tag = tag.replace("%",'')
		#check the converted result, replace matching tags w values
		new = new.replace("\n"+human,"\n"+tag)

	    tmpfile.close
	    return new

def to_marc(new):
	    #create a MARCXML hash using 'new' as source
	    lines = new.split("\n")
	    cf = {} #controlfields
	    dfsf = {} #datafield-subfield -dict
	    rn = '' #record number in case new record needed
	    for l in lines:
		#get the controlfield
		if l.startswith("controlfield"):
			cff = str(l[12:15])
			cfv = l[16:]
			cf[cff]=cfv

		sf={}
		dbrec = ''
        	#if the line starts with 555xxx: it's a tag
	        p = re.compile('^\d\d\d...:')
		if p.match(l):
			#take the junk
			dfieldtag = l[0:3]
			dfieldind1 = l[3]
			dfieldind2 = l[4]
			main = dfieldtag+dfieldind1+dfieldind2
			subfieldc = l[5]
			rest = l[7:]
			#put in hash
			if dfsf.has_key(main):
				sf = dfsf[main]
				if sf.has_key(subfieldc):
					#print "warning! "+main+" "+subfieldc+" IS "+sf[subfieldc]
					#create a new record
					rn = main
					tmp = 0
					if dfsf.has_key(rn):
						while dfsf.has_key(rn):
							sft = dfsf[rn]
							if sft.has_key(subfieldc):
								#increase tmp to check next
								rn = rn+str(tmp)
								tmp = tmp+1
							else:
								main = rn
								#print "adding to existing record "+str(rn)
								sft[subfieldc] = rest
								sf = sft
						#after while loop: now we are
						#sure a new record can be created
						main = rn
						#print "new record "+str(rn)
						sft = {}
						sft[subfieldc] = rest
						sf = sft
			sf[subfieldc] = rest
			dfsf[main] = sf

 	    #go through the hash -- put stuff in newrecord
	    newr = '<collection>\n<record>\n'
	    for i in cf.keys():
                newr =newr+'<controlfield tag="'+i+'">'+cf[i]+'</controlfield>\n'
	    for i in dfsf.keys():
		#split again
		dfieldtag = i[0:3]
	        dfieldind1 = i[3]
                dfieldind2 = i[4]
		newr = newr+'<datafield tag="'+dfieldtag+'" ind1="'+dfieldind1+'" ind2="'+dfieldind2+'">'
		sf = dfsf[i]
		for j in sf.keys():
			newr=newr+'<subfield code="'+j+'">'+sf[j]+'</subfield>'
		newr=newr+'</datafield>\n'

            #close
	    newr=newr+"</record></collection>"
	    return newr

if __name__ == "__main__":
    main(sys.argv[1:])

1
