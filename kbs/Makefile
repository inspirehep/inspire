include ../config.mk

WEBDESC='Mapping of SPIRES abbreviations for URLs to Displayable names'
OADESC='Journals that are fully OA'
PWD=`pwd`

install: all

all:
	@echo "Loading knowledge bases..."
	make delete-weblinks
	make delete-oalinks
	make delete-talktype
	make load-weblinks-knowledge-base
	make load-weblinks-knowledge-base
	make load-talktype-knowledge-base
	@echo "Done."

test:
	@echo "Not Implemented."

delete-weblinks:
	echo "DELETE FROM fmtKNOWLEDGEBASEMAPPINGS where id_fmtKNOWLEDGEBASES=(SELECT id from fmtKNOWLEDGEBASES where name='WEBLINKS')" | $(BINDIR)/dbexec

delete-oalinks:
	echo "DELETE FROM fmtKNOWLEDGEBASEMAPPINGS where id_fmtKNOWLEDGEBASES=(SELECT id from fmtKNOWLEDGEBASES where name='OALINKS')" | $(BINDIR)/dbexec

delete-talktype:
	echo "DELETE FROM fmtKNOWLEDGEBASEMAPPINGS where id_fmtKNOWLEDGEBASES=(SELECT id from fmtKNOWLEDGEBASES where name='TALKTYPE')" | $(BINDIR)/dbexec

load-weblinks-knowledge-base:
	echo "INSERT into fmtKNOWLEDGEBASES (name, description) VALUES('WEBLINKS',$(WEBDESC)) on duplicate key update description = $(WEBDESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like fmtKNOWLEDGEBASEMAPPINGS;\
LOAD DATA LOCAL INFILE '$(PWD)/weblinks.dat' replace INTO TABLE templinks;\
update templinks set id_fmtKNOWLEDGEBASES= (select id from fmtKNOWLEDGEBASES where name='WEBLINKS');\
insert into  fmtKNOWLEDGEBASEMAPPINGS  (m_key,m_value,id_fmtKNOWLEDGEBASES) select m_key,m_value,id_fmtKNOWLEDGEBASES from templinks ;\
"|$(BINDIR)/dbexec

load-oalinks-knowledge-base:
	echo "INSERT into fmtKNOWLEDGEBASES (name, description) VALUES('OALINKS',$(OADESC)) on duplicate key update description = $(OADESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like fmtKNOWLEDGEBASEMAPPINGS;\
LOAD DATA LOCAL INFILE '$(PWD)/oalinks.dat' replace INTO TABLE templinks;\
update templinks set id_fmtKNOWLEDGEBASES= (select id from fmtKNOWLEDGEBASES where name='WEBLINKS');\
insert into  fmtKNOWLEDGEBASEMAPPINGS  (m_key,m_value,id_fmtKNOWLEDGEBASES) select m_key,m_value,id_fmtKNOWLEDGEBASES from templinks ;\
"|$(BINDIR)/dbexec

load-talktype-knowledge-base:
	echo "INSERT into fmtKNOWLEDGEBASES (name, description) VALUES('TALKTYPE',$(WEBDESC)) on duplicate key update description = $(WEBDESC)" | $(BINDIR)/dbexec
	echo " create temporary table templinks like fmtKNOWLEDGEBASEMAPPINGS;\
LOAD DATA LOCAL INFILE '$(PWD)/talktype.kba' replace INTO TABLE templinks;\
update templinks set id_fmtKNOWLEDGEBASES= (select id from fmtKNOWLEDGEBASES where name='TALKTYPE');\
insert into  fmtKNOWLEDGEBASEMAPPINGS  (m_key,id_fmtKNOWLEDGEBASES) select m_key,id_fmtKNOWLEDGEBASES from templinks ;\
"|$(BINDIR)/dbexec


clean:
	@rm -f *.orig *~
