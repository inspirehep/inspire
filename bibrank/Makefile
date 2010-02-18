# $Id$

include ../config.mk
-include ../config-local.mk

CFGFILES = citation.cfg wrd.cfg
CFGDIR = $(ETCDIR)/bibrank

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(CFGFILES) $(CFGDIR)

clean:
	@rm -f *.orig *~
