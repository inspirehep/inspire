# $Id$

include config.mk

SUBDIRS = bibconvert bibformat

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
	echo "DELETE FROM collection_collection" | $(BINDIR)/dbexec
	echo "DELETE FROM collection WHERE id>1" | $(BINDIR)/dbexec
	echo "UPDATE collection SET dbquery=\"970__a:'SPIRES'\"" | $(BINDIR)/dbexec
	echo "UPDATE collection_rnkMETHOD SET id_collection=1" | $(BINDIR)/dbexec
	$(BINDIR)/webcoll -u admin


load-inspire-test-site-records:
	(cd bibconvert && make)
	$(BINDIR)/bibupload -ir bibconvert/test_record_spires_converted.xml

load-all-inspire-test-site-records:
	(cd bibconvert && make)
	$(BINDIR)/bibupload -ir bibconvert/inspire_set_converted.xml

load-large-inspire-test-site-records:
	(cd bibconvert && make)
	$(BINDIR)/bibupload -ir bibconvert/large_converted.xml


