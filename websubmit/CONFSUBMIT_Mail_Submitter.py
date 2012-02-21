## This file is part of Invenio.
## Copyright (C) 2004, 2005, 2006, 2007, 2008, 2010, 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from invenio.config import CFG_SITE_NAME, \
     CFG_SITE_URL, \
     CFG_SITE_SUPPORT_EMAIL, \
     CFG_SITE_RECORD, \
     CFG_SITE_LANG, \
     CFG_SITE_NAME_INTL

from invenio.websubmit_functions.INSPIRE_Mail_Submitter import Mail_Submitter, \
     load_parameters, email_footer
# email_footer function will be passed further

CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL = "conf@inspirehep.net"
CFG_WEBSUBMIT_CONF_FROMADDR = 'INSPIRE-HEP Conference support <%s>' % (CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL,)

def CONFSUBMIT_Mail_Submitter(parameters, curdir, form, user_info=None):
    param_list = load_parameters(parameters=parameters, curdir=curdir)
    fullrn = param_list[0]
    m_title = param_list[1]
    m_author = param_list[2]
    # create email body
    email_txt = "The conference with reference number %s\nTitle: %s\nSubmitter(s): %s\n\nhas been received for approval.\n\n" % (fullrn,m_title,m_author)
    # The user is either informed that the document has been added to the database, or sent for approval
    email_txt += "Your listing will not be visible until it has been fully approved by one of our catalogers. " \
                 "When this happens, you will be notified by email.\n\n" \
                 "If you detect an error, please let us know by sending an email to %s. \n\n" \
                 "Thank you for using the Inspire Conference submission.\n" % (CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL,)
    # send the mail
    Mail_Submitter(parameters=parameters, curdir=curdir, subject="%s: Document Received" % fullrn,\
      text=email_txt, support_email=CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL, from_address=CFG_WEBSUBMIT_CONF_FROMADDR)
    return ""
