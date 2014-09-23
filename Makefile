include config.mk
-include config-local.mk
#
# Note that local makefile configurations can be defined in config-local.mk to override config.mk

SUBDIRS = bibconvert \
		  bibformat \
		  webstyle \
		  bibrank \
		  conf \
		  bibedit \
		  webhelp \
		  feedboxes \
		  bibharvest \
		  kbs \
		  bibcatalog \
		  websubmit \
		  bibtasklets \
		  apsharvest \
		  miscutil \
		  bibsort \
		  bibexport \
		  webaccess \
		  tests \
		  www

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Done.  Please run make install now."

install:
	@echo "Installing new code and support files..."
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to copy $(ETCDIR)/invenio-local.conf-example to $(ETCDIR)/invenio-local.conf, edit commented parts, run inveniocfg --update-all --reset-all and restart Apache now."
	@echo "To install database changes, run 'make install-dbchanges'."

install-dbchanges: reset-inspire-field-configuration \
                 reset-inspire-index-configuration \
                 reset-inspire-collection-configuration \
                 reset-inspire-search-sort-field-configuration \
                 reset-inspire-useraccess-configuration \
                 reset-inspire-submission-configuration \
                 reset-inspire-portalbox-configuration \
                 reset-inspire-examples-searches \
                 reset-inspire-rank-configuration \
                 reset-inspire-format-configuration \
                 reset-inspire-examples-searches

	@echo "Installing database changes..."
	@cd kbs && make install-dbchanges && cd ..
	@echo "Done."

reset-ugly-ui:
	@cd webstyle && make install-ugly && cd ..

reset-test-ui:
	@cd webstyle && make install-test && cd ..

reset-normal-ui:
	@cd webstyle && make install && cd ..

load-demo-records:
	@cd bibconvert && make load-records && cd ..

load-legacy-records:
	@cd bibconvert && make load-test-sample-of-records && cd ..

clean:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make clean && cd .. ;)
	@rm -f *.orig *~
	@echo "Done."

reset-inspire-field-configuration:
	@echo ">>> Resetting table tag:"
	echo "TRUNCATE tag" | $(BINDIR)/dbexec
	echo "TRUNCATE field" | $(BINDIR)/dbexec
	echo "TRUNCATE field_tag" | $(BINDIR)/dbexec
	@echo ">>> Add tag-field config."
	$(BINDIR)/dbexec < bibindex/config/tag_field_dump.sql
	echo "TRUNCATE fieldname" | $(BINDIR)/dbexec
	@echo ">>> Add fieldname config."
	$(BINDIR)/dbexec < bibindex/config/fieldnames.sql
	@echo ">>> Done reset-inspire-field-configuration."

reset-inspire-index-configuration:
	@echo ">>> Resetting table idxINDEX:"
	echo "TRUNCATE idxINDEX" | $(BINDIR)/dbexec
	-echo "TRUNCATE idxINDEX_idxINDEX" | $(BINDIR)/dbexec
	echo "TRUNCATE idxINDEX_field" | $(BINDIR)/dbexec
	$(BINDIR)/dbexec < bibindex/config/idxINDEX_dump.sql
	@echo ">>> Done reset-inspire-index-configuration."
## Create tables for new indexes 17->22
	$(PYTHON) ./bibindex/create_index_tables.py 17 27

