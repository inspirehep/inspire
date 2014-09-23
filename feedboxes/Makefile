include ../config.mk
-include ../config-local.mk

SCRIPTS = inspire_update_feedboxes.py

all:
	@echo "Done."

test:
	@echo "Done."

install: test
	$(INSTALL) -m 755 $(SCRIPTS) $(BINDIR)

clean:
	@rm -f *.orig *~

reset-inspire-portalbox-configuration:
	./inspire_update_feedboxes.py --load


# end of file
