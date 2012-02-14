# $Id$

include ../config.mk
-include ../config-local.mk

IMGFILES = *.png invenio_inspire.css
JSFILES = *.js
LIBFILES = web*_templates_inspire.py

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(IMGFILES) $(WEBDIR)/img
	$(INSTALL) -m 664 $(JSFILES) $(WEBDIR)/js
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)/python/invenio

install-ugly: install uglify

uglify:
	@cat invenio_inspire_ugly.css >>$(WEBDIR)/img/invenio_inspire.css
	@mv $(WEBDIR)/img/inspire_logo_hep_ugly.png $(WEBDIR)/img/inspire_logo_hep.png

clean:
	@rm -f *.orig *~

# end of file
