include ../config.mk
-include ../config-local.mk

WEBSUBMITFILES = JOBSUBMIT_*.py
WEBSUBMITTPLFILES = JOBSUBMIT*.tpl
WEBSUBMITFNC = $(LIBDIR)/python/invenio/websubmit_functions
# main targets:

all:
	@echo "Done."

clean:
	@echo "Done."

install:
	$(INSTALL) -m 664 $(WEBSUBMITFILES) $(WEBSUBMITFNC)
	$(INSTALL) -m 664 $(WEBSUBMITTPLFILES) $(ETCDIR)/bibconvert/config

# end of file

