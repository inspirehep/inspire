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
		  apsharvest

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
	echo "TRUNCATE idxINDEX_field" | $(BINDIR)/dbexec
	$(BINDIR)/dbexec < bibindex/config/idxINDEX_dump.sql
	@echo ">>> Done reset-inspire-index-configuration."
## Create tables for new indexes 17->22
	$(PYTHON) ./bibindex/create_index_tables.py 17 24

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
		## announce portalbox:
	echo "TRUNCATE portalbox" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_portalbox" | $(BINDIR)/dbexec
	echo "INSERT INTO portalbox VALUES (1, '', 'FIXME')" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'bg', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'ca', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'de', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'el', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'en', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'es', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'fr', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'hr', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'it', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'ja', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'no', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'pl', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'pt', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'ru', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'sk', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'sv', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'zh_CN', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 1, 'zh_TW', 'ne', 100)" | $(BINDIR)/dbexec
		# now update portalbox value from the announce file:
	echo 'from invenio.dbquery import run_sql;body = open("webhelp/inspire_announce.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=1", (body,))' | $(PYTHON)
		## sidebar portalbox:
	echo "INSERT INTO portalbox VALUES (2, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value with placeholder text
	echo "UPDATE portalbox SET body=' ' WHERE id=2"|$(BINDIR)/dbexec
		## and now update portalbox values with RSS feed material
	$(PYTHON) ./feedboxes/inspire_update_feedboxes.py -d

	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'bg', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'ca', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'de', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'el', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'en', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'es', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'fr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'hr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'it', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'ja', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'no', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'pl', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'pt', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'ru', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 2, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
## Now add HEP portalbox to INST collection
	echo "INSERT INTO portalbox VALUES (15, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_inst_right_top.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=15", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'bg', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'ca', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'de', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'el', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'en', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'es', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'fr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'hr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'it', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'ja', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'no', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'pl', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'pt', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'ru', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 15, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
