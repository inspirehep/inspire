include ../config.mk
-include ../config-local.mk

SCRIPTBINFILES = rt
SCRIPTBINDIR = $(BINDIR)
SUBDIRS = ticket_templates
# main targets:

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done."
clean:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make clean && cd .. ;)
	@echo "Done."

install:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	$(INSTALL) $(SCRIPTBINFILES) $(SCRIPTBINDIR)

# end of file
