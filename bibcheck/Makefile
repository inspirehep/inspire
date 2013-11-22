include ../config.mk
-include ../config-local.mk

CFGFILES = *.cfg
CFGDIR = $(ETCDIR)/bibcheck

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(CFGFILES) $(CFGDIR)

clean:
	@rm -f *.orig *~
