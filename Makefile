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
	$(PYTHON) ./bibindex/create_index_tables.py 17 22

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
	$(BINDIR)/webcoll -u admin
	@echo "Please run the webcoll task just submitted, if your bibsched daemon is not in an automatic mode."

reset-inspire-rank-configuration:
	@echo ">>> Resetting ranking configuration:"
	echo "TRUNCATE rnkMETHOD" | $(BINDIR)/dbexec
	echo "TRUNCATE rnkMETHODNAME" | $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHOD VALUES (1,'wrd','0000-00-00 00:00:00')"  | $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHOD VALUES (2,'citation','0000-00-00 00:00:00')"  | $(BINDIR)/dbexec
	echo "INSERT INTO rnkMETHOD VALUES (3,'inst_papers','0000-00-00 00:00:00')"  | $(BINDIR)/dbexec
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
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'sk', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'sv', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'zh_CN', 'tp', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (1, 6, 'zh_TW', 'tp', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -u admin -f' to see the new portalboxes."

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
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (5, 9, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -u admin -f' to see the new portalboxes."

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
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (4, 14, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -u admin -f' to see the new portalboxes."

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
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (7, 17, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
	@echo ">>> Done. You may want to run 'webcoll -u admin -f' to see the new portalboxes."


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
	$(BINDIR)/webaccessadmin -u admin -c
	@echo ">>> Done reset-inspire-useraccess-configuration."

reset-inspire-submission-configuration:
	@echo ">>> Resetting submission configuration:"
	echo "TRUNCATE sbmCOLLECTION" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmCOLLECTION_sbmCOLLECTION" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmCOLLECTION_sbmDOCTYPE" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmDOCTYPE" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmFUNDESC" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmFIELD" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmFIELDDESC" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmALLFUNCDESCR" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmCATEGORIES" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmFUNCTIONS" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmIMPLEMENT" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmPARAMETERS" | $(BINDIR)/dbexec
	echo "TRUNCATE sbmCHECKS" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION VALUES (1,'Submit a Job');" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION_sbmCOLLECTION VALUES (0,1,1);" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCOLLECTION_sbmDOCTYPE VALUES (1,'JOBSUBMIT',1);" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCATEGORIES VALUES ('JOBSUBMIT','JOB','Job Vacancy',1);" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmDOCTYPE VALUES ('Job Submission form','JOBSUBMIT','2011-09-05','2011-09-05','Job submission form');" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmPARAMETERS VALUES ('JOBSUBMIT','authorfile','JOBSUBMIT_CONTA'),('JOBSUBMIT','autorngen','Y'),('JOBSUBMIT','counterpath','lastid_JOBSUBMIT_JOB_<PA>yy</PA>   '),('JOBSUBMIT','createTemplate','JOBSUBMITcreate.tpl'),('JOBSUBMIT','edsrn','JOBSUBMIT_IRN'),('JOBSUBMIT','emailFile','JOBSUBMIT_EMAIL'),('JOBSUBMIT','fieldnameMBI','JOBSUBMIT_CHANG'),('JOBSUBMIT','modifyTemplate','JOBSUBMITmodify.tpl'),('JOBSUBMIT','rnformat','JOBSUBMIT-JOB-<PA>yy</PA>'),('JOBSUBMIT','rnin','comboJOBSUBMIT'),('JOBSUBMIT','sourceDoc','Textual Document'),('JOBSUBMIT','sourceTemplate','JOBSUBMIT.tpl'),('JOBSUBMIT','status','ADDED'),('JOBSUBMIT','titleFile','JOBSUBMIT_TITLE'),('JOBSUBMIT','yeargen','AUTO'),('JOBSUBMIT','casesteps','2,3'),('JOBSUBMIT','casevalues','approve,reject'),('JOBSUBMIT','casevariable','JOBSUBMIT_DECSN'),('JOBSUBMIT','decision_file','JOBSUBMIT_DECSN'),('JOBSUBMIT','newrnin','NEWRN'),('JOBSUBMIT','comments_file','JOBSUBMIT_COMNT'),('JOBSUBMIT','addressesAPP',''),('JOBSUBMIT','affiliationfile','JOBSUBMIT_AFFIL'),('JOBSUBMIT','abstractfile','JOBSUBMIT_ABSTR'),('JOBSUBMIT','contactemailfile','JOBSUBMIT_EMAIL'),('JOBSUBMIT','contactnamefile','JOBSUBMIT_CONTA'),('JOBSUBMIT','datefile','JOBSUBMIT_DATE'),('JOBSUBMIT','experimentsfile','JOBSUBMIT_EXP'),('JOBSUBMIT','fieldfile','JOBSUBMIT_FIELD'),('JOBSUBMIT','rankfile','JOBSUBMIT_RANK'),('JOBSUBMIT','referencefile','JOBSUBMIT_REFEM'),('JOBSUBMIT','regionfile','JOBSUBMIT_REG'),('JOBSUBMIT','urlfile','JOBSUBMIT_URL'),('JOBSUBMIT','casedefault','approve'),('JOBSUBMIT','categformatDAM','JOBSUBMIT-<CATEG>-.*'),('JOBSUBMIT','addressesDAM','jobs@inspirehep.net');" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmFUNDESC VALUES ('JOBSUBMIT_Mail_Submitter','authorfile'),('JOBSUBMIT_Mail_Submitter','edsrn'),('JOBSUBMIT_Mail_Submitter','emailFile'),('JOBSUBMIT_Mail_Submitter','newrnin'),('JOBSUBMIT_Mail_Submitter','status'),('JOBSUBMIT_Mail_Submitter','titleFile'),('JOBSUBMIT_Print_Success','edsrn'),('JOBSUBMIT_Print_Success','newrnin'),('JOBSUBMIT_Print_Success','status'),('Get_Recid','record_search_pattern'),('Get_Report_Number','edsrn'),('Send_Modify_Mail','addressesMBI'),('Send_Modify_Mail','sourceDoc'),('Register_Approval_Request','categ_file_appreq'),('Register_Approval_Request','categ_rnseek_appreq'),('Register_Approval_Request','note_file_appreq'),('Register_Referee_Decision','decision_file'),('Withdraw_Approval_Request','categ_file_withd'),('Withdraw_Approval_Request','categ_rnseek_withd'),('Report_Number_Generation','edsrn'),('Report_Number_Generation','autorngen'),('Report_Number_Generation','rnin'),('Report_Number_Generation','counterpath'),('Report_Number_Generation','rnformat'),('Report_Number_Generation','yeargen'),('Report_Number_Generation','nblength'),('Mail_Approval_Request_to_Referee','categ_file_appreq'),('Mail_Approval_Request_to_Referee','categ_rnseek_appreq'),('Mail_Approval_Request_to_Referee','edsrn'),('Mail_Approval_Withdrawn_to_Referee','categ_file_withd'),('Mail_Approval_Withdrawn_to_Referee','categ_rnseek_withd'),('Mail_Submitter','authorfile'),('Mail_Submitter','status'),('Create_Modify_Interface','fieldnameMBI'),('Send_Modify_Mail','fieldnameMBI'),('Update_Approval_DB','categformatDAM'),('Update_Approval_DB','decision_file'),('Send_SRV_Mail','categformatDAM'),('Send_SRV_Mail','addressesSRV'),('JOBSUBMIT_Send_Approval_Request','directory'),('JOBSUBMIT_Send_Approval_Request','categformatDAM'),('JOBSUBMIT_Send_Approval_Request','addressesDAM'),('JOBSUBMIT_Send_Approval_Request','titleFile'),('Send_APP_Mail','edsrn'),('Mail_Submitter','titleFile'),('Send_Modify_Mail','emailFile'),('Get_Info','authorFile'),('Get_Info','emailFile'),('Get_Info','titleFile'),('Make_Modify_Record','modifyTemplate'),('Send_APP_Mail','addressesAPP'),('Send_APP_Mail','categformatAPP'),('Send_APP_Mail','newrnin'),('Send_APP_Mail','decision_file'),('Send_APP_Mail','comments_file'),('CaseEDS','casevariable'),('CaseEDS','casevalues'),('CaseEDS','casesteps'),('CaseEDS','casedefault'),('Send_SRV_Mail','noteFile'),('Send_SRV_Mail','emailFile'),('Mail_Submitter','emailFile'),('Mail_Submitter','edsrn'),('Mail_Submitter','newrnin'),('Make_Record','sourceTemplate'),('Make_Record','createTemplate'),('Print_Success','edsrn'),('Print_Success','newrnin'),('Print_Success','status'),('Make_Modify_Record','sourceTemplate'),('Move_Files_to_Storage','documenttype'),('Move_Files_to_Storage','iconsize'),('Move_Files_to_Storage','paths_and_suffixes'),('Move_Files_to_Storage','rename'),('Move_Files_to_Storage','paths_and_restrictions'),('Move_Files_to_Storage','paths_and_doctypes'),('Move_Revised_Files_to_Storage','elementNameToDoctype'),('Move_Revised_Files_to_Storage','createIconDoctypes'),('Move_Revised_Files_to_Storage','createRelatedFormats'),('Move_Revised_Files_to_Storage','iconsize'),('Move_Revised_Files_to_Storage','keepPreviousVersionDoctypes'),('Set_Embargo','date_file'),('Set_Embargo','date_format'),('Stamp_Uploaded_Files','files_to_be_stamped'),('Stamp_Uploaded_Files','latex_template'),('Stamp_Uploaded_Files','latex_template_vars'),('Stamp_Uploaded_Files','stamp'),('Stamp_Uploaded_Files','layer'),('Stamp_Uploaded_Files','switch_file'),('Make_Dummy_MARC_XML_Record','dummyrec_source_tpl'),('Make_Dummy_MARC_XML_Record','dummyrec_create_tpl'),('Print_Success_APP','decision_file'),('Print_Success_APP','newrnin'),('Send_Delete_Mail','edsrn'),('Send_Delete_Mail','record_managers'),('Second_Report_Number_Generation','2nd_rn_file'),('Second_Report_Number_Generation','2nd_rn_format'),('Second_Report_Number_Generation','2nd_rn_yeargen'),('Second_Report_Number_Generation','2nd_rncateg_file'),('Second_Report_Number_Generation','2nd_counterpath'),('Second_Report_Number_Generation','2nd_nb_length'),('Stamp_Replace_Single_File_Approval','file_to_be_stamped'),('Stamp_Replace_Single_File_Approval','latex_template'),('Stamp_Replace_Single_File_Approval','latex_template_vars'),('Stamp_Replace_Single_File_Approval','new_file_name'),('Stamp_Replace_Single_File_Approval','stamp'),('Stamp_Replace_Single_File_Approval','layer'),('Stamp_Replace_Single_File_Approval','switch_file'),('Move_CKEditor_Files_to_Storage','input_fields'),('Create_Upload_Files_Interface','maxsize'),('Create_Upload_Files_Interface','minsize'),('Create_Upload_Files_Interface','doctypes'),('Create_Upload_Files_Interface','restrictions'),('Create_Upload_Files_Interface','canDeleteDoctypes'),('Create_Upload_Files_Interface','canReviseDoctypes'),('Create_Upload_Files_Interface','canDescribeDoctypes'),('Create_Upload_Files_Interface','canCommentDoctypes'),('Create_Upload_Files_Interface','canKeepDoctypes'),('Create_Upload_Files_Interface','canAddFormatDoctypes'),('Create_Upload_Files_Interface','canRestrictDoctypes'),('Create_Upload_Files_Interface','canRenameDoctypes'),('Create_Upload_Files_Interface','canNameNewFiles'),('Create_Upload_Files_Interface','createRelatedFormats'),('Create_Upload_Files_Interface','keepDefault'),('Create_Upload_Files_Interface','showLinks'),('Create_Upload_Files_Interface','fileLabel'),('Create_Upload_Files_Interface','filenameLabel'),('Create_Upload_Files_Interface','descriptionLabel'),('Create_Upload_Files_Interface','commentLabel'),('Create_Upload_Files_Interface','restrictionLabel'),('Create_Upload_Files_Interface','startDoc'),('Create_Upload_Files_Interface','endDoc'),('Create_Upload_Files_Interface','defaultFilenameDoctypes'),('Create_Upload_Files_Interface','maxFilesDoctypes'),('Move_Uploaded_Files_to_Storage','iconsize'),('Move_Uploaded_Files_to_Storage','createIconDoctypes'),('Move_Uploaded_Files_to_Storage','forceFileRevision'),('Move_Photos_to_Storage','iconsize'),('Move_Photos_to_Storage','iconformat'),('User_is_Record_Owner_or_Curator','curator_role'),('User_is_Record_Owner_or_Curator','curator_flag'),('JOBSUBMIT_Send_APP_Mail','authorfile'),('JOBSUBMIT_Send_APP_Mail','addressesAPP'),('JOBSUBMIT_Send_APP_Mail','newrnin'),('JOBSUBMIT_Send_APP_Mail','categformatAPP'),('JOBSUBMIT_Send_APP_Mail','edsrn'),('JOBSUBMIT_Send_APP_Mail','emailFile'),('JOBSUBMIT_Send_APP_Mail','decision_file'),('JOBSUBMIT_Send_APP_Mail','comments_file'),('JOBSUBMIT_Send_Approval_Request','contactnamefile'),('JOBSUBMIT_Send_Approval_Request','contactemailfile'),('JOBSUBMIT_Send_Approval_Request','referencefile'),('JOBSUBMIT_Send_Approval_Request','affiliationfile'),('JOBSUBMIT_Send_Approval_Request','regionfile'),('JOBSUBMIT_Send_Approval_Request','rankfile'),('JOBSUBMIT_Send_Approval_Request','fieldfile'),('JOBSUBMIT_Send_Approval_Request','experimentsfile'),('JOBSUBMIT_Send_Approval_Request','urlfile'),('JOBSUBMIT_Send_Approval_Request','datefile'),('JOBSUBMIT_Send_Approval_Request','abstractfile');" | $(BINDIR)/dbexec

	echo "INSERT INTO sbmFIELD VALUES ('MBIJOBSUBMIT',1,1,'JOBSUBMIT_IRN','<table width=\"100%\" bgcolor=\"#D3E3E2\" align=\"center\" cellspacing=\"2\" cellpadding=\"2\" border=\"1\"><tr><td align=\"left\"><br /><b>Modify an article\'s bibliographic information:</b><br /><br /><span style=\'color: red;\'>*</span>Document Reference Number:&nbsp;&nbsp;','M','Reference Number','','2011-09-21','2011-09-21',NULL,NULL),('MBIJOBSUBMIT',1,2,'JOBSUBMIT_CHANG','<br /><br /><span style=\"color: red;\">*</span>Choose the fields to be modified:<br />','O','Fields to Modify','','2011-09-21','2011-09-21',NULL,NULL),('MBIJOBSUBMIT',1,3,'JOBSUBMIT_CONT','<br /><br /></td></tr></table>','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,1,'JOBSUBMIT_TITLE','<TABLE CLASS="submission" WIDTH="100%" BGCOLOR=\"#D3E3E2\" ALIGN=\"center\" CELLSPACING=\"2\" CELLPADDING=\"2\" BORDER=\"1\"><TR><TD ALIGN=\"left\"><br /><b>Submit an Job Vacancy:</b><br /><br />Job Title:<br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,11,'JOBSUBMIT_DATE','<br /><br />Deadline Date: <i>(yyyy-mm-dd)</i><br />','O','','DatCheckNew','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,12,'JOBSUBMIT_ABSTR','<br /><br />Job Description:<br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,13,'JOBSUBMIT_END','<br /><br /></td></tr></table><br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,2,'JOBSUBMIT_CONTA','<br /><br />Contact name:</br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,3,'JOBSUBMIT_EMAIL','<br /><br />Contact email:<br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,4,'JOBSUBMIT_REFEM','<br /><br />Email for reference letters:<br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,5,'JOBSUBMIT_AFFIL','<br /><br />Affiliated institute:<br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,6,'JOBSUBMIT_REG','<br /><br />Region:<br />','O','','','2011-09-21','2011-09-29',NULL,NULL),('SBIJOBSUBMIT',1,7,'JOBSUBMIT_RANK','<br /><br />Rank: <br /><small><i>Hold the Control key to choose multiple ranks</i></small><br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,8,'JOBSUBMIT_FIELD','<br /><br />Field of interest: <br /><small><i>Hold the Control key to choose multiple fields</i></small><br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,9,'JOBSUBMIT_EXP','<br /><br />Experiment: <br /><small><i>Hold the Control key to choose multiple experiments</i></small><br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('SBIJOBSUBMIT',1,10,'JOBSUBMIT_URL','<br /><br />URL:<br />','O','','','2011-09-21','2011-09-21',NULL,NULL),('APPJOBSUBMIT',1,1,'JOBSUBMIT_IRN','<table width=\"100%\" bgcolor=\"#D3E3E2\" align=\"center\" cellspacing=\"2\" cellpadding=\"2\" border=\"1\"><tr><td align=\"left\"><br /><b>Approve or reject a JOB submission:</b><br /><br /><span style=\'color: red;\'>*</span>Job Reference Number:&nbsp;&nbsp;','M','Reference Number','','2011-10-18','2011-10-18',NULL,NULL),('APPJOBSUBMIT',1,2,'JOBSUBMIT_DECSN','<br /><br /><span style=\"color: red;\">*</span>Decision:<br /> ','M','Decision','','2011-10-18','2011-10-18',NULL,NULL),('APPJOBSUBMIT',1,3,'JOBSUBMIT_COMNT','<br /><br />Comments on Decision:<br />','O','Referee\'s Comments','','2011-10-18','2011-10-18',NULL,NULL),('APPJOBSUBMIT',1,4,'JOBSUBMIT_END','<br /><br /></td></tr></table>','O','','','2011-09-21','2011-09-21',NULL,NULL);" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmFIELDDESC VALUES ('JOBSUBMIT_ABSTR',NULL,'520__a','T',NULL,20,80,NULL,NULL,NULL,'2011-09-21','2011-09-21','<br />Job description:<br />',NULL,0),('JOBSUBMIT_AFFIL',NULL,'110__a','I',NULL,1,30,NULL,NULL,NULL,'2011-09-21','2011-09-21','<br />Affiliation:<br />',NULL,0),('JOBSUBMIT_CHANG',NULL,'','S',NULL,NULL,NULL,NULL,NULL,'<select name=\"JOBSUBMIT_CHANG[]\" size=\"8\" multiple>\n <option value=\"JOBSUBMIT_TITLE\">Title</option>\n <option value=\"JOBSUBMIT_CONTA\">Contact Name</option>\n <option value=\"JOBSUBMIT_EMAIL\">Contact Email</option>\n <option value=\"JOBSUBMIT_REFEM\">Reference Email</option>\n <option value=\"JOBSUBMIT_AFFIL\">Institute</option>\n <option value=\"JOBSUBMIT_REG\">Region</option>\n <option value=\"JOBSUBMIT_RANK\">Rank</option>\n <option value=\"JOBSUBMIT_FIELD\">Field of Interest</option>\n <option value=\"JOBSUBMIT_EXP\">Experiment</option>\n <option value=\"JOBSUBMIT_URL\">URL</option>\n <option value=\"JOBSUBMIT_DATE\">Deadline Date</option>\n <option value=\"JOBSUBMIT_ABSTR\">Job Description</option>\n</select>','2011-09-21','2011-09-21',NULL,NULL,0),('JOBSUBMIT_CONT',NULL,'','D',NULL,NULL,NULL,NULL,NULL,'<div align=\"center\">\n<input type=\"button\" class=\"adminbutton\" width=\"400\" height=\"50\" name=\"endS\" value=\"Continue\" onclick=\"finish();\" />\n</div>','2011-09-21','2011-09-21','<br />Contact name:<br />',NULL,0),('JOBSUBMIT_CONTA',NULL,'270__p','I',NULL,1,30,NULL,NULL,NULL,'2011-09-21','2011-09-21','<br />Contact name:<br />',NULL,0),('JOBSUBMIT_DATE',NULL,'046__i','D',NULL,1,30,NULL,NULL,'<input type=\"text\" value=\"\" onBlur=\"defText(this)\" onFocus=\"clearText(this)\" placeholder=\"yyyy-mm-dd\" id=\"datepicker\" name=\"JOBSUBMIT_DATE\">','2011-09-21','2011-12-05','<br />Deadline date:<br />',NULL,0),('JOBSUBMIT_EMAIL',NULL,'270__M','I',NULL,1,30,NULL,NULL,NULL,'2011-09-21','2011-09-21','<br />Contact email:<br />',NULL,0),('JOBSUBMIT_REFEM',NULL,'270__o','I',NULL,1,30,NULL,NULL,NULL,'2011-09-21','2011-09-21','<br />Email for reference letters:<br />',NULL,0),('JOBSUBMIT_END',NULL,'','D',NULL,NULL,NULL,NULL,NULL,'<INPUT TYPE=\"button\" class=\"submissionbutton\" name=\"JOBSUBMIT_END\" width=\"400\" height=\"50\" value=\"Finish Submission\" onclick=\"finish();\">','2011-09-21','2011-09-21',NULL,NULL,0),('JOBSUBMIT_EXP',NULL,'693__e','S',NULL,1,30,NULL,NULL,'<select name=\"JOBSUBMIT_EXP\" multiple=\"yes\"> \n<option value=\"AMANDA\">AMANDA</option> \n<option value=\"AMS\">AMS</option> \n<option value=\"ANTARES\">ANTARES</option> \n<option value=\"AUGER\">AUGER</option> \n<option value=\"BAIKAL\">BAIKAL</option> \n<option value=\"BEPC-BES\">BEPC-BES</option> \n<option value=\"BNL-E-0877\">BNL-E-0877</option> \n<option value=\"BNL-LEGS\">BNL-LEGS</option> \n<option value=\"BNL-RHIC-BRAHMS\">BNL-RHIC-BRAHMS</option> \n<option value=\"BNL-RHIC-PHENIX\">BNL-RHIC-PHENIX</option> \n<option value=\"BNL-RHIC-PHOBOS\">BNL-RHIC-PHOBOS</option> \n<option value=\"BNL-RHIC-STAR\">BNL-RHIC-STAR</option> \n<option value=\"CDMS\">CDMS</option> \n<option value=\"CERN-LEP-ALEPH\">CERN-LEP-ALEPH</option> \n<option value=\"CERN-LEP-DELPHI\">CERN-LEP-DELPHI</option> \n<option value=\"CERN-LEP-L3\">CERN-LEP-L3</option> \n<option value=\"CERN-LEP-OPAL\">CERN-LEP-OPAL</option> \n<option value=\"CERN-LHC-ALICE\">CERN-LHC-ALICE</option> \n<option value=\"CERN-LHC-ATLAS\">CERN-LHC-ATLAS</option> \n<option value=\"CERN-LHC-B\">CERN-LHC-B</option> \n<option value=\"CERN-LHC-CMS\">CERN-LHC-CMS</option> \n<option value=\"CERN-LHC-LHCB\">CERN-LHC-LHCB</option> \n<option value=\"CERN-NA-060\">CERN-NA-060</option> \n<option value=\"CERN-NA-061\">CERN-NA-061</option> \n<option value=\"CERN-NA-062\">CERN-NA-062</option> \n<option value=\"CERN-PS-214\">CERN-PS-214 (HARP)</option> \n<option value=\"CESR-CLEO\">CESR-CLEO</option> \n<option value=\"CESR-CLEO-C\">CESR-CLEO-C</option> \n<option value=\"CESR-CLEO-II\">CESR-CLEO-II</option> \n<option value=\"CHIMERA\">CHIMERA</option> \n<option value=\"COBRA\">COBRA</option> \n<option value=\"COSY-ANKE\">COSY-ANKE</option> \n<option value=\"cryoEDM\">cryoEDM</option> \n<option value=\"CUORE\">CUORE</option> \n<option value=\"DAYA-BAY\">DAYA-BAY</option> \n<option value=\"DESY-DORIS-ARGUS\">DESY-DORIS-ARGUS</option> \n<option value=\"DESY-HERA-B\">DESY-HERA-B</option> \n<option value=\"DESY-HERA-H1\">DESY-HERA-H1</option> \n<option value=\"DESY-HERA-HERMES\">DESY-HERA-HERMES</option> \n<option value=\"DESY-HERA-ZEUS\">DESY-HERA-ZEUS</option> \n<option value=\"DESY-PETRA-MARK-J\">DESY-PETRA-MARK-J</option> \n<option value=\"DESY-PETRA-PLUTO-2\">DESY-PETRA-PLUTO-2</option> \n<option value=\"DESY-PETRA-TASSO\">DESY-PETRA-TASSO</option> \n<option value=\"DOUBLE-CHOOZ\">DOUBLE-CHOOZ</option> \n<option value=\"DRIFT\">DRIFT</option> \n<option value=\"EXO\">EXO</option> \n<option value=\"FERMI-LAT\">FERMI-LAT</option> \n<option value=\"FNAL-E-0687\">FNAL-E-0687</option> \n<option value=\"FNAL-E-0690\">FNAL-E-0690</option> \n<option value=\"FNAL-E-0706\">FNAL-E-0706</option> \n<option value=\"FNAL-E-0740\">FNAL-E-0740 (D0 Run I)</option> \n<option value=\"FNAL-E-0741\">FNAL-E-0741 (CDF Run I)</option> \n<option value=\"FNAL-E-0799\">FNAL-E-0799 (KTeV)</option> \n<option value=\"FNAL-E-0823\">FNAL-E-0815 (NuTeV)</option> \n<option value=\"FNAL-E-0823\">FNAL-E-0823 (D0 Run II)</option> \n<option value=\"FNAL-E-0830\">FNAL-E-0830 (CDF Run II)</option> \n<option value=\"FNAL-E-0831\">FNAL-E-0831 (FOCUS)</option> \n<option value=\"FNAL-E-0832\">FNAL-E-0832 (KTeV)</option> \n<option value=\"FNAL-E-0872\">FNAL-E-0872 (DONUT)</option> \n<option value=\"FNAL-E-0875\">FNAL-E-0875 (MINOS)</option> \n<option value=\"FNAL-E-0886\">FNAL-E-0886 (FNPL)</option> \n<option value=\"FNAL-E-0892\">FNAL-E-0892 (USCMS)</option> \n<option value=\"FNAL-E-0898\">FNAL-E-0898 (MiniBooNE)</option> \n<option value=\"FNAL-E-0904\">FNAL-E-0904 (MUCOOL)</option> \n<option value=\"FNAL-E-0906\">FNAL-E-0906 (NuSea)</option> \n<option value=\"FNAL-E-0907\">FNAL-E-0907 (MIPP)</option> \n<option value=\"FNAL-E-0937\">FNAL-E-0937 (FINeSSE)</option> \n<option value=\"FNAL-E-0938\">FNAL-E-0938 (MINERvA)</option> \n<option value=\"FNAL-E-0954\">FNAL-E-0954 (SciBooNE)</option> \n<option value=\"FNAL-E-0961\">FNAL-E-0961 (COUPP)</option> \n<option value=\"FNAL-E-0974\">FNAL-E-0974</option> \n<option value=\"FNAL-LC\">FNAL-LC</option> \n<option value=\"FNAL-P-0929\">FNAL-P-0929 (NOvA)</option> \n<option value=\"FNAL-T-0962\">FNAL-T-0962 (ArgoNeuT)</option> \n<option value=\"FRASCATI-DAFNE-KLOE\">FRASCATI-DAFNE-KLOE</option> \n<option value=\"FREJUS-NEMO-3\">FREJUS-NEMO-3</option> \n<option value=\"GERDA\">GERDA</option> \n<option value=\"GSI-HADES\">GSI-HADES</option> \n<option value=\"GSI-SIS-ALADIN\">GSI-SIS-ALADIN</option> \n<option value=\"HARP\">HARP</option> \n<option value=\"HESS\">HESS</option> \n<option value=\"ICECUBE\">ICECUBE</option> \n<option value=\"ILC\">ILC</option> \n<option value=\"JLAB-E-01-104\">JLAB-E-01-104</option> \n<option value=\"KAMLAND\">KAMLAND</option> \n<option value=\"KASCADE-GRANDE\">KASCADE-GRANDE</option> \n<option value=\"KATRIN\">KATRIN</option> \n<option value=\"KEK-BF-BELLE\">KEK-BF-BELLE</option> \n<option value=\"KEK-BF-BELLE-II\">KEK-BF-BELLE-II</option> \n<option value=\"KEK-T2K\">KEK-T2K</option> \n<option value=\"LBNE\">LBNE</option> \n<option value=\"LIGO\">LIGO</option> \n<option value=\"LISA\">LISA</option> \n<option value=\"LSST\">LSST</option> \n<option value=\"MAGIC\">MAGIC</option> \n<option value=\"MAJORANA\">MAJORANA</option> \n<option value=\"MICE\">MICE</option> \n<option value=\"PLANCK\">PLANCK</option> \n<option value=\"SDSS\">SDSS</option> \n<option value=\"SLAC-PEP2-BABAR\">SLAC-PEP2-BABAR</option> \n<option value=\"SNAP\">SNAP</option> \n<option value=\"SSCL-GEM\">SSCL-GEM</option> \n<option value=\"SUDBURY-SNO\">SUDBURY-SNO</option> \n<option value=\"SUDBURY-SNO+\">SUDBURY-SNO+</option> \n<option value=\"SUPER-KAMIOKANDE\">SUPER-KAMIOKANDE</option> \n<option value=\"VERITAS\">VERITAS</option> \n<option value=\"VIRGO\">VIRGO</option> \n<option value=\"WASA-COSY\">WASA-COSY</option> \n<option value=\"WMAP\">WMAP</option> \n<option value=\"XENON\">XENON</option> \n</select> ','2011-09-21','2011-09-21','<br />Experiment:<br />',NULL,0),('JOBSUBMIT_FIELD',NULL,'65017a','S',NULL,1,30,NULL,NULL,'<select name=\"JOBSUBMIT_FIELD\" multiple=\"yes\"> \n<option value=\"astro-ph\">astro-ph</option>\n<option value=\"cond-mat\">cond-mat</option> \n<option value=\"cs\">cs</option> \n<option value=\"gr-qc\">gr-qc</option> \n<option value=\"hep-ex\">hep-ex</option> \n<option value=\"hep-lat\">hep-lat</option> \n<option value=\"hep-ph\">hep-ph</option> \n<option value=\"hep-th\">hep-th</option> \n<option value=\"math\">math</option> \n<option value=\"math-ph\">math-ph</option> \n<option value=\"nucl-ex\">nucl-ex</option> \n<option value=\"nucl-th\">nucl-th</option> \n<option value=\"physics.acc-phys\">physics.acc-phys</option> \n<option value=\"physics.ins-det\">physics.ins-det</option> \n<option value=\"physics-other\">physics-other</option> \n<option value=\"quant\">quant-ph</option>\n</select>','2011-09-21','2011-09-21','<br />Field of interest:<br />',NULL,0),('JOBSUBMIT_IRN',NULL,'970__a','I',NULL,NULL,NULL,NULL,NULL,NULL,'2011-09-21','2011-09-21',NULL,NULL,0),('JOBSUBMIT_RANK',NULL,'656__a','S',NULL,1,30,NULL,NULL,'<select name=\"JOBSUBMIT_RANK\" multiple=\"yes\">\n <option value=\"Senior\">Senior (permanent)</option>\n <option value=\"Junior\">Junior (leads to Senior)</option>\n <option value=\"Postdoc\">Postdoc</option>\n <option value=\"Student\">Student</option>\n <option value=\"Visitor\">Visiting Scientist</option>\n <option value=\"Staff\">Staff (non-research position)</option>\n</select>','2011-09-21','2011-09-21','<br />Rank:<br />',NULL,0),('JOBSUBMIT_REG',NULL,'043__a','S',NULL,1,30,NULL,NULL,'<select name=\"JOBSUBMIT_REG\">\n <option value=\"Africa\">Africa</option>\n <option value=\"Asia\">Asia</option>\n <option value=\"Australasia\">Australasia</option>\n <option value=\"Europe\">Europe</option>\n <option value=\"Middle East\">Middle East</option>\n <option value=\"North America\">North America</option>\n <option value=\"South America\">South America</option>\n </select>','2011-09-21','2011-09-29','<br />Region:<br />',NULL,0),('JOBSUBMIT_TITLE',NULL,'245__a','I',NULL,1,30,NULL,NULL,NULL,'2011-09-21','2011-09-21','<br />Title:<br />',NULL,0),('JOBSUBMIT_URL',NULL,'8564_u','I',NULL,1,30,NULL,NULL,NULL,'2011-09-21','2011-09-21','<br />URL:<br />',NULL,0),('JOBSUBMIT_DECSN',NULL,'','S',NULL,NULL,NULL,NULL,NULL,'<select name=\"JOBSUBMIT_DECSN\">\n<option value=\"Select:\">Select:</option>\n<option value=\"approve\">Approve</option>\n<option value=\"reject\">Reject</option>\n</select>','2011-10-18','2011-10-18',NULL,NULL,0),('JOBSUBMIT_COMNT',NULL,'','T',NULL,6,60,NULL,NULL,NULL,'2011-10-18','2011-10-18',NULL,NULL,0);" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmALLFUNCDESCR VALUES ('JOBSUBMIT_Mail_Submitter','This function send an email to the submitter to warn them that the document they have just submitted has been correctly received.  Parameters:    * authorfile: Name of the file containing the authors of the                 document    * titleFile: Name of'),('JOBSUBMIT_Print_Success','This function simply displays a text on the screen, telling the user the submission went fine. To be used in the \'Submit New Record\' action.  Parameters:     * status: Depending on the value of this parameter, the      function adds an additional text to '),('Ask_For_Record_Details_Confirmation',''),('CaseEDS',''),('Create_Modify_Interface',NULL),('Create_Recid',NULL),('Finish_Submission',''),('Get_Info',''),('Get_Recid','This function gets the recid for a document with a given report-number (as stored in the global variable rn).'),('Get_Report_Number',NULL),('Get_Sysno',NULL),('Insert_Modify_Record',''),('JOBSUBMIT_Insert_Record',NULL),('Is_Original_Submitter',''),('JOBSUBMIT_Is_Original_Submitter',''),('Is_Referee','This function checks whether the logged user is a referee for the current document'),('Mail_Approval_Request_to_Referee',NULL),('Mail_Approval_Withdrawn_to_Referee',NULL),('Mail_Submitter',NULL),('Make_Modify_Record',NULL),('Make_Record',''),('Move_From_Pending',''),('Move_to_Done',NULL),('Move_to_Pending',NULL),('Print_Success',''),('Print_Success_Approval_Request',NULL),('Print_Success_APP',''),('Print_Success_DEL','Prepare a message for the user informing them that their record was successfully deleted.'),('Print_Success_MBI',NULL),('Print_Success_SRV',NULL),('Register_Approval_Request',NULL),('Register_Referee_Decision',NULL),('Withdraw_Approval_Request',NULL),('Report_Number_Generation',NULL),('Second_Report_Number_Generation','Generate a secondary report number for a document.'),('JOBSUBMIT_Send_Approval_Request',NULL),('Send_APP_Mail',''),('Send_Delete_Mail',''),('Send_Modify_Mail',NULL),('Send_SRV_Mail',NULL),('Set_Embargo','Set an embargo on all the documents of a given record.'),('Stamp_Replace_Single_File_Approval','Stamp a single file when a document is approved.'),('Stamp_Uploaded_Files','Stamp some of the files that were uploaded during a submission.'),('Test_Status',''),('Update_Approval_DB',NULL),('User_is_Record_Owner_or_Curator','Check if user is owner or special editor of a record'),('Move_Files_to_Storage','Attach files received from chosen file input element(s)'),('Move_Revised_Files_to_Storage','Revise files initially uploaded with \"Move_Files_to_Storage\"'),('Make_Dummy_MARC_XML_Record',''),('Move_CKEditor_Files_to_Storage','Transfer files attached to the record with the CKEditor'),('Create_Upload_Files_Interface','Display generic interface to add/revise/delete files. To be used before function Move_Uploaded_Files_to_Storage'),('Move_Uploaded_Files_to_Storage','Attach files uploaded with \"Create_Upload_Files_Interface\"'),('Move_Photos_to_Storage','Attach/edit the pictures uploaded with the \"create_photos_manager_interface()\" function'),('JOBSUBMIT_Send_APP_Mail',NULL);" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmFUNCTIONS VALUES ('MBI','JOBSUBMIT','Create_Modify_Interface',40,1),('MBI','JOBSUBMIT','Get_Recid',20,1),('MBI','JOBSUBMIT','Get_Recid',20,2),('MBI','JOBSUBMIT','Get_Report_Number',10,1),('MBI','JOBSUBMIT','Get_Report_Number',10,2),('MBI','JOBSUBMIT','Insert_Modify_Record',50,2),('MBI','JOBSUBMIT','JOBSUBMIT_Is_Original_Submitter',30,1),('MBI','JOBSUBMIT','JOBSUBMIT_Is_Original_Submitter',30,2),('MBI','JOBSUBMIT','Make_Modify_Record',40,2),('MBI','JOBSUBMIT','Move_to_Done',80,2),('MBI','JOBSUBMIT','Print_Success_MBI',60,2),('MBI','JOBSUBMIT','Send_Modify_Mail',70,2),('SBI','JOBSUBMIT','JOBSUBMIT_Mail_Submitter',40,1),('SBI','JOBSUBMIT','Make_Dummy_MARC_XML_Record',30,1),('SBI','JOBSUBMIT','JOBSUBMIT_Print_Success',70,1),('SBI','JOBSUBMIT','Report_Number_Generation',20,1),('APP','JOBSUBMIT','Get_Report_Number',10,1),('APP','JOBSUBMIT','Test_Status',20,1),('APP','JOBSUBMIT','Is_Referee',30,1),('APP','JOBSUBMIT','CaseEDS',40,1),('APP','JOBSUBMIT','Print_Success_APP',80,2),('APP','JOBSUBMIT','Update_Approval_DB',70,2),('APP','JOBSUBMIT','JOBSUBMIT_Insert_Record',60,2),('APP','JOBSUBMIT','Make_Record',50,2),('APP','JOBSUBMIT','Get_Info',40,2),('APP','JOBSUBMIT','Get_Recid',30,2),('APP','JOBSUBMIT','Move_From_Pending',20,2),('SBI','JOBSUBMIT','Create_Recid',10,1),('SBI','JOBSUBMIT','Update_Approval_DB',50,1),('SBI','JOBSUBMIT','JOBSUBMIT_Send_Approval_Request',60,1),('SBI','JOBSUBMIT','Move_to_Pending',80,1),('APP','JOBSUBMIT','Get_Report_Number',10,3),('APP','JOBSUBMIT','Move_From_Pending',20,3),('APP','JOBSUBMIT','Get_Recid',30,3),('APP','JOBSUBMIT','Update_Approval_DB',50,3),('APP','JOBSUBMIT','Print_Success_APP',60,3),('APP','JOBSUBMIT','Get_Report_Number',10,2),('APP','JOBSUBMIT','Move_to_Done',70,3),('APP','JOBSUBMIT','Get_Info',40,3),('APP','JOBSUBMIT','Move_to_Done',100,2),('APP','JOBSUBMIT','JOBSUBMIT_Send_APP_Mail',90,2);" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmIMPLEMENT VALUES ('JOBSUBMIT','MBI','Y','MBIJOBSUBMIT',1,'2011-09-19','2011-09-21',2,'','',0,0,''),('JOBSUBMIT','SBI','Y','SBIJOBSUBMIT',1,'2011-08-24','2011-09-29',1,'','',0,0,' '),('JOBSUBMIT','APP','Y','APPJOBSUBMIT',1,'2011-10-18','2011-10-18',3,'','',0,1,'');" | $(BINDIR)/dbexec
	echo "INSERT INTO sbmCHECKS VALUES ('AUCheck','function AUCheck(txt) {\r\n	var res=1;\r\n	tmp=txt.indexOf(\"\\015\");\r\n	while (tmp != -1) {\r\n		left=txt.substring(0,tmp);\r\n		right=txt.substring(tmp+2,txt.length);\r\n		txt=left + \"\\012\" + right;\r\n		tmp=txt.indexOf(\"\\015\");\r\n	}\r\n	tmp=txt.indexOf(\"\\012\");\r\n	if (tmp==-1){\r\n		line=txt;\r\n	txt=\'\';}\r\n	else{\r\n		line=txt.substring(0,tmp);\r\n		txt=txt.substring(tmp+1,txt.length);}\r\n	while (line != \"\"){\r\n		coma=line.indexOf(\",\");\r\n		left=line.substring(0,coma);\r\n		right=line.substring(coma+1,line.length);\r\n		coma2=right.indexOf(\",\");\r\n		space=right.indexOf(\" \");\r\n		if ((coma==-1)||(left==\"\")||(right==\"\")||(space!=0)||(coma2!=-1)){\r\n			res=0;\r\n			error_log=line;\r\n		}\r\n		tmp=txt.indexOf(\"\\012\");\r\n		if (tmp==-1){\r\n	line=txt;\r\n			txt=\'\';}\r\n		else{\r\n			line=txt.substring(0,tmp-1);\r\n			txt=txt.substring(tmp+1,txt.length);}\r\n	}\r\n	if (res == 0){\r\n		alert(\"This author name cannot be managed \\: \\012\\012\" + error_log + \" \\012\\012It is not in the required format!\\012Put one author per line and a comma (,) between the name and the firstname initial letters. \\012The name is going first, followed by the firstname initial letters.\\012Do not forget the whitespace after the comma!!!\\012\\012Example \\: Put\\012\\012Le Meur, J Y \\012Baron, T \\012\\012for\\012\\012Le Meur Jean-Yves & Baron Thomas.\");\r\n		return 0;\r\n	}	\r\n	return 1;	\r\n}','1998-08-18','0000-00-00','',''),('DatCheckNew','function DatCheckNew(txt) {\r\n	var res=1;\r\n	if (txt.length != 10){res=0;}\r\n	if (txt.indexOf(\"-\") != 4){res=0;}\r\n	if (txt.lastIndexOf(\"-\") != 7){res=0;}\r\n	tmp=parseInt(txt.substring(8,10),10);\r\n	if ((tmp > 31)||(tmp < 1)||(isNaN(tmp))){res=0;}\r\n	tmp=parseInt(txt.substring(5,7),10);\r\n	if ((tmp > 12)||(tmp < 1)||(isNaN(tmp))){res=0;}\r\n	tmp=parseInt(txt.substring(0,4),10);\r\nif ((tmp < 1)||(isNaN(tmp))){res=0;}\r\n	if (txt.length  == 0){res=1;}\r\n	if (res == 0){\r\n		alert(\"Please enter a correct Date Format: YYYY-MM-DD\");\r\n		return 0;\r\n	}\r\n	return 1;\r\n}','0000-00-00','2011-11-29','','');" | $(BINDIR)/dbexec
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
	@echo ">>> Done reset-inspire-example-searches."
