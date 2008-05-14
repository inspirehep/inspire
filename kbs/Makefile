include ../config.mk


WLDESC='Mapping of SPIRES abbreviations for URLs to Displayable names'
OADESC='Journals that are fully OA'

install:all

all:
	make delete-weblinks
	make delete-oalinks
	make load-weblinks-knowledge-base
	make load-oalinks-knowledge-base

load-weblinks-knowledge-base:
	echo "INSERT into  fmtKNOWLEDGEBASES (name, description) VALUES('WEBLINKS',$(WLDESC)) on duplicate key update description = $(WLDESC)" | $(BINDIR)/dbexec
	echo "LOAD DATA LOCAL INFILE '/home/tcb/inspire_code/inspire/kbs/weblinks.dat' replace INTO TABLE fmtKNOWLEDGEBASEMAPPINGS (m_key, m_value) set id_fmtKNOWLEDGEBASES=(SELECT id from fmtKNOWLEDGEBASES where name='WEBLINKS')" | $(BINDIR)/dbexec


load-oalinks-knowledge-base:
	echo "INSERT into  fmtKNOWLEDGEBASES (name, description) VALUES('OALINKS',$(OADESC)) on duplicate key update description = $(OADESC)" | $(BINDIR)/dbexec
	echo "LOAD DATA LOCAL INFILE '/home/tcb/inspire_code/inspire/kbs/oalinks.dat' replace INTO TABLE fmtKNOWLEDGEBASEMAPPINGS (m_key, m_value) set id_fmtKNOWLEDGEBASES=(SELECT id from fmtKNOWLEDGEBASES where name='OALINKS')" | $(BINDIR)/dbexec

delete-weblinks:
	echo "DELETE FROM fmtKNOWLEDGEBASEMAPPINGS where id_fmtKNOWLEDGEBASES=(SELECT id from fmtKNOWLEDGEBASES where name='WEBLINKS')" | $(BINDIR)/dbexec
delete-oalinks:
	echo "DELETE FROM fmtKNOWLEDGEBASEMAPPINGS where id_fmtKNOWLEDGEBASES=(SELECT id from fmtKNOWLEDGEBASES where name='OALINKS')" | $(BINDIR)/dbexec