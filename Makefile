# $Id$

include config.mk

SUBDIRS = bibconvert bibformat webstyle kbs bibrank conf

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Done.  Please run make install now."

reset-inspire-test-site-field-configuration:
	echo "UPDATE tag SET value='773__%' WHERE name='journal'" | $(BINDIR)/dbexec
	echo "UPDATE tag SET value='260__c' WHERE name='year'" | $(BINDIR)/dbexec
	echo "UPDATE tag SET value='693__e' WHERE name='experiment'" | $(BINDIR)/dbexec
	echo "REPLACE INTO field VALUES (50, 'collaboration', 'collaboration')" | $(BINDIR)/dbexec
	echo "REPLACE INTO tag VALUES (200, 'collaboration', '710__g')" | $(BINDIR)/dbexec
	echo "REPLACE INTO field_tag VALUES (50, 200, 100)" | $(BINDIR)/dbexec

install: reset-inspire-test-site-field-configuration reset-inspire-test-site-collection-configuration
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to copy invenio-local.conf.inspire on invenio-local.conf, run inveniocfg  --update-all and restart Apache now."

reset-inspire-test-site-collection-configuration:
	echo "TRUNCATE collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collectionname" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_portalbox" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_rnkMETHOD" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (1, 'HEP', '970__a:\'SPIRES\'', 0, NULL, NULL)" | $(BINDIR)/dbexec
	#echo "INSERT INTO collection VALUES (2, 'Institutions', '980__a:"DIRECTORY"', 0, NULL, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 1, 200)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 3, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'en', 'ln', 'HEP')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'fr', 'ln', 'HEP')" | $(BINDIR)/dbexec
	#echo "DELETE FROM collection_externalcollection WHERE id_collection > 2" | $(BINDIR)/dbexec
	echo "DELETE FROM collection_externalcollection WHERE id_collection >= 2" | $(BINDIR)/dbexec
	#echo "UPDATE collection_externalcollection SET type=1 WHERE type=2" | $(BINDIR)/dbexec
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

load-knowledge-base:
	cd kbs && make && cd ..
