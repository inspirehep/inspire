# $Id$

all:
	@echo "Nothing to be made.  Now type 'make test'."

test:
	/opt/cds-invenio/bin/bibconvert -c SPIRES2MARC.xsl < test_record_spires.xml > test_record_spires_converted.xml
	xmllint --format test_record_spires_converted.xml
