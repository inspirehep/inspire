# $Id$
"""
Input: one big file specified by -f (default: "large_test.xml") containing
dump from SPIRES.

-f:  filename (default: large-test.xml)
-X:  erase all previously created split files (otherwise pick up
-numbering where you left off)

Output: many small "<input_filename>_000234" files 
"""

import getopt
import sys
import re
import os
def main(argv):
	erase=0
	input_filename = "large_test.xml"
	try:                                
		opts, args = getopt.getopt(argv, "f:X")
	except getopt.GetoptError, err:
		print str(err)
		usage()                         
		sys.exit(2)
	opts.sort()
       	for opt, val in opts:
		if opt =='-f':
			input_filename = val
	       	if opt =='-X':
			erase = 1
				#sys.exit()


	lastnum=0
	dir=os.path.dirname(input_filename)
	file=os.path.basename(input_filename)
	print dir+"  "+file
	if dir=='':
		dir='.'
	for file in os.listdir(dir):
		match = re.search(input_filename+'_(\d+)$', file)
		if match:
			if erase:
				os.unlink(file)
			else:
				lastnum=int(match.group(1))
				
	
       	nb_records = lastnum
	nb_records_in_chunk = 1000

	record = ""
	f = open(input_filename, "r")
	out=open("%s_%09d" % (input_filename, nb_records+nb_records_in_chunk), "w")
	out
	for line in f:
		out.write(line)
		if line.startswith("</goal_record>"):
			print nb_records
			nb_records += 1
			if nb_records % nb_records_in_chunk == 0:
				out.write("\n</records>")
				out.close()
				out=open("%s_%09d" % (input_filename, nb_records+nb_records_in_chunk), "w")
				out.write( "<records>")
	f.close()
	out.write("\n</records>")
	out.close()


def usage():
	print __doc__


if __name__ == "__main__":
	main(sys.argv[1:])
