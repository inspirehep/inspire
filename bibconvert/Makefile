include ../config.mk
-include ../config-local.mk


FTP_LOC = ftp://ftp.slac.stanford.edu/groups/library/spires/inspire/

SMALL_BASE = hep_test_recs
SMALL_URL = ${FTP_LOC}testset/${SMALL_BASE}.xml
MARC_URL = ${FTP_LOC}testset/${SMALL_BASE}.marcxml

INST_BASE = inst_test_recs
INST_URL = ${FTP_LOC}testset/${INST_BASE}.xml
INST_MARC_URL = ${FTP_LOC}testset/${INST_BASE}.marcxml

FULL_INST_BASE = inst_recs
FULL_INST_URL = ${FTP_LOC}inst/${FULL_INST_BASE}.xml
FULL_INST_MARC_URL = ${FTP_LOC}inst/${FULL_INST_BASE}.marcxml


XSLFILES = SPIRES2MARC.xsl oaiarXiv2inspire.xsl oaiarXiv2inspire_categories.xml inst2marc.xsl conf2marc.xsl
TEST_TARGETS = load-small-sample-of-records

# main targets:

all:
	@echo "Done."

test: ${TEST_TARGETS}
	@echo "Done."

clean:
	@rm -f ${SMALL_BASE}.*xml ${INST_BASE}.*xml ${FULL_INST_BASE}.*xml

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

convert-small-sample-of-records: get-small convert-small
load-small-sample-of-records: get-small convert-small upload-small

# helper targets:

get-small:
	@echo "* Downloading the file please be patient..."
	rm -f $(SMALL_BASE).xml
	wget $(SMALL_URL)
	@echo "* Done.  Please run 'make convert-small' now."

get-small-marc:
	@echo "* Downloading the file please be patient..."
	rm -f $(SMALL_BASE).marcxml
	wget $(MARC_URL)
	@echo "* Done.  Please run 'make upload-small' now."

clean-small:
	@echo "* Removing non-ascii chars in large file, please be patient..."
	@for file in `/bin/ls ${SMALL_BASE}.xml`; do \
		perl -i.bk -pe 's/[^[:ascii:]]//g;' $${file} ;\
		cat $${file} | tr -d "\000-\011" | tr -d "\013-\014"| tr -d "\016-\037" > $${file}.x ;\
		mv  $${file}.x $${file} ;\
		done
	@echo "Please see clean-spires-data.sh if your input contains broken tags"
	@echo "* Done.  Please run 'make convert-large' now."

convert-small:
	@echo -n "* Converting small SPIRES record sample..."
	$(BINDIR)/bibconvert -c `pwd`/SPIRES2MARC.xsl < ${SMALL_BASE}.xml > ${SMALL_BASE}.marcxml
	@echo -n " done."
	@echo "Please run 'make upload-small' now."

upload-small:
	@echo "* Uploading converted files..."
	cp ${SMALL_BASE}.marcxml /tmp
	chmod a+r /tmp/${SMALL_BASE}.marcxml
	$(BINDIR)/bibupload -ir /tmp/${SMALL_BASE}.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

### Institutions targets

get-inst:
	@echo "* Downloading the file please be patient..."
	rm -f $(INST_BASE).xml
	wget $(INST_URL)
	@echo "* Done.  Please run 'make convert-inst' now."

get-inst-marc:
	@echo "* Downloading the file please be patient..."
	rm -f $(INST_BASE).marcxml
	wget $(INST_MARC_URL)
	@echo "* Done.  Please run 'make upload-inst' now."

convert-inst:
	@echo -n "* Converting small INST record sample..."
	$(BINDIR)/bibconvert -c `pwd`/inst2marc.xsl < ${SMALL_BASE}.xml > ${SMALL_BASE}.marcxml
	@echo -n " done."
	@echo "Please run 'make upload-small' now."

upload-inst:
	@echo "* Uploading converted files..."
	cp ${INST_BASE}.marcxml /tmp
	chmod a+r /tmp/${INST_BASE}.marcxml
	$(BINDIR)/bibupload -ir /tmp/${INST_BASE}.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

