# $Id$

include ../config.mk

XSLFILES = conf2marc.xsl
SPIRESXML = ftp://ftp.slac.stanford.edu/groups/library/spires/conf.xml.gz

all:
	@echo "Done."
test:
	$(BINDIR)/bibconvert -c $(XSLFILES) < test_conf.xml > test_conf.marcxml
	xmllint --format test_conf.marcxml

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

# targets working with big SPIRES dump files follow:




get:
	@echo "* Downloading large file from SLAC FTP server, please be patient..."
	wget $(SPIRESXML)
	rm -f ./conf.xml
	gunzip ./conf.xml.gz
	@echo "* Done.  Please run 'make utf8' now."


utf8:
	@echo "* Changing non-standard characters to UTF8 .."
	mv conf.xml confn.xml
	iconv -fLatin1 -tUTF8 confn.xml > conf.xml
	rm -f confn.xml


	perl -i.bk -pe 's/[^[:ascii:]]//g;' conf.xml
	cat conf.xml | tr -d "\000-\011" | tr -d "\013-\014"| tr -d "\016-\037" > conf.x
	mv  conf.x conf.xml
	@echo "Please see clean-spires-data.sh if your input contains broken tags"


	@echo "* Done.  Please run 'make convert' now."

convert:
	@echo "* Converting  files, please be patient..."
	$(BINDIR)/bibconvert -c $(XSLFILES) < conf.xml > conf.marcxml 
	@echo "* Done.  Please run 'make test-with-xmllint' or 'make test-with-xmlmarclint' now."

test-with-xmllint:
	@echo "* Testing XML correctness of converted files, please be patient..."
	xmllint --noout conf.marcxml
	@echo "* Done.  Please run 'make upload' now."

test-with-xmlmarclint:
	@echo "* Testing MARCXML correctness of converted files, please be patient..."
	$(BINDIR)/xmlmarclint conf.marcxml
	@echo "* Done.  Please run 'make upload' now."

upload:
	@echo "* Uploading converted files..."
	$(BINDIR)/bibupload -ir conf.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

supload:
	@echo "* Uploading converted files..."
	sudo -u $(BIBSCHED_PROCESS_USER) $(BINDIR)/bibupload -ir conf.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

load-all-records: get utf8 convert test-with-xmllint supload

# end of file
