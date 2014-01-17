# $Id$

include ../../config.mk
-include ../../config-local.mk

LIBFILES = *.py

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(LIBDIR)/python/invenio/bibedit_ticket_templates
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)/python/invenio/bibedit_ticket_templates

clean:
	@rm -f *.orig *~