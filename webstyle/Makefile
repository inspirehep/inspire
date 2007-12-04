# $Id$

include ../config.mk

IMGFILES = inspire_logo.gif
LIBFILES = webstyle_templates_inspire.py

all:
	@echo "Done."

test:
	@echo "Done."

install:
	$(INSTALL) -m 664 $(IMGFILES) $(WEBDIR)/img
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)/python/invenio
	# force 'inspire' skin in case it was not set up in config.wml:
	perl -pi -e 's,CFG_WEBSTYLE_TEMPLATE_SKIN = "default",CFG_WEBSTYLE_TEMPLATE_SKIN = "inspire",g' $(LIBDIR)/python/invenio/config.py

# end of file
