# $Id$

include ../config.mk
-include ../config-local.mk

LIBFILES = *.py
PYDIR = $(LIBDIR)/python/invenio/

SUBDIRS = format_elements format_templates output_formats

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Done.  Please run make install now."

install:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)

	$(INSTALL) -m 664 $(LIBFILES) $(PYDIR)
	@echo "Done.  You may want to restart Apache now."


clean:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make clean && cd .. ;)
	@rm -f *.orig *~
	@echo "Done."

reset-inspire-format-configuration:
	echo "TRUNCATE format" | $(BINDIR)/dbexec
	echo "INSERT INTO \`format\` (\`id\`, \`name\`, \`code\`, \`description\`, \`content_type\`, \`visibility\`) VALUES \
	(1, 'HTML brief', 'hb', 'HTML brief output format, used for search results pages.', 'text/html', 1),\
	(2, 'HTML detailed', 'hd', 'HTML detailed output format, used for Detailed record pages.', 'text/html', 1),\
	(3, 'MARC', 'hm', 'HTML MARC.', 'text/html', 1),\
	(4, 'Dublin Core', 'xd', 'XML Dublin Core.', 'text/xml', 1),\
	(5, 'MARCXML', 'xm', 'XML MARC.', 'text/xml', 1),\
	(6, 'portfolio', 'hp', 'HTML portfolio-style output format for photos.', 'text/html', 0),\
	(7, 'photo captions only', 'hc', 'HTML caption-only output format for photos.', 'text/html', 0),\
	(8, 'BibTeX', 'hx', 'BibTeX.', 'text/html', 1),\
	(9, 'EndNote', 'xe', 'XML EndNote.', 'text/xml', 1),\
	(10, 'NLM', 'xn', 'XML NLM.', 'text/xml', 1),\
	(11, 'Excel', 'excel', 'Excel csv output', 'application/ms-excel', 0),\
	(12, 'HTML similarity', 'hs', 'Very short HTML output for similarity box (<i>people also viewed..</i>).', 'text/html', 0),\
	(13, 'RSS', 'xr', 'RSS.', 'text/xml', 0),\
	(14, 'OAI DC', 'xoaidc', 'OAI DC.', 'text/xml', 0),\
	(15, 'File mini-panel', 'hdfile', 'Used to show fulltext files in mini-panel of detailed record pages.', 'text/html', 0),\
	(16, 'Actions mini-panel', 'hdact', 'Used to display actions in mini-panel of detailed record pages.', 'text/html', 0),\
	(17, 'References tab', 'hdref', 'Display record references in References tab.', 'text/html', 0),\
	(18, 'HTML citesummary', 'hcs', 'HTML cite summary format, used for search results pages.', 'text/html', 1),\
	(19, 'RefWorks', 'xw', 'RefWorks.', 'text/xml', 1),\
	(20, 'MODS', 'xo', 'Metadata Object Description Schema', 'application/xml', 1),\
	(21, 'LaTeX (EU)', 'hlxe', 'LaTeX formatted reference (EU style)', 'text/html', 1),\
	(22, 'LaTeX (US)', 'hlxu', 'LaTeX formatted reference (US Style)',\
	'text/html', 1);" | $(BINDIR)/dbexec


