# $Id$

include ../config.mk
-include ../config-local.mk

IMGFILES = *.png invenio_inspire.css
LIBFILES = webstyle_templates_inspire.py

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(IMGFILES) $(WEBDIR)/img
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)/python/invenio

clean:
	@rm -f *.orig *~

# end of file
