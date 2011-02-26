include config.mk
-include config-local.mk
#
# Note that local makefile configurations can be defined in config-local.mk to override config.mk

SUBDIRS = bibconvert bibformat webstyle bibrank conf bibedit webhelp feedboxes bibharvest

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
                 reset-inspire-format-configuration \
                 reset-inspire-portalbox-configuration \
                 reset-inspire-format-configuration \
		 reset-inspire-examples-searches 
	@echo "Installing database changes..."
	@cd kbs && make install-dbchanges && cd ..
	@echo "Done."

reset-ugly-ui:
	@cd webstyle && make install-ugly && cd ..

reset-normal-ui:
	@cd webstyle && make install && cd ..

clean:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make clean && cd .. ;)
	@rm -f *.orig *~
	@echo "Done."

reset-inspire-field-configuration:
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
	echo "INSERT INTO tag (id,name,value) VALUES (64, 'indicator','690C_a')" | $(BINDIR)/dbexec
### now add Inst values:
	echo "INSERT INTO tag (id,name,value) VALUES (65, 'address','371__a')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (66, 'postal code','371__e')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (67, 'country','371__d')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (68, 'city','371__b')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (69, 'region code','371__f')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (70, 'state/province','410__g')" | $(BINDIR)/dbexec
	echo "INSERT INTO tag (id,name,value) VALUES (71, 'institution name','110__u')" | $(BINDIR)/dbexec
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
	echo "INSERT INTO field (id,name,code) VALUES (16, 'collaboration', 'collaboration')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (17, 'exact author', 'exactauthor')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (18, 'date created', 'datecreated')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (19, 'date modified', 'datemodified')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (20, 'refers to', 'refersto')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (21, 'cited by', 'citedby')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (22, 'fulltext', 'fulltext')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (23, 'caption', 'caption')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (24, 'first author','firstauthor')" | $(BINDIR)/dbexec
	####inst fields
	echo "INSERT INTO field (id,name,code) VALUES (25, 'address', 'address')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (26, 'postal code', 'postal_code')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (27, 'country', 'country')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (28, 'city', 'city')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (29, 'region', 'region')" | $(BINDIR)/dbexec
	echo "INSERT INTO field (id,name,code) VALUES (30, 'institution name', 'institution_name')" | $(BINDIR)/dbexec
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
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (16, 35, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (17, 8, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (17, 11, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (17, 29, 70)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (17, 32, 60)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (22, 44, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (23, 46, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (24, 8, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (24, 11, 90)" | $(BINDIR)/dbexec
	### inst field_tags
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (25,	65, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (25, 66, 120)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (25, 67, 110)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (25, 68, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (25, 69, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (25, 70, 80)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (25, 71, 200)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (26, 66, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (27, 67, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (28, 68, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (29, 69, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (29,	70, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO field_tag (id_field,id_tag,score) VALUES (30,	71, 90)" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-field-configuration."

reset-inspire-index-configuration:
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
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (10, 'affiliation', 'affiliation', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (11, 'collaboration', 'collaboration', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (12, 'exactauthor', 'exactauthor', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (13, 'fulltext', 'fulltext', '0000-00-00 00:00:00', 'en')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (14, 'caption', 'caption', '0000-00-00 00:00:00', 'en')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (15, 'firstauthor', 'firstauthor', '0000-00-00 00:00:00', 'en')" | $(BINDIR)/dbexec
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
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (10, 15)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (11, 16)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (12, 17)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (13, 22)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (14, 23)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (15, 24)" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-index-configuration."
<<<<<<< HEAD
# add address to global index
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (1, 25)" | $(BINDIR)/dbexec
=======
	## inst indexes:
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (16, 'address', 'address', '0000-00-00 00:00:00', 'en')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (17, 'postalcode', 'postal code', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX (id,name,description,last_updated,stemming_language) VALUES (18, 'institution', 'institution', '0000-00-00 00:00:00', '')" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (16, 25)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (17, 26)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (18, 30)" | $(BINDIR)/dbexec
	echo "INSERT INTO idxINDEX_field (id_idxINDEX,id_field) VALUES (1, 25)" | $(BINDIR)/dbexec

	echo "CREATE TABLE IF NOT EXISTS idxPAIR17F (\
  id mediumint(9) unsigned NOT NULL auto_increment,\
  term varchar(100) default NULL,\
  hitlist longblob,\
  PRIMARY KEY  (id),\
  UNIQUE KEY term (term)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxPAIR17R (\
  id_bibrec mediumint(9) unsigned NOT NULL,\
  termlist longblob,\
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',\
  PRIMARY KEY (id_bibrec,type)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxPHRASE17F (\
  id mediumint(9) unsigned NOT NULL auto_increment,\
  term text default NULL,\
  hitlist longblob,\
  PRIMARY KEY  (id),\
  KEY term (term(50))\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxPHRASE17R (\
  id_bibrec mediumint(9) unsigned NOT NULL,\
  termlist longblob,\
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',\
  PRIMARY KEY (id_bibrec,type)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxWORD17F (\
  id mediumint(9) unsigned NOT NULL auto_increment,\
  term varchar(50) default NULL,\
  hitlist longblob,\
  PRIMARY KEY  (id),\
  UNIQUE KEY term (term)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxWORD17R (\
  id_bibrec mediumint(9) unsigned NOT NULL,\
  termlist longblob,\
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',\
  PRIMARY KEY (id_bibrec,type)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxPAIR18F (\
  id mediumint(9) unsigned NOT NULL auto_increment,\
  term varchar(100) default NULL,\
  hitlist longblob,\
  PRIMARY KEY  (id),\
  UNIQUE KEY term (term)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxPAIR18R (\
  id_bibrec mediumint(9) unsigned NOT NULL,\
  termlist longblob,\
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',\
  PRIMARY KEY (id_bibrec,type)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxPHRASE18F (\
  id mediumint(9) unsigned NOT NULL auto_increment,\
  term text default NULL,\
  hitlist longblob,\
  PRIMARY KEY  (id),\
  KEY term (term(50))\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxPHRASE18R (\
  id_bibrec mediumint(9) unsigned NOT NULL,\
  termlist longblob,\
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',\
  PRIMARY KEY (id_bibrec,type)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxWORD18F (\
  id mediumint(9) unsigned NOT NULL auto_increment,\
  term varchar(50) default NULL,\
  hitlist longblob,\
  PRIMARY KEY  (id),\
  UNIQUE KEY term (term)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec
	echo "CREATE TABLE IF NOT EXISTS idxWORD18R (\
  id_bibrec mediumint(9) unsigned NOT NULL,\
  termlist longblob,\
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',\
  PRIMARY KEY (id_bibrec,type)\
) ENGINE=MyISAM;" | $(BINDIR)/dbexec

reset-inspire-collection-configuration:
	echo "TRUNCATE collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collectionname" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_collection" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_portalbox" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_rnkMETHOD" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (1, 'HEP', 'collection:HEP or 970__a:\'SPIRES\'', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection VALUES (2, 'Institutions',	'collection:INSTITUTION', 0, NULL)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 1, 200)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_rnkMETHOD VALUES (1, 3, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'en', 'ln', 'HEP')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (1, 'fr', 'ln', 'HEP')" |$(BINDIR)/dbexec
	echo "INSERT INTO collectionname VALUES (2, 'en', 'ln', 'Institutions')" | $(BINDIR)/dbexec
	echo "DELETE FROM collection_externalcollection WHERE id_collection >= 2" | $(BINDIR)/dbexec
	echo "UPDATE collection_externalcollection SET type=1 WHERE type=2" | $(BINDIR)/dbexec
	echo "TRUNCATE collectiondetailedrecordpagetabs" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (1, 'metadata;references;citations;files;plots')" | $(BINDIR)/dbexec
	echo "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (2, 'metadata')" | $(BINDIR)/dbexec

	$(BINDIR)/webcoll -u admin
	@echo "Please run the webcoll task just submitted, if your bibsched daemon is not in an automatic mode."

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
## Now add to the second colelction
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'bg', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'ca', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'de', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'el', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'en', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'es', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'fr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'hr', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'it', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'ja', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'no', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'pl', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'pt', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'sk', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'sv', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'zh_CN', 'rt', 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_portalbox VALUES (2, 2, 'zh_TW', 'rt', 100)" | $(BINDIR)/dbexec
		# now update portalbox value with placeholder text
	echo "UPDATE portalbox SET body=' ' WHERE id=2"|$(BINDIR)/dbexec
		## and now update portalbox values with RSS feed material
	$(PYTHON) ./feedboxes/inspire_update_feedboxes.py -d
	@echo ">>> Done. You may want to run 'webcoll -u admin -f' to see the new portalboxes."

reset-inspire-search-sort-field-configuration:
	@echo ">>> Resetting search/sort field configuration:"
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
	@echo ">>> Done reset-inspire-search-sort-field-configuration."
	@echo ">>> Adding inst search/sort field configuration:"
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (2, 25, NULL, 'sew', 50, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (2, 26, NULL, 'sew', 10, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (2, 27, NULL, 'sew', 25, 0)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_field_fieldvalue (id_collection, id_field, id_fieldvalue, type, score, score_fieldvalue) VALUES (2, 30, NULL, 'sew', 100, 0)" | $(BINDIR)/dbexec
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
	(22, 'LaTeX (US)', 'hlxu', 'LaTeX formatted reference (US Style)',\
	'text/html', 1);" | $(BINDIR)/dbexec
	echo "TRUNCATE collection_format" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (2, 1, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (2, 2, 120)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 18, 110)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 8, 100)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 21, 90)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 22, 80)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 9, 50)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 19, 10)" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-format-configuration."
	@echo ">>> Adding format configuration for inst:"
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 1, 130)" | $(BINDIR)/dbexec
	echo "INSERT INTO collection_format (id_collection, id_format, score) VALUES (1, 2, 120)" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-inst-format-configuration."



reset-inspire-examples-searches:
	@echo ">>> Resetting example searches:"
	echo "TRUNCATE collection_example" | $(BINDIR)/dbexec
	echo "TRUNCATE example" | $(BINDIR)/dbexec
	cat webhelp/search_examples.dat |  $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example)	select 1, example.id from example where example.type='HEP';" | $(BINDIR)/dbexec
	echo "insert into collection_example (id_collection,id_example)	select 2, example.id from example where example.type='Institutions';" | $(BINDIR)/dbexec
	@echo ">>> Done reset-inspire-example-searches."



