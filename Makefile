# $Id$

include config.mk

SUBDIRS = bibconvert bibformat webstyle

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Done.  Please run make install now."

install:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	perl -pi -e 's,CFG_BIBINDEX_FULLTEXT_INDEX_LOCAL_FILES_ONLY = 0,CFG_BIBINDEX_FULLTEXT_INDEX_LOCAL_FILES_ONLY = 1,g' $(LIBDIR)/python/invenio/config.py
	@echo "Done.  You may want to restart Apache now."

reset-inspire-test-site-collection-configuration:
	echo "TRUNCATE collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collectionname" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_portalbox" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_rnkMETHOD" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (1, 'Inspire Test Site', '970__a:\'SPIRES\'', 0, NULL, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (2, 'Institutions', '980__a:"DIRECTORY"', 0, NULL, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 3, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'en', 'ln', 'HEP')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'fr', 'ln', 'HEP')" | $(BINDIR)/dbexec
	$(BINDIR)/webcoll -u admin
	@echo "Please run the webcoll task just submitted, if your bibsched daemon is not in an automatic mode."

load-inspire-test-site-records:
	(cd bibconvert && make)
	$(BINDIR)/bibupload -ir bibconvert/test_record_spires_converted.xml

load-all-inspire-test-site-records:
	(cd bibconvert && make)
	$(BINDIR)/bibupload -ir bibconvert/inspire_set_converted.xml

load-large-inspire-test-site-records:
	(cd bibconvert && make)
	$(BINDIR)/bibupload -ir bibconvert/large_converted.xml


