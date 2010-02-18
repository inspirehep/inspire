# $Id$

include ../../config.mk
-include ../../config-local.mk

BFOFILES = *.bfo
BFODIR = $(ETCDIR)/bibformat/output_formats

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(BFOFILES) $(BFODIR)

clean:
	@rm -f *.orig *~
