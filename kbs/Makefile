include ../config.mk
-include ../config-local.mk

WEBDESC='Mapping of SPIRES abbreviations for URLs to Displayable names'
OADESC='Journals that are fully OA'
CODDESC='Coden to short title mappings'
JOURNALDESC='Mapping of journal abbreviations to full names'
TALKTYPEDESC='List of types of talks'
COLLECTIONDESC='690C aliases'
SUBJECTDESC='65017 aliases'
PWD=`pwd`

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) journal-titles-inspire.kb $(ETCDIR)/refextract/journal-titles-inspire.kb

install-dbchanges: announce-kb-load weblinks oalinks journals talktype type subject create-institutions-dynamic-kb
	@echo "Done."

weblinks: delete-weblinks load-weblinks-knowledge-base
oalinks: delete-oalinks load-oalinks-knowledge-base
journals: delete-journals load-journals-knowledge-base
talktype: delete-talktype load-talktype-knowledge-base
type: delete-type load-type-knowledge-base
subject: delete-subject load-subject-knowledge-base

announce-kb-load:
	@echo "Loading knowledge bases into DB..."

delete-weblinks:
	echo "DELETE FROM knwKBRVAL where id_knwKB=(SELECT id from knwKB where name='WEBLINKS')" | $(BINDIR)/dbexec

delete-coden:
	echo "DELETE FROM knwKBRVAL where id_knwKB=(SELECT id from knwKB where name='CODENS')" | $(BINDIR)/dbexec

delete-oalinks:
	echo "DELETE FROM knwKBRVAL where id_knwKB=(SELECT id from knwKB where name='OALINKS')" | $(BINDIR)/dbexec

delete-journals:
	echo "DELETE FROM knwKBRVAL where id_knwKB=(SELECT id from knwKB where name='JOURNALS')" | $(BINDIR)/dbexec

delete-talktype:
	echo "DELETE FROM knwKBRVAL where id_knwKB=(SELECT id from knwKB where name='TALKTYPE')" | $(BINDIR)/dbexec

delete-type:
	echo "DELETE FROM knwKBRVAL where id_knwKB=(SELECT id from knwKB where name='COLLECTION')" | $(BINDIR)/dbexec

delete-subject:
	echo "DELETE FROM knwKBRVAL where id_knwKB=(SELECT id from knwKB where name='SUBJECT')" | $(BINDIR)/dbexec

load-weblinks-knowledge-base:
	echo "INSERT into knwKB (name, description) VALUES('WEBLINKS',$(WEBDESC)) on duplicate key update description = $(WEBDESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like knwKBRVAL;\
LOAD DATA LOCAL INFILE '$(PWD)/weblinks.dat' replace INTO TABLE templinks;\
update templinks set id_knwKB= (select id from knwKB where name='WEBLINKS');\
insert into  knwKBRVAL  (m_key,m_value,id_knwKB) select m_key,m_value,id_knwKB from templinks ;\
"|$(BINDIR)/dbexec

KBNAME="CODENS"
KBFILE="coden.kb"
KBTMP="tempcoden"
load-coden-knowledge-base:
	echo "INSERT into knwKB (name, description) VALUES('$(KBNAME)',$(CODDESC)) on duplicate key update description = $(CODDESC)" | $(BINDIR)/dbexec
	echo " create temporary table $(KBTMP) like knwKBRVAL;\
LOAD DATA LOCAL INFILE '$(PWD)/$(KBFILE)' replace INTO TABLE $(KBTMP);\
update $(KBTMP) set id_knwKB= (select id from knwKB where name='$(KBNAME)');\
insert into  knwKBRVAL  (m_key,m_value,id_knwKB) select m_key,m_value,id_knwKB from $(KBTMP) ;\
"|$(BINDIR)/dbexec

load-oalinks-knowledge-base:
	echo "INSERT into knwKB (name, description) VALUES('OALINKS',$(OADESC)) on duplicate key update description = $(OADESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like knwKBRVAL;\
LOAD DATA LOCAL INFILE '$(PWD)/oalinks.dat' replace INTO TABLE templinks;\
update templinks set id_knwKB= (select id from knwKB where name='OALINKS');\
insert into  knwKBRVAL  (m_key,m_value,id_knwKB) select m_key,m_value,id_knwKB from templinks ;\
"|$(BINDIR)/dbexec

load-journals-knowledge-base:
	echo "INSERT into knwKB (name, description) VALUES('JOURNALS',$(JOURNALDESC)) on duplicate key update description = $(JOURNALDESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like knwKBRVAL;\
LOAD DATA LOCAL INFILE '$(PWD)/journal.kb' replace INTO TABLE templinks;\
update templinks set id_knwKB= (select id from knwKB where name='JOURNALS');\
insert into  knwKBRVAL  (m_key,m_value,id_knwKB) select m_key,m_value,id_knwKB from templinks ;\
"|$(BINDIR)/dbexec

load-type-knowledge-base:
	echo "INSERT into knwKB (name, description) VALUES('COLLECTION',$(COLLECTIONDESC)) on duplicate key update description = $(COLLECTIONDESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like knwKBRVAL;\
LOAD DATA LOCAL INFILE '$(PWD)/collection.kb' replace INTO TABLE templinks;\
update templinks set id_knwKB= (select id from knwKB where name='COLLECTION');\
insert into  knwKBRVAL  (m_key,m_value,id_knwKB) select m_key,m_value,id_knwKB from templinks ;\
"|$(BINDIR)/dbexec

load-subject-knowledge-base:
	echo "INSERT into knwKB (name, description) VALUES('SUBJECT',$(SUBJECTDESC)) on duplicate key update description = $(SUBJECTDESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like knwKBRVAL;\
LOAD DATA LOCAL INFILE '$(PWD)/subject.kb' replace INTO TABLE templinks;\
update templinks set id_knwKB= (select id from knwKB where name='SUBJECT');\
insert into  knwKBRVAL  (m_key,m_value,id_knwKB) select m_key,m_value,id_knwKB from templinks ;\
"|$(BINDIR)/dbexec

load-talktype-knowledge-base:
	echo "INSERT into knwKB (name, description) VALUES('TALKTYPE',$(TALKTYPEDESC)) on duplicate key update description = $(TALKTYPEDESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like knwKBRVAL;\
LOAD DATA LOCAL INFILE '$(PWD)/talktype.kba' replace INTO TABLE templinks;\
update templinks set id_knwKB= (select id from knwKB where name='TALKTYPE');\
insert into  knwKBRVAL  (m_key,id_knwKB) select m_key,id_knwKB from templinks ;\
"|$(BINDIR)/dbexec

create-institutions-dynamic-kb:
	$(PYTHON) InstitutionsCollection_dynamic_KB.py

clean:
	@rm -f *.orig *~
