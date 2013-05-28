include ../config.mk
-include ../config-local.mk
TASKLETS = bst_*.py

# main targets:

all:
	@echo "Done."

clean:
	@echo "No clean."

install:
	$(INSTALL) -m 664 $(TASKLETS) $(LIBDIR)/python/invenio/bibsched_tasklets


