# $Id$
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
	erase=0
	input_filename = "large_test.xml"
	nb_records_in_chunk = 1000
	try:
		opts, args = getopt.getopt(argv, "f:n:Xc")
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)
	opts.sort()
	clean=0
       	for opt, val in opts:
		if opt =='-f':
			input_filename = val
		if opt =='-c':
			clean =1
	       	if opt =='-X':
			erase = 1
		if opt == '-n':
			nb_records_in_chunk = int(val)
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


	record = ""
	f = open(input_filename, "r")
	out=open("%s_%09d" % (input_filename, nb_records+nb_records_in_chunk), "w")
	out
	for line in f:
		out.write(line)
		if line.startswith(" </goal_record>"):
			nb_records += 1
			if nb_records % nb_records_in_chunk == 0:
				out.write("\n</records>")
				out.close()
				if clean:
					os.system("sh clean-spires-data.sh<"+out.name+">"+out.name+".clean")
				out=open("%s_%09d" % (input_filename, nb_records+nb_records_in_chunk), "w")
				out.write( "<records>")
				print nb_records
			

	f.close()
	out.close()


def usage():
	print __doc__


if __name__ == "__main__":
	main(sys.argv[1:])
