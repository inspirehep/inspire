include ../config.mk
-include ../config-local.mk

WEBSUBMITFILES = *.py
WEBSUBMITTPLFILES = *.tpl

# main targets:
all:
	@echo "Done."

clean:
	@echo "Done."

install:
	$(INSTALL) -m 664 $(WEBSUBMITFILES) $(LIBDIR)/python/invenio/websubmit_functions
	$(INSTALL) -m 664 $(WEBSUBMITTPLFILES) $(ETCDIR)/bibconvert/config

# end of file

