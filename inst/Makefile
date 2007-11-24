# $Id$

include ../config.mk

XSLFILES = inst2marc.xsl
SPIRESXML = ftp://ftp.slac.stanford.edu/groups/library/spires/inst.xml.gz

all:
	@echo "Done."
test:
	$(BINDIR)/bibconvert -c $(XSLFILES) < test_inst.xml > test_inst.marcxml
	xmllint --format test_inst.marcxml

install:
	$(INSTALL) -m 664 $(XSLFILES) $(ETCDIR)/bibconvert/config

# targets working with big SPIRES dump files follow:

get:
	@echo "* Downloading large file from SLAC FTP server, please be patient..."
	wget $(SPIRESXML)
	rm ./inst.xml
	gunzip ./inst.xml.gz
	#  Please note, bibconvert and xmllint appear to fail on this large file.  
	#  It may be neccessary to use a different xslt engine or break up the 
	#  file.
	@echo "* Done.  Please run 'make convert' now."


convert:
	@echo "* Converting  files, please be patient..."
	$(BINDIR)/bibconvert -c $(XSLFILES) < inst.xml > inst.marcxml 
	@echo "* Done.  Please run 'make test-with-xmllint' or 'make test-with-xmlmarclint' now."

test-with-xmllint:
	@echo "* Testing XML correctness of converted files, please be patient..."
	xmllint --noout inst.marcxml
	@echo "* Done.  Please run 'make upload' now."

test-with-xmlmarclint:
	@echo "* Testing MARCXML correctness of converted files, please be patient..."
	$(BINDIR)/xmlmarclint inst.marcxml
	@echo "* Done.  Please run 'make upload' now."

upload:
	@echo "* Uploading converted files..."
	$(BINDIR)/bibupload -ir inst.marcxml
	@echo "* Done.  Please see via 'bibsched' the task progress."

# end of file
