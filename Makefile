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
	@echo "Done.  You may want to restart Apache now."

reset-inspire-test-site-collection-configuration:
	echo "DELETE FROM collection_collection" | $(BINDIR)/dbexec
	echo "DELETE FROM collection WHERE id>1" | $(BINDIR)/dbexec
	echo "UPDATE collection SET dbquery=\"970:'SPIRES'\"" | $(BINDIR)/dbexec
	$(BINDIR)/webcoll -u admin

load-inspire-test-site-records:
	(cd bibconvert && make)
	$(BINDIR)/bibupload -ir bibconvert/test_record_spires_converted.xml
