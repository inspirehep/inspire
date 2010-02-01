include ../config.mk

# helper definitions:

SMALL = http://cdsware.cern.ch/download/invenio-demo-site-files/SPIRES_small_sample.xml.gz
LARGE = ftp://ftp.slac.stanford.edu/groups/library/spires/large_test.xml.gz
XSLFILES = SPIRES2MARC.xsl


# main targets:

all:
	@echo "Done."

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

load-small-sample-of-records: get-small convert-small supload-small

load-large-sample-of-records: get-large clean-large split-large convert-large supload-large

load-full-sample-of-records: clean-full split-full convert-full supload-full

# helper targets:

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
	@echo "* rsyncing files from  server, please be patient..."
	rsync --delete -raz ${SPIRESDIR} ${FULLSET_DIR}
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

clean-full:
	@echo "* Removing non-ascii chars in large file, please be patient..."
	perl -i.bk -pe 's/[^[:ascii:]]//g;' $(FULLSET_DIR)*.xml
#	cat large_test.xml | tr -d "\000-\011" | tr -d "\013-\014"| tr -d "\016-\037" > large_test.x
#	mv  large_test.x large_test.xml
	@echo "Please see clean-spires-data.sh if your input contains broken tags"
	@echo "* Done.  Please run 'make split-full' now."

split-large:
	@echo "* Splitting downloaded large file, please be patient..."
	@sleep 3
	python ./split_large_spires_dump_file.py
	@echo "* Done.  Please run 'make convert-large' now."

split-full:
	@echo "* Splitting downloaded large file, please be patient..."
	@sleep 3
	for file in $(FULLSET_DIR)*.xml ; do \
	   python ./split_large_spires_dump_file.py -n10000 -f $${file} ;\
	done
	@echo "* Done.  Please run 'make convert-full' now."

convert-small:
	$(BINDIR)/bibconvert -c `pwd`/SPIRES2MARC.xsl < SPIRES_small_sample.xml > SPIRES_small_sample.marcxml

convert-large:
	@echo "* Converting split files, please be patient..."
	for file in large_test.xml_*[0-9]; do \
	   echo " ... converting file $${file}..." ;\
	   $(BINDIR)/bibconvert -c `pwd`/SPIRES2MARC.xsl < $${file} > $${file}.marcxml ;\
        done
	@echo "* Done.  Please run 'make test-large-with-xmllint' or 'make
	test-large-with-xmlmarclint' now."

convert-full:
	@echo "* Converting split files, please be patient..."
	for file in $(FULLSET_DIR)*.xml_*[0-9]; do \
	   echo " ... converting file $${file}..." ;\
	   $(CONVERT) SPIRES2MARC.xsl  $${file} > $${file}.marcxml ;\
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
	cp SPIRES_small_sample.marcxml /tmp
	chmod a+r /tmp/SPIRES_small_sample.marcxml
	$(BINDIR)/bibupload -ir /tmp/SPIRES_small_sample.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

upload-large:
	@echo "* Uploading converted files..."
	for file in large_test.xml_*[0-9].marcxml; do \
	    $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."

upload-full:
	@echo "* Uploading converted files..."
	for file in $(FULLSET_DIR)*.marcxml* ; do \
	    $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."

supload-small:
	@echo "* Uploading converted files..."
	cp SPIRES_small_sample.marcxml /tmp
	chmod a+r /tmp/SPIRES_small_sample.marcxml
	sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/bibupload -ir /tmp/SPIRES_small_sample.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

supload-large:
	@echo "* Uploading converted files..."
	for file in large_test.xml_*[0-9].marcxml; do \
	    sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."

supload-full:
	@echo "* Uploading converted files..."
	for file in $(FULLSET_DIR)*.marcxml* ; do \
	    sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."


convert-SPIRES:
	@echo "* Converting split files, please be patient..."
	for file in SPIRES_*.xml_*[0-9]; do \
	   echo " ... converting file $${file}..." ;\
	   $(BINDIR)/bibconvert -c `pwd`/SPIRES2MARC.xsl < $${file} > $${file}.marcxml ;\
        done
	@echo "* Done.  Please run 'make test-large-with-xmllint' or 'make test-large-with-xmlmarclint' now."


upload:
	@echo "* Uploading converted files..."
	for file in SPIRES_*.xml_*[0-9].marcxml; do \
	    $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."

supload:
	@echo "* Uploading converted files..."
	for file in SPIRES_*.xml_*[0-9].marcxml; do \
	    sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/bibupload -ir $${file}; \
        done
	@echo "* Done.  Please see via 'bibsched' the task progress."

# end of file
