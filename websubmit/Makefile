include ../config.mk
-include ../config-local.mk

WEBSUBMITFILES = JOBSUBMIT_Mail_Submitter.py JOBSUBMIT_Send_APP_Mail.py JOBSUBMIT_Print_Success.py JOBSUBMIT_Send_Approval_Request.py
WEBSUBMITTPLFILES = JOBSUBMITmodify.tpl JOBSUBMIT.tpl JOBSUBMITcreate.tpl
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

