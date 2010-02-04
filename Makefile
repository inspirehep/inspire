include config.mk
-include config-local.mk
#
# Note that local makefile configurations can be defined in config-local.mk to override config.mk

SUBDIRS = bibconvert bibformat webstyle bibrank conf editor

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

install-dbchanges: reset-inspire-test-site-field-configuration reset-inspire-test-site-collection-configuration
	@echo "Installing database changes..."
	@cd kbs && make install && cd ..
	@echo "Done."

clean:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make clean && cd .. ;)
	@rm -f *.orig *~
	@echo "Done."

reset-inspire-test-site-field-configuration:
	@echo ">>> Resetting table tag:"
	echo "TRUNCATE tag" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (1, 'ext system source', '035__9')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (2, 'ext system ID', '035__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (3, 'ext system ID deprecated', '035__z')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (4, 'report number source', '037__9')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (5, 'report number', '037__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (6, 'report number category', '037__c')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (7, 'language', '041__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (8, 'first author name', '100__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (9, 'first author ID', '100__i')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (10, 'first author other ID', '100__j')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (11, 'first author alternative name', '100__q')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (12, 'first author affiliation', '100__u')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (13, 'title abbreviated', '210__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (14, 'title', '245__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (15, 'title tex source', '246__9')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (16, 'title tex', '246__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (17, 'numberofpages', '300__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (18, 'note', '500__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (19, 'abstract source', '520__9')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (20, 'abstract', '520__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (21, 'internal note source', '595__9')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (22, 'internal note', '595__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (23, 'uncontrolled keyword source', '6531_9')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (24, 'uncontrolled keyword', '6531_a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (26, 'experiment', '693__e')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (27, 'controlled keyword authority', '695__2')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (28, 'controlled keyword', '695__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (29, 'additional author name', '700__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (30, 'additional author ID', '700__i')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (31, 'additional author other ID', '700__j')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (32, 'additional author alternative name', '700__q')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (33, 'additional author affiliation', '700__u')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (34, 'corporate name', '710__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (35, 'collaboration', '710__g')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (36, 'journal publication doi', '773__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (37, 'journal publication page', '773__c')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (38, 'journal publication title', '773__p')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (39, 'conference publication leading text', '773__t')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (40, 'journal publication volume', '773__v')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (41, 'conference publication conference code', '773__w')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (42, 'journal publication legacy freetext', '773__x')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (43, 'journal publication year', '773__y')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (44, 'url', '8564_u')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (45, 'url record control number', '8564_w')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (46, 'url label', '8564_y')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (47, 'other affiliations', '902__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (48, 'cataloging date update', '961__c')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (49, 'cataloging date creation', '961__x')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (50, 'SPIRES IRN', '970__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (51, 'collection', '980__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (52, 'collection deleted', '980__c')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (53, 'reference report number', '999C5r')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (54, 'reference journal', '999C5s')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (55, 'record ID', '001')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (56, 'journal', '773__%')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (57, 'translated title', '242__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (58, 'translated title language', '242__y')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (59, 'reference doi', '999C5a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (60, 'date', '269__c')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (61, 'subject authority', '650172')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (62, 'subject', '65017a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (63, 'indicator authority', '690C_2')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (64, 'indicator', '690C_a')" | $(BINDIR)/dbexec
	@echo ">>> Resetting table field:"
	echo "TRUNCATE field" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (1, 'any field', 'anyfield')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (2, 'title', 'title')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (3, 'author', 'author')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (4, 'abstract', 'abstract')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (5, 'keyword', 'keyword')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (6, 'report number', 'reportnumber')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (7, 'subject', 'subject')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (8, 'reference', 'reference')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (9, 'collection', 'collection')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (10, 'year', 'year')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (11, 'experiment', 'experiment')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (12, 'doi', 'doi')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (13, 'journal', 'journal')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (14, 'record ID', 'recid')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (15, 'affiliation', 'affiliation')" | $(BINDIR)/dbexec
	@echo ">>> Resetting table fieldname:"
	echo "TRUNCATE fieldname" | $(BINDIR)/dbexec
	@echo ">>> Resetting table field_tag:"
	echo "TRUNCATE field_tag" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 2, 360)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 3, 350)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 5, 340)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 6, 330)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 7, 320)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 8, 310)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 11, 300)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 12, 290)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 13, 280)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 14, 270)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 16, 260)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 18, 250)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 20, 240)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 24, 230)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 26, 220)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 28, 210)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 29, 200)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 32, 190)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 33, 180)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 34, 170)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 35, 160)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 36, 150)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 37, 140)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 38, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 39, 120)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 40, 110)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 41, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 42, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 43, 80)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 47, 70)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 57, 50)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 58, 40)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 60, 30)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (1, 62, 20)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (2, 14, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (2, 16, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (2, 57, 80)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (2, 13, 70)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (3, 8, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (3, 11, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (3, 29, 70)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (3, 32, 60)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (4, 20, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (5, 28, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (5, 24, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (6, 5, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (7, 62, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (8, 53, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (8, 54, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (9, 51, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (10, 60, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (10, 43, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (11, 26, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (12, 36, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (13, 56, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (14, 55, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (15, 12, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (15, 33, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (15, 47, 80)" | $(BINDIR)/dbexec
	@echo ">>> Resetting table idxINDEX:"
	echo "TRUNCATE idxINDEX" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (1, 'global', 'global', '0000-00-00 00:00:00', 'en')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (2, 'collection', 'collection', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (3, 'author', 'author', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (4, 'keyword', 'keyword', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (5, 'reference', 'reference', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (6, 'reportnumber', 'reportnumber', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (7, 'title', 'title', '0000-00-00 00:00:00', 'en')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (8, 'year', 'year', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (9, 'journal', 'journal', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	@echo ">>> Resetting table idxINDEX_field:"
	echo "TRUNCATE idxINDEX_field" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (1, 1)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (2, 9)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (3, 3)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (4, 5)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (5, 8)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (6, 6)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (7, 2)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (8, 10)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (9, 13)" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-test-site-field-configuration."
	@echo ">>> You may want to run inveniocfg --reset-fieldnames now."

reset-inspire-test-site-collection-configuration:
	echo "TRUNCATE collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collectionname" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_portalbox" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_rnkMETHOD" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (1, 'HEP', '970__a:\'SPIRES\'', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (2, 'Institutions', '980__a:"INSTITUTIONS"', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 1, 200)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 3, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'en', 'ln', 'HEP')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'fr', 'ln', 'HEP')" |$(BINDIR)/dbexec
	echo "DELETE FROM collection_externalcollection WHERE id_collection >= 2" | $(BINDIR)/dbexec
	echo "UPDATE collection_externalcollection SET type=1 WHERE type=2" | $(BINDIR)/dbexec

	$(BINDIR)/webcoll -u admin
#	@sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/webcoll -u admin 
	@echo "Please run the webcoll task just submitted, if your bibsched daemon is not in an automatic mode."