## Now add JOBS collection portalbox
	echo "INSERT INTO portalbox VALUES (3, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the main portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_jobs.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=3", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'bg', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'ca', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'de', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'el', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'en', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'es', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'fr', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'hr', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'it', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'ja', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'no', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'pl', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'pt', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'ru', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'sk', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'sv', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'zh_CN', 'ne', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 3, 'zh_TW', 'ne', 100)" | $(BINDIR)/dbexec

	echo "INSERT INTO portalbox VALUES (4, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_jobs_right_top.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=4", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'bg', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'ca', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'de', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'el', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'en', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'es', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'fr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'hr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'it', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'ja', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'no', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'pl', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'pt', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'ru', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 4, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec

	echo "INSERT INTO portalbox VALUES (5, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_jobs_title.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=5", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'bg', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'ca', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'de', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'el', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'en', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'es', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'fr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'hr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'it', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'ja', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'no', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'pl', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'pt', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'ru', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'sv', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (3, 5, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec

	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'bg', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'ca', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'de', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'el', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'en', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'es', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'fr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'hr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'it', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'ja', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'no', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'pl', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'pt', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'ru', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'sv', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (6, 5, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec
# Add HEP title box
	echo "INSERT INTO portalbox VALUES (6, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_hep_title.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=6", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'bg', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'ca', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'de', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'el', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'en', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'es', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'fr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'hr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'it', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'ja', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'no', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'pl', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'pt', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'ru', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'sv', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -f' to see the new portalboxes."

# Add Inst title box
	echo "INSERT INTO portalbox VALUES (7, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_inst_title.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=7", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'bg', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'ca', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'de', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'el', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'en', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'es', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'fr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'hr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'it', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'ja', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'no', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'pl', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'pt', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'ru', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'sv', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 7, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec

# Add Hepnames title box
	echo "INSERT INTO portalbox VALUES (8, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_hepnames_title.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=8", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'bg', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'ca', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'de', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'el', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'en', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'es', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'fr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'hr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'it', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'ja', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'no', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'pl', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'pt', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'ru', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'sv', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 8, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec

	echo "INSERT INTO portalbox VALUES (9, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_hepnames_right_top.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=9", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'bg', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'ca', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'de', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'el', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'en', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'es', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'fr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'hr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'it', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'ja', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'no', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'pl', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'pt', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'ru', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -f' to see the new portalboxes."

# Add Conf title box
	echo "INSERT INTO portalbox VALUES (13, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_conf_title.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=13", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'bg', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'ca', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'de', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'el', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'en', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'es', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'fr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'hr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'it', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'ja', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'no', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'pl', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'pt', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'ru', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'sv', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 13, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec

	echo "INSERT INTO portalbox VALUES (14, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_conf_right_top.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=14", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'bg', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'ca', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'de', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'el', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'en', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'es', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'fr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'hr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'it', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'ja', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'no', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'pl', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'pt', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'ru', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -f' to see the new portalboxes."

# Add Exp title box
	echo "INSERT INTO portalbox VALUES (16, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_exp_title.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=16", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'bg', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'ca', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'de', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'el', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'en', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'es', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'fr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'hr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'it', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'ja', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'no', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'pl', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'pt', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'ru', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'sv', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 16, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec

	echo "INSERT INTO portalbox VALUES (17, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_exp_right_top.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=17", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'bg', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'ca', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'de', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'el', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'en', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'es', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'fr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'hr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'it', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'ja', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'no', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'pl', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'pt', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'ru', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -f' to see the new portalboxes."

# Add Journal title box
	echo "INSERT INTO portalbox VALUES (18, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_journal_title.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=18", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'bg', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'ca', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'de', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'el', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'en', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'es', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'fr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'hr', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'it', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'ja', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'no', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'pl', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'pt', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'ru', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 18, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec

	echo "INSERT INTO portalbox VALUES (19, '', 'FIXME')" | $(BINDIR)/dbexec
		# now update portalbox value from the right top portalbox file:
	echo 'from invenio.dbquery import run_sql;body = open("feedboxes/portalbox_journal_right_top.html").read();run_sql("UPDATE portalbox SET body=%s WHERE id=19", (body,))' | $(PYTHON)

	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'bg', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'ca', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'de', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'el', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'en', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'es', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'fr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'hr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'it', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'ja', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'no', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'pl', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'pt', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'ru', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (8, 19, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -f' to see the new portalboxes."


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
	echo "INSERT INTO \`format\` (\`id\`, \`name\`, \`code\`, \`description\`, \`content_type\`, \`visibility\`) VALUES \
	(1, 'HTML brief', 'hb', 'HTML brief output format, used for search results pages.', 'text/html', 1),\
	(2, 'HTML detailed', 'hd', 'HTML detailed output format, used for Detailed record pages.', 'text/html', 1),\
	(3, 'MARC', 'hm', 'HTML MARC.', 'text/html', 1),\
	(4, 'Dublin Core', 'xd', 'XML Dublin Core.', 'text/xml', 1),\
	(5, 'MARCXML', 'xm', 'XML MARC.', 'text/xml', 1),\
	(6, 'portfolio', 'hp', 'HTML portfolio-style output format for photos.', 'text/html', 0),\
	(7, 'photo captions only', 'hc', 'HTML caption-only output format for photos.', 'text/html', 0),\
	(8, 'BibTeX', 'hx', 'BibTeX.', 'text/html', 1),\
	(9, 'EndNote', 'xe', 'XML EndNote.', 'text/xml', 1),\
	(10, 'NLM', 'xn', 'XML NLM.', 'text/xml', 1),\
	(11, 'Excel', 'excel', 'Excel csv output', 'application/ms-excel', 0),\
	(12, 'HTML similarity', 'hs', 'Very short HTML output for similarity box (<i>people also viewed..</i>).', 'text/html', 0),\
	(13, 'RSS', 'xr', 'RSS.', 'text/xml', 0),\
	(14, 'OAI DC', 'xoaidc', 'OAI DC.', 'text/xml', 0),\
	(15, 'File mini-panel', 'hdfile', 'Used to show fulltext files in mini-panel of detailed record pages.', 'text/html', 0),\
	(16, 'Actions mini-panel', 'hdact', 'Used to display actions in mini-panel of detailed record pages.', 'text/html', 0),\
	(17, 'References tab', 'hdref', 'Display record references in References tab.', 'text/html', 0),\
	(18, 'HTML citesummary', 'hcs', 'HTML cite summary format, used for search results pages.', 'text/html', 1),\
	(19, 'RefWorks', 'xw', 'RefWorks.', 'text/xml', 1),\
	(20, 'MODS', 'xo', 'Metadata Object Description Schema', 'application/xml', 1),\
	(21, 'LaTeX (EU)', 'hlxe', 'LaTeX formatted reference (EU style)', 'text/html', 1),\
	(22, 'LaTeX (US)', 'hlxu', 'LaTeX formatted reference (US Style)', 'text/html', 1),\
	(23, 'INSPIRE Citation Format', 'hca', 'Very brief cite-as format used by reference submission form.', 'text/html', 1),\
	(24, 'INSPIRE Reference Submission Form', 'hrf', 'Reference submission form, used for user updates to reference lists.', 'text/html', 0),\
	(25, 'LaTeX CV', 'tlcv', 'A LaTeX CV', 'text/plain', 1),\
	(26, 'text CV', 'htcv', 'A plaintext CV', 'text/html', 1),\
	(27, 'HTML CV', 'hcv', 'A CV with hyperlinks', 'text/html', 1);" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_format" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 1, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 2, 120)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 18, 110)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 8, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 21, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 22, 80)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 9, 50)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 19, 10)" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-format-configuration."
	@echo ">>> Adding format configuration for inst:"
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (2, 1, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (2, 2, 120)" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-inst-format-configuration."
	@echo ">>> Done reset-inspire-jobs-format-configuration."
	@echo ">>> Adding format configuration for jobs:"
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (3, 1, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (3, 2, 120)" | $(BINDIR)/dbexec
	@echo ">>> Adding format configuration for conf:"
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (4, 1, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (4, 2, 120)" | $(BINDIR)/dbexec
	@echo ">>> Adding format configuration for Hepnames:"
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (5, 1, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (5, 2, 120)" | $(BINDIR)/dbexec
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
