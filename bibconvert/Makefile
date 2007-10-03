# $Id$

include ../config.mk

XSLFILES = SPIRES2MARC.xsl
SPIRESXML = ftp://ftp.slac.stanford.edu/groups/library/spires/large_test.xml

all:
	@echo "Done."

getlarge:
	wget $(SPIRESXML)

convertlarge:  
	/opt/cds-invenio/bin/bibconvert -c SPIRES2MARC.xsl < large_test.xml > large_converted.xml
	xmllint --noout large_converted.xml
#
#  PLease note, bibconvert and xmllint appear to fail on this large file.  
#  It may be neccessary to use a different xslt engine or break up the 
#  file.
#


testfullset: 
	/opt/cds-invenio/bin/bibconvert -c SPIRES2MARC.xsl < inspire_set.xml > inspire_set_converted.xml
	xmllint --format inspire_set_converted.xml

test:
	/opt/cds-invenio/bin/bibconvert -c SPIRES2MARC.xsl < test_record_spires.xml > test_record_spires_converted.xml
	xmllint --format test_record_spires_converted.xml

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

