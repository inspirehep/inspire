# $Id$

include ../config.mk

XSLFILES = SPIRES2MARC.xsl
SPIRESXML = ftp://ftp.slac.stanford.edu/groups/library/spires/large_test.xml

all:
	@echo "Done."

test:
	$(BINDIR)/bibconvert -c SPIRES2MARC.xsl < test_record_spires.xml > test_record_spires_converted.xml
	xmllint --format test_record_spires_converted.xml

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

# targets working with big SPIRES dump files follow:

get-large:
	@echo "* Downloading large file from SLAC FTP server, please be patient..."
	wget $(SPIRESXML)
	#  Please note, bibconvert and xmllint appear to fail on this large file.  
	#  It may be neccessary to use a different xslt engine or break up the 
	#  file.
	@echo "* Done.  Please run 'make split-large' now."

split-large:
	@echo "* Splitting downloaded large file, please be patient..."
	@sleep 3
	python ./split_large_spires_dump_file.py
	@echo "* Done.  Please run 'make convert-large' now."

convert-large:
	@echo "* Converting split files, please be patient..."
	for file in large_test.xml_*; do \
	   $(BINDIR)/bibconvert -c SPIRES2MARC.xsl < $${file} > $${file}.marcxml ;\
        done
	@echo "* Done.  Please run 'make test-large-with-xmllint' or 'make test-large-with-xmlmarclint' now."

test-large-with-xmllint:
	@echo "* Testing XML correctness of converted files, please be patient..."
	for file in large_test.xml_*marcxml; do \
	    xmllint --noout $${file}; \
        done
	@echo "* Done.  Please run 'make upload-large' now."

test-large-with-xmlmarclint:
	@echo "* Testing MARCXML correctness of converted files, please be patient..."
	for file in large_test.xml_*marcxml; do \
	    $(BINDIR)/xmlmarclint --noout $${file}; \
        done
	@echo "* Done.  Please run 'make upload-large' now."

upload-large:
	@echo "* Uploading converted files..."
	for file in large_test.xml_*marcxml; do \
	    $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."

# end of file
