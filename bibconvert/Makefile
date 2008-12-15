# $Id$

include ../config.mk

SMALL = http://cdsware.cern.ch/download/invenio-demo-site-files/SPIRES_small_sample.xml.gz
LARGE = ftp://ftp.slac.stanford.edu/groups/library/spires/large_test.xml.gz
XSLFILES = SPIRES2MARC.xsl
SPIRESDIR = ftp://ftp.slac.stanford.edu/groups/library/spires
SPIRESFILES = SPIRES_pre_1975.xml.gz SPIRES_1975_1984.xml.gz SPIRES_1985_1994.xml.gz SPIRES_1995_1999.xml.gz SPIRES_2000_2002.xml.gz SPIRES_2003_2005.xml.gz SPIRES_post_2005.xml.gz

all:
	@echo "The sequence is get-large, clean-large, split-large, convert-large or prepare-large or prepare-full"

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

# targets working with big SPIRES dump files follow:

get-small:
	@echo "* Downloading the file please be patient..."
	wget $(SMALL)
	rm -f ./SPIRES_small_sample.xml
	gunzip SPIRES_small_sample.xml.gz

get-large:
	@echo "* Downloading files from SLAC FTP server, please be patient..."
	wget $(LARGE)
	rm -f ./large_test.xml
	gunzip ./large_test.xml.gz        

get-full:
	@echo "* Downloading files from SLAC FTP server, please be patient..."
	rm -rf ${SPIRESFILES} large_test.xml
	for i in ${SPIRESFILES}; do wget -nc ${SPIRESDIR}/$${i}; done
	for i in ${SPIRESFILES}; do gunzip -c $${i} >> large_test.xml; done
	#  Please note, bibconvert and xmllint appear to fail on this large file.  
	#  It may be neccessary to use a different xslt engine or break up the 
	#  file.
	@echo "* Done.  Please run 'make split-large' or 'make clean-large' now."

clean-large:
	@echo "* Removing non-ascii chars in large file, please be patient..."
	perl -i.bk -pe 's/[^[:ascii:]]//g;' large_test.xml
	cat large_test.xml | tr -d "\000-\011" | tr -d "\013-\014"| tr -d "\016-\037" > large_test.x
	mv  large_test.x large_test.xml
	@echo "Please see clean-spires-data.sh if your input contains broken tags"
	@echo "* Done.  Please run 'make split-large' now."

split-large:
	@echo "* Splitting downloaded large file, please be patient..."
	@sleep 3
	python ./split_large_spires_dump_file.py
	@echo "* Done.  Please run 'make convert-large' now."

convert-small:
	$(BINDIR)/bibconvert -c `pwd`/SPIRES2MARC.xsl < SPIRES_small_sample.xml > SPIRES_small_sample.marcxml

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

upload-small:
	@echo "* Uploading converted files..."
	$(BINDIR)/bibupload -ir SPIRES_small_sample.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

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

upload:
	@echo "* Uploading converted files..."
	for file in SPIRES_*.xml_*[0-9].marcxml; do \
	    $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."

prepare-and-upload-large:
	@echo for calling large test from upper level Makefile
	make get-large
	make clean-large
	make split-large
	make convert-large
	make upload

prepare-and-upload-full:
	@echo for calling full sample from upper level Makefile
	make get-full
	make clean-large
	make split-large
	make convert-large
	make upload

# end of file
