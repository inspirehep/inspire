# $Id$

include ../../config.mk
-include ../../config-local.mk

LIBFILES = *.py
BIBCHECKPLUGINSDIR = $(PREFIX)/lib/python/invenio/bibcheck_plugins

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(LIBFILES) $(BIBCHECKPLUGINSDIR)

clean:
	@rm -f *.orig *~
