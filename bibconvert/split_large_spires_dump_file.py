# $Id$
"""
Input: one big file "large_test.xml" containing dump from SPIRES.
Output: many small "large_test.xml_000234" files.
"""
nb_records = 0
nb_records_in_chunk = 1000
input_filename = "large_test.xml"
record = ""
for line in open(input_filename, "r").readlines():
	record += line
	if line.startswith("</goal_record>"):
		print nb_records
		nb_records += 1
		if nb_records % nb_records_in_chunk == 0:
			open("%s_%09d" % (input_filename, nb_records), "w").write(record + "\n</records>")
			record = "<records>"

open("%s_%09d" % (input_filename, nb_records+1), "w").write(record)
