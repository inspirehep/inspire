# $Id$

include ../config.mk

XSLFILES = SPIRES2MARC.xsl
SPIRESXML = ftp://ftp.slac.stanford.edu/groups/library/spires/large_test.xml.gz

all:
	@echo "Done."

convert-test:
test:
	$(BINDIR)/bibconvert -c SPIRES2MARC.xsl < test_record_spires.xml > test_record_spires_converted.xml
	xmllint --format test_record_spires_converted.xml

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

upload-test:
	@echo "* Uploading converted files..."
	$(BINDIR)/bibupload -ir test_record_spires_converted.xml
	@echo "* Done.  Please see via 'bibsched' the task progress."


# targets working with big SPIRES dump files follow:

get-large:
	@echo "* Downloading large file from SLAC FTP server, please be patient..."
	wget $(SPIRESXML)
	rm -f ./large_test.xml
	gunzip ./large_test.xml.gz
	#  Please note, bibconvert and xmllint appear to fail on this large file.  
	#  It may be neccessary to use a different xslt engine or break up the 
	#  file.
	@echo "* Done.  Please run 'make split-large' or 'make clean-large' now."

clean-large:
	@echo "* Removing non-ascii chars in large file, please be patient..."
	perl -i.bk -pe 's/[^[:ascii:]]//g;' large_test.xml
	@echo "Please see clean-spires-data.sh if your input contains broken tags"
	@echo "* Done.  Please run 'make split-large' now."

split-large:
	@echo "* Splitting downloaded large file, please be patient..."
	@sleep 3
	python ./split_large_spires_dump_file.py
	@echo "* Done.  Please run 'make convert-large' now."

convert-large:
	@echo "* Converting split files, please be patient..."
	for file in large_test.xml_*[0-9]; do \
	   echo " ... converting file $${file}..." ;\
	   $(BINDIR)/bibconvert -c `pwd`/SPIRES2MARC.xsl < $${file} > $${file}.marcxml ;\
        done
	@echo "* Done.  Please run 'make test-large-with-xmllint' or 'make test-large-with-xmlmarclint' now."


test-large-with-xmllint:
	@echo "* Testing XML correctness of converted files, please be patient..."
	for file in large_test.xml_*[0-9].marcxml; do \
	    xmllint --noout $${file}; \
        done
	@echo "* Done.  Please run 'make upload-large' now."

test-large-with-xmlmarclint:
	@echo "* Testing MARCXML correctness of converted files, please be patient..."
	for file in large_test.xml_*[0-9].marcxml; do \
	    echo $(BINDIR)/xmlmarclint  $${file}; \
	    $(BINDIR)/xmlmarclint  $${file}; \
        done
	@echo "* Done.  Please run 'make upload-large' now."

upload-large:
	@echo "* Uploading converted files..."
	for file in large_test.xml_*[0-9].marcxml; do \
	    $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."




convert-SPIRES:
	@echo "* Converting split files, please be patient..."
	for file in SPIRES_*.xml_*[0-9]; do \
	   echo " ... converting file $${file}..." ;\
	   $(BINDIR)/bibconvert -c `pwd`/SPIRES2MARC.xsl < $${file} > $${file}.marcxml ;\
        done
	@echo "* Done.  Please run 'make test-large-with-xmllint' or 'make test-large-with-xmlmarclint' now."


test-SPIRES-with-xmllint:
	@echo "* Testing XML correctness of converted files, please be patient..."
	for file in SPIRES_*.xml_*[0-9].marcxml; do \
	    xmllint --noout $${file}; \
        done
	@echo "* Done.  Please run 'make upload-large' now."

test-SPIRES-with-xmlmarclint:
	@echo "* Testing MARCXML correctness of converted files, please be patient..."
	for file in SPIRES_*.xml_*[0-9].marcxml; do \
	    $(BINDIR)/xmlmarclint --noout $${file}; \
        done
	@echo "* Done.  Please run 'make upload-large' now."

upload-SPIRES:
	@echo "* Uploading converted files..."
	for file in SPIRES_*.xml_*[0-9].clean.marcxml; do \
	    $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."

# end of file
