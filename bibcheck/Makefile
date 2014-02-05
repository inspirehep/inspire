include ../config.mk
-include ../config-local.mk

CFGFILES = *.cfg
CFGDIR = $(ETCDIR)/bibcheck

SUBDIRS = plugins

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)

	$(INSTALL) -m 664 $(CFGFILES) $(CFGDIR)

clean:
	@rm -f *.orig *~