####
## Get the full 9000 record institution set.  Should rarely if ever be used.

get-inst-full:
	@echo "* Downloading the file please be patient..."
	rm -f $(FULL_INST_BASE).xml
	wget $(FULL_INST_URL)
	@echo "* Done.  Please run 'make convert-inst-full' now."

get-inst-marc-full:
	@echo "* Downloading the file please be patient..."
	rm -f $(FULL_INST_BASE).marcxml
	wget $(FULL_INST_MARC_URL)
	@echo "* Done.  Please run 'make upload-inst-full' now."

convert-inst-full:
	@echo -n "* Converting full inst record set..."
	$(BINDIR)/bibconvert -c `pwd`/inst2marc.xsl < ${FULL_INST_BASE}.xml > ${FULL_INST_BASE}.marcxml
	@echo -n " done."
	@echo "Please run 'make upload-inst-full' now."

upload-inst-full:
	@echo "* Uploading converted files..."
	cp ${FULL_INST_BASE}.marcxml /tmp
	chmod a+r /tmp/${FULL_INST_BASE}.marcxml
	$(BINDIR)/bibupload -ir /tmp/${FULL_INST_BASE}.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."



#################
# FIXME: Targets below this point have not been verified as correct

load-full-sample-of-records: get-full clean-large convert-large upload-full
#load-large-sample-of-records: get-large clean-large convert-large supload-large

get-full:
	@echo "* rsyncing files from  server, please be patient..."
	rsync --delete -raz ${SPIRESDIR} ${FULLSET_DIR}
	#  Please note, bibconvert and xmllint appear to fail on this large file.
	#  It may be neccessary to use a different xslt engine or break up the
	#  file.
	@echo "* Done.  Please run 'make split-full' or 'make clean-full' now."

clean-full: get-full
	@echo "* Removing non-ascii chars in large file, please be patient..."
	perl -i.bk -pe 's/[^[:ascii:]]//g;' $(FULLSET_DIR)*.xml
	#  cat large_test.xml | tr -d "\000-\011" | tr -d "\013-\014"| tr -d "\016-\037" > large_test.x
	#  mv  large_test.x large_test.xml
	@echo "Please see clean-spires-data.sh if your input contains broken tags"
	@echo "* Done.  Please run 'make split-full' now."

convert-full:
	@echo "* Converting split files, please be patient..."
	@for file in $(FULLSET_DIR)*.xml_*[0-9]; do \
	   echo " ... converting file $${file}..." ;\
	   $(CONVERT) SPIRES2MARC.xsl  $${file} > $${file}.marcxml ;\
	 done
	@echo "* Done.  Please run 'make test-large-with-xmllint' or 'make test-large-with-xmlmarclint' now."

split-full:
	@echo "* Splitting downloaded large file, please be patient..."
	@sleep 3
	@for file in $(FULLSET_DIR)*.xml ; do \
	   python ./split_large_spires_dump_file.py -n10000 -f $${file} ;\
	 done
	@echo "* Done.  Please run 'make convert-full' now."

upload-full:
	@echo "* Uploading converted files..."
	@for file in $(FULLSET_DIR)*.marcxml* ; do \
		$(BINDIR)/bibupload -ir $${file}; \
	done
	@echo "* Done.  Please see via 'bibsched' the task progress."

supload-full:
	@echo "* Uploading converted files..."
	@for file in $(FULLSET_DIR)*.marcxml* ; do \
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
	@for file in SPIRES_*.xml_*[0-9].marcxml; do \
		$(BINDIR)/bibupload -ir $${file}; \
	 done
	@echo "* Done.  Please see via 'bibsched' the task progress."

supload:
	@echo "* Uploading converted files..."
	@for file in SPIRES_*.xml_*[0-9].marcxml; do \
		sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/bibupload -ir $${file}; \
	 done
	@echo "* Done.  Please see via 'bibsched' the task progress."

# end of file
