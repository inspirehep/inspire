# $Id$

include ../config.mk
-include ../config-local.mk

DOCFILES = *.webdoc
DOCDIR = $(LIBDIR)/webdoc/invenio/help/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(DOCFILES) $(DOCDIR)

clean:
	@rm -f *.orig *~

# end of file
