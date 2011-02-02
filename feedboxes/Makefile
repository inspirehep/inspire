include ../config.mk
-include ../config-local.mk

SCRIPTS = inspire_update_feedboxes.py

all:
	@echo "Done."

test:
	$(PYTHON) test_for_feedparser.py
	@echo "Done."

install: test
	$(INSTALL) -m 755 $(SCRIPTS) $(BINDIR)

clean:
	@rm -f *.orig *~

# end of file
