include ../config.mk
-include ../config-local.mk

XMLRECORDFILES = record_*.xml
XMLRECORDDIR = $(ETCDIR)/bibedit/record_templates
XMLFIELDFILES = field_*.xml
XMLFIELDDIR = $(ETCDIR)/bibedit/field_templates

SUBDIRS = ticket_templates

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Nothing to test."

install:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)

	$(INSTALL) -m 664 $(XMLRECORDFILES) $(XMLRECORDDIR)
	$(INSTALL) -m 664 $(XMLFIELDFILES) $(XMLFIELDDIR)

clean:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make clean && cd .. ;)
	@rm -f *.orig *~
