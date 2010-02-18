include ../config.mk
-include ../config-local.mk

XMLFILES = *.xml
XMLDIR = $(ETCDIR)/bibedit/record_templates

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(XMLFILES) $(XMLDIR)

clean:
	@rm -f *.orig *~
