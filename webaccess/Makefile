# $Id$

include ../config.mk
-include ../config-local.mk

LIBFILES = searchuser.py
LIBDIR = $(WEBDIR)/admin/webaccess

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(LIBDIR) $(LIBFILES)

clean:
	@rm -f *.orig *~
