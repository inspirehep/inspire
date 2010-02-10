# $Id$

include ../../config.mk

LIBFILES = *.py
BIBFORMATELEMENTSDIR = $(PREFIX)/lib/python/invenio/bibformat_elements

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(LIBFILES) $(BIBFORMATELEMENTSDIR)

clean:
	@rm -f *.orig *~
