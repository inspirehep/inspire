# $Id$

include ../config.mk
-include ../config-local.mk

SUBDIRS = img
CSSFILES = invenio_inspire.css jobsubmit.css
JSFILES = *.js
LIBFILES = *.py
ROBOTSFILES = robots.txt
CKEDITORFILES = websubmit-ckeditor-config.js

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Nothing to test."

install:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	$(INSTALL) -m 664 $(CSSFILES) $(WEBDIR)/img
	$(INSTALL) -m 664 $(JSFILES) $(WEBDIR)/js
	$(INSTALL) -m 664 $(ROBOTSFILES) $(WEBDIR)
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)/python/invenio
	$(INSTALL) -m 664 $(CKEDITORFILES) $(WEBDIR)/ckeditor

install-ugly: install uglify

install-test: install uglify-test

uglify:
	@cat invenio_inspire_ugly.css >>$(WEBDIR)/img/invenio_inspire.css
	@mv $(WEBDIR)/img/inspire_logo_hep_ugly.png $(WEBDIR)/img/inspire_logo_hep.png

uglify-test:
	@mv $(WEBDIR)/img/inspire_logo_hep_ugly_test.png $(WEBDIR)/img/inspire_logo_hep.png

clean:
	@rm -f *.orig *~

# end of file
