include ../config.mk
-include ../config-local.mk

XMLRECORDFILES = record_*.xml
XMLRECORDDIR = $(ETCDIR)/bibedit/record_templates
XMLFIELDFILES = field_*.xml
XMLFIELDDIR = $(ETCDIR)/bibedit/field_templates

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(XMLRECORDFILES) $(XMLRECORDDIR)
	$(INSTALL) -m 664 $(XMLFIELDFILES) $(XMLFIELDDIR)

clean:
	@rm -f *.orig *~
