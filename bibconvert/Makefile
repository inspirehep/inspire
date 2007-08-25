# $Id$

include ../config.mk

XSLFILES = SPIRES2MARC.xsl

all:
	@echo "Done."

testfullset: 
	/opt/cds-invenio/bin/bibconvert -c SPIRES2MARC.xsl < inspire_set.xml > inspire_set_converted.xml
	xmllint --format inspire_set_converted.xml

test:
	/opt/cds-invenio/bin/bibconvert -c SPIRES2MARC.xsl < test_record_spires.xml > test_record_spires_converted.xml
	xmllint --format test_record_spires_converted.xml

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

