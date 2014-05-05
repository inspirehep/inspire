# Override these settings for the Makefiles in a separate file named:
#     config-local.mk
# in your top level directory
#

PREFIX = $(VIRTUAL_ENV)

ifeq "$(PREFIX)" ""
    PREFIX = $(CFG_INVENIO_PREFIX)
endif

ifeq "$(PREFIX)" ""
    PREFIX = /opt/invenio
endif

BINDIR = $(PREFIX)/bin
ETCDIR = $(PREFIX)/etc
TMPDIR = $(PREFIX)/tmp
LIBDIR = $(PREFIX)/lib
WEBDIR = $(PREFIX)/var/www

INSTALL = install -g `whoami` -m 775

PYTHON = /usr/bin/env python

# bibconvert options
#

CONVERT = $(BINDIR)/bibconvert -c
# where, locally, do the converted data files live
FULLSETDIR = full_spires_records/
# where to fetch the spires records
SPIRESDIR = ftp://ftp.slac.stanford.edu/groups/library/spires/inspire/test/
