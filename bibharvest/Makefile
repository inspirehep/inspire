include ../config.mk
-include ../config-local.mk

FILTERCFGFILES = oaiarXiv_bibfilter_actions.cfg oaicds_bibfilter_config.json
FILTERCFGDIR = $(ETCDIR)/bibharvest/
FILTERBINFILES = bibfilter_oaiarXiv2inspire.py bibfilter_oaicds2inspire.py
FILTERBINDIR = $(BINDIR)
# main targets:

all:
	@echo "Done."

clean:
	@echo "Done."

install:
	mkdir -p $(FILTERCFGDIR)
	$(INSTALL) $(FILTERCFGFILES) $(FILTERCFGDIR)
	$(INSTALL) $(FILTERBINFILES) $(FILTERBINDIR)

# end of file