reset-inspire-collection-configuration:
	echo "TRUNCATE collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collectionname" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_portalbox" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_rnkMETHOD" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (1, 'HEP', '970__a:\'SPIRES\' or 980__a:\"HEP\"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (2, 'Institutions', '980__a:\"INSTITUTION\"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (3, 'Jobs', '980__a:\"JOB\"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (4, 'Conferences', '980__a:\"CONFERENCES\"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (5, 'HepNames', '980__a:\"HEPNAMES\"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (6, 'Jobs Hidden', '980__a:\"JOBHIDDEN\"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (7, 'Experiments', '980__a:\"EXPERIMENT\"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (8, 'Journals', '980__a:\"JOURNALS\"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 1, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 2, 110)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (2, 3, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'en', 'ln', 'HEP')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'fr', 'ln', 'HEP')" |$(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (2, 'en', 'ln', 'Institutions')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (3, 'en', 'ln', 'Jobs')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (4, 'en', 'ln', 'Conferences')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (5, 'en', 'ln', 'HepNames')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (6, 'en', 'ln', 'Jobs Hidden')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (7, 'en', 'ln', 'Experiments')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (8, 'en', 'ln', 'Journals')" | $(BINDIR)/dbexec
	echo "DELETE FROM collection_externalcollection WHERE id_collection >= 2" | $(BINDIR)/dbexec
	echo "UPDATE collection_externalcollection SET type=1 WHERE type=2" | $(BINDIR)/dbexec
	echo "TRUNCATE collectiondetailedrecordpagetabs" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (1, 'metadata;references;citations;files;plots')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (2, 'metadata')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (3, 'metadata')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (4, 'metadata')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (5, 'metadata')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (6, 'metadata')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (7, 'metadata')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (8, 'metadata')" | $(BINDIR)/dbexec
	if [ x"$(CFG_INSPIRE_BIBTASK_USER)" != x"" ]; then \
	    $(BINDIR)/webcoll -u $(CFG_INSPIRE_BIBTASK_USER) -f; \
	else \
	    $(BINDIR)/webcoll -f; \
	fi
	@echo "Please run the webcoll task just submitted, if your bibsched daemon is not in an automatic mode."

reset-inspire-rank-configuration:
	@echo ">>> Resetting ranking configuration:"
	echo "TRUNCATE rnkMETHOD" | $(BINDIR)/dbexec
	echo "TRUNCATE rnkMETHODNAME" | $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHOD VALUES (1,'wrd','0000-00-00 00:00:00')"  | $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHOD VALUES (2,'citation','0000-00-00 00:00:00')"  | $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHOD VALUES (3,'inst_papers','0000-00-00 00:00:00')"  | $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHOD VALUES (4,'selfcites','0000-00-00 00:00:00')"  | $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHODNAME VALUES (1, 'en', 'ln', 'word similarity')" |  $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHODNAME VALUES (2, 'en', 'ln', 'times cited')" |  $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHODNAME VALUES (3, 'en', 'ln', 'papers in HEP')" |  $(BINDIR)/dbexec

reset-inspire-portalbox-configuration:
	@echo ">>> Resetting collection portalboxes:"
	cd feedboxes; make reset-inspire-portalbox-configuration

reset-inspire-search-sort-field-configuration:
	@echo ">>> Resetting search/sort field configuration:"
	@echo ">>> Adding hep search/sort field configuration:"
	echo "TRUNCATE collection_field_fieldvalue" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 15, NULL, 'sew', 14, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 3, NULL, 'sew', 13, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 23, NULL, 'sew', 12, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 16, NULL, 'sew', 11, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 11, NULL, 'sew', 10, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 17, NULL, 'sew', 9, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 22, NULL, 'sew', 8, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 13, NULL, 'sew', 7, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 5, NULL, 'sew', 6, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 8, NULL, 'sew', 5, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 6, NULL, 'sew', 4, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 14, NULL, 'sew', 3, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 2, NULL, 'sew', 2, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 10, NULL, 'sew', 1, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 3, NULL, 'soo', 4, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 6, NULL, 'soo', 3, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 2, NULL, 'soo', 2, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (1, 10, NULL, 'soo', 1, 0)" | $(BINDIR)/dbexec
	@echo ">>> Adding inst search/sort field configuration:"
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (2, 25, NULL, 'sew', 50, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (2, 26, NULL, 'sew', 10, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (2, 27, NULL, 'sew', 25, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (2, 30, NULL, 'sew', 100, 0)" | $(BINDIR)/dbexec
	@echo ">>> Adding jobs search/sort field configuration:"
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (3, 18, NULL, 'soo', 1, 0)" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-inst-search-sort-field-configuration."


reset-inspire-useraccess-configuration:
	@echo ">>> Resetting user access configuration:"
#FIXME - truncating accARGUMENT is necc. if building on top of Atlantis -
#should probably build from scratch instead...
	echo "TRUNCATE accARGUMENT;" | $(BINDIR)/dbexec
	echo "UPDATE accROLE SET firerole_def_src='deny all' WHERE name='basketusers'" | $(BINDIR)/dbexec
	echo "UPDATE accROLE SET firerole_def_src='deny all' WHERE name='loanusers'" | $(BINDIR)/dbexec
	echo "UPDATE accROLE SET firerole_def_src='deny all' WHERE name='groupusers'" | $(BINDIR)/dbexec
	echo "UPDATE accROLE SET firerole_def_src='deny all' WHERE name='messageusers'" | $(BINDIR)/dbexec
	echo "UPDATE accROLE SET firerole_def_src='deny all' WHERE name='holdingsusers'" | $(BINDIR)/dbexec
	echo "UPDATE accROLE SET firerole_def_src='deny all' WHERE name='statisticsusers'" | $(BINDIR)/dbexec
	echo "UPDATE accROLE SET firerole_def_src='deny all' WHERE name='basketusers'" | $(BINDIR)/dbexec
	echo "UPDATE accROLE SET firerole_def_src='deny all' WHERE name='alertusers'" | $(BINDIR)/dbexec
	# Activate guest submission for all submissions
	echo "INSERT INTO accROLE_accACTION_accARGUMENT (id_accROLE, id_accACTION, id_accARGUMENT, argumentlistid) VALUES (3, 33, -1, -1)" | $(BINDIR)/dbexec
	if [ x"$(CFG_INSPIRE_BIBTASK_USER)" != x"" ]; then \
	    $(BINDIR)/webaccessadmin -u $(CFG_INSPIRE_BIBTASK_USER) -c; \
	else \
	    $(BINDIR)/webaccessadmin -c; \
	fi
	@echo ">>> Done reset-inspire-useraccess-configuration."

reset-inspire-submission-configuration:
	@echo ">>> Resetting submission configuration:"
	echo "TRUNCATE sbmCOLLECTION" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmCOLLECTION_sbmCOLLECTION" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmCOLLECTION_sbmDOCTYPE" | $(BINDIR)/dbexec
	@echo ">>> Add Job submission."
	echo "INSERT INTO sbmCOLLECTION VALUES (1,'Submit a Job')" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION_sbmCOLLECTION VALUES (0,1,1)" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION_sbmDOCTYPE VALUES (1,'JOBSUBMIT',1)" | $(BINDIR)/dbexec
	$(BINDIR)/dbexec < websubmit/config/JOBSUBMIT_db_dump.sql
	@echo ">>> Add Conf submission."
	echo "INSERT INTO sbmCOLLECTION VALUES (2,'Submit a Conference')" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION_sbmCOLLECTION VALUES (0,2,2)" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION_sbmDOCTYPE VALUES (2,'CONFSUBMIT',2)" | $(BINDIR)/dbexec
	$(BINDIR)/dbexec < websubmit/config/CONFSUBMIT_db_dump.sql
	@echo ">>> Add BibTeX form."
	echo "INSERT INTO sbmCOLLECTION VALUES (3,'Submit BibTeX')" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION_sbmCOLLECTION VALUES (0,3,3)" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION_sbmDOCTYPE VALUES (3,'bibtex',3)" | $(BINDIR)/dbexec
	$(BINDIR)/dbexec < websubmit/config/bibtex_db_dump.sql
	@echo ">>> Done reset-inspire-submission-configuration."

reset-inspire-format-configuration:
	@echo ">>> Resetting format configuration:"
	echo "TRUNCATE format" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_format" | $(BINDIR)/dbexec
	$(BINDIR)/dbexec < bibformat/config/format_collection_dump.sql
	@echo ">>> Done reset-inspire-jobs-format-configuration."

reset-inspire-examples-searches:
	@echo ">>> Resetting example searches:"
	echo "TRUNCATE collection_example" | $(BINDIR)/dbexec
	echo "TRUNCATE example" | $(BINDIR)/dbexec
	cat webhelp/search_examples.dat |  $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example)	select 1, example.id from example where example.type='HEP';" | $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example)	select 2, example.id from example where example.type='Institutions';" | $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example) select 3, example.id from example where example.type='Jobs';" | $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example) select 4, example.id from example where example.type='Conferences';" | $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example) select 5, example.id from example where example.type='HepNames';" | $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example) select 7, example.id from example where example.type='Experiments';" | $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example) select 8, example.id from example where example.type='Journals';" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-example-searches."
