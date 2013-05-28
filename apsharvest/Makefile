# $Id$

include ../config.mk
-include ../config-local.mk

LIBFILES = *.py
XSLT = *.xsl

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)/python/invenio
	$(INSTALL) -m 664 $(XSLT) $(ETCDIR)/bibconvert/config

clean:
	@rm -f *.orig *~

# end of file
