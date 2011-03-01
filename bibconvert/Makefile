include ../config.mk
-include ../config-local.mk

SMALL_BASE = hep_test_recs
INST_BASE = inst_test_recs
SMALL_LOC = http://www.slac.stanford.edu/spires/inspire_test/testset/
SMALL_URL = ${SMALL_LOC}/${SMALL_BASE}.xml
INST_URL = ${SMALL_LOC}/${INST_BASE}.xml
MARC_URL = ${SMALL_LOC}/${SMALL_BASE}.marcxml
INST_MARC_URL = ${SMALL_LOC}/${INST_BASE}.marcxml


LARGE_PATH = /afs/slac.stanford.edu/public/groups/library/spires/inspire/test
LARGE_PATTERN = ????_test_set.xml
XSLFILES = SPIRES2MARC.xsl oaiarXiv2inspire.xsl oaiarXiv2inspire_categories.xml
TEST_TARGETS = test-large-with-xmllint test-large-with-xmlmarclint

# main targets:

all:
	@echo "Done."

test: ${TEST_TARGETS}
	@echo "Done."

clean:
	@rm -f ${LARGE_PATTERN} ${LARGE_PATTERN}.x ${LARGE_PATTERN}.bk \
		   ${LARGE_PATTERN}.marcxml SPIRES_small_sample.xml.gz \
		   SPIRES_small_sample.xml SPIRES_small_sample.marcxml

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

convert-small-sample-of-records: get-small convert-small
convert-large-sample-of-records: get-large clean-large convert-large
load-small-sample-of-records: get-small convert-small upload-small
load-large-sample-of-records: get-large clean-large convert-large upload-large
#load-small-sample-of-records: get-small convert-small supload-small

# helper targets:

get-small:
	@echo "* Downloading the file please be patient..."
	wget $(SMALL_URL)
	@echo "* Done.  Please run 'make convert-small' now."

get-small-marc:
	@echo "* Downloading the file please be patient..."
	wget $(MARC_URL)
	@echo "* Done.  Please run 'make upload-small' now."

get-inst:
	@echo "* Downloading the file please be patient..."
	wget $(INST_URL)
	@echo "* Done.  Please run 'make convert-inst' now."

get-inst-marc:
	@echo "* Downloading the file please be patient..."
	wget $(INST_MARC_URL)
	@echo "* Done.  Please run 'make upload-inst' now."

get-large:
	@echo -n "* Copying XML files from AFS space, please be patient..."
	@cp ${LARGE_PATH}/${LARGE_PATTERN} .
	@echo " done."

clean-large:
	@echo "* Removing non-ascii chars in large file, please be patient..."
	@for file in `/bin/ls ${LARGE_PATTERN}`; do \
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

convert-inst:
	@echo -n "* Institution conversion currently broken.  Use 'make get-inst-marc' instead."
#	@echo -n "* Converting small SPIRES record sample..."
#	$(BINDIR)/bibconvert -c `pwd`/INST2MARC.xsl < ${SMALL_BASE}.xml > ${SMALL_BASE}.marcxml
#	@echo -n " done."
#	@echo "Please run 'make upload-small' now."



convert-large:
	@echo "* Converting split files, please be patient..."
	@for file in `/bin/ls ${LARGE_PATTERN}`; do \
	   echo " ... converting file $${file}..." ;\
	   $(BINDIR)/bibconvert -c `pwd`/SPIRES2MARC.xsl < $${file} > $${file}.marcxml ;\
	   if [ `md5sum $${file} | cut -f1 -d' '` = `md5sum $${file}.bk | cut -f1 -d' '` ]; \
	     then rm -f $${file}.bk ;\
		 else echo "WARNING: Input and backup files differ; something strange is going on." ;\
	   fi ;\
     done
	@echo "* Done.  Please run 'make test-large-with-xmllint' or 'make test-large-with-xmlmarclint' now."

test-large-with-xmllint: convert-large
	@echo "* Testing XML correctness of converted files, please be patient..."
	@for file in `/bin/ls ${LARGE_PATTERN}`; do \
	    xmllint --noout $${file}; \
     done
	@echo "* Done.  Please run 'make upload-large' now."

############# XXX: HACK: The following output parsing (if clause) would be unnecessary
#############            if xmlmarclint used shell return codes correctly.
############# was: $(BINDIR)/xmlmarclint $${file}; \

test-large-with-xmlmarclint: convert-large
	@echo "* Testing MARCXML correctness of converted files, please be patient..."
	@for file in `/bin/ls ${LARGE_PATTERN}.marcxml`; do \
	    echo -n $(BINDIR)/xmlmarclint $${file}; \
		if [ -n "`$(BINDIR)/xmlmarclint $${file}`" ] ;\
		  then echo "Removing $${file} because of bad/missing records..."; rm -f $${file} ;\
		  else echo " ...ok." ;\
		fi ;\
     done
	@echo "* Done.  Please run 'make upload-large' now."

upload-small:
	@echo "* Uploading converted files..."
	cp ${SMALL_BASE}.marcxml /tmp
	chmod a+r /tmp/${SMALL_BASE}.marcxml
	$(BINDIR)/bibupload -ir /tmp/${SMALL_BASE}.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

upload-inst:
	@echo "* Uploading converted files..."
	cp ${INST_BASE}.marcxml /tmp
	chmod a+r /tmp/${INST_BASE}.marcxml
	$(BINDIR)/bibupload -ir /tmp/${INST_BASE}.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

# upload-small that uses sudo internally
supload-small:
	@echo "* Uploading converted files..."
	cp ${SMALL_BASE}.marcxml /tmp
	chmod a+r /tmp/${SMALL_BASE}.marcxml
	sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/bibupload -ir /tmp/${SMALL_BASE}.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

upload-large:
	@echo "* Uploading converted files..."
	@for file in `/bin/ls ${LARGE_PATTERN}.marcxml`; do \
		echo "Uploading from " $${file} "..." ;\
	    $(BINDIR)/bibupload -ir $${file}; \
     done
	@echo "* Done.  Please see via 'bibsched' the task progress."

# upload-large that uses sudo internally
supload-large:
	@echo "* Uploading converted files..."
	@for file in `/bin/ls ${LARGE_PATTERN}.marcxml`; do \
		echo "Uploading from " $${file} "..." ;\
	    sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/bibupload -ir $${file}; \
     done
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
