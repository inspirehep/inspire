## This file is part of Invenio.
## Copyright (C) 2004, 2005, 2006, 2007, 2008, 2010, 2011, 2012 CERN.
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

import os
import re

from invenio.config import CFG_SITE_NAME, \
     CFG_SITE_URL, \
     CFG_SITE_SUPPORT_EMAIL, \
     CFG_SITE_RECORD, \
     CFG_SITE_LANG, \
     CFG_SITE_NAME_INTL

from invenio.websubmit_config import CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN
from invenio.mailutils import send_email
from invenio.messages import wash_language, gettext_set_language

def Mail_Submitter(parameters, curdir, subject, text, support_email="", from_address=""):
    """
    This function send an email to the submitter to warn him the
    document he has just submitted has been correctly received.

    Parameters:

      * authorfile: Name of the file containing the authors of the
                    document

      * titleFile: Name of the file containing the title of the
                   document

      * emailFile: Name of the file containing the email of the
                   submitter of the document

      * status: Depending on the value of this parameter, the function
                adds an additional text to the email.  This parameter
                can be one of: ADDED: The file has been integrated in
                the database.  APPROVAL: The file has been sent for
                approval to a referee.  or can stay empty.

      * edsrn: Name of the file containing the reference of the
               document

      * newrnin: Name of the file containing the 2nd reference of the
                 document (if any)
    """
    # The submitters email address is read from the file specified by 'emailFile'
    try:
        fp = open("%s/%s" % (curdir,parameters['emailFile']),"r")
        m_recipient = fp.read().replace ("\n"," ")
        fp.close()
    except:
        m_recipient = ""
    # send the mail
    send_email(fromaddr=from_address, toaddr=m_recipient.strip(), subject=subject, \
               content=text, footer=email_footer(support_email=support_email), copy_to_admin=CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN)
    return ""

def email_footer(ln=CFG_SITE_LANG, support_email=""):
    """The footer of the email
    @param ln: language
    @param support_email: email address of the support
    @return: footer as a string"""
    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    #standard footer
    out = """\n\n%(best_regards)s
--
%(sitename)s <%(siteurl)s>
%(need_intervention_please_contact)s <%(sitesupportemail)s>
        """ % {
            'sitename': CFG_SITE_NAME_INTL[ln],
            'best_regards': _("Best regards"),
            'siteurl': CFG_SITE_URL,
            'need_intervention_please_contact': _("Need human intervention?  Contact"),
            'sitesupportemail': support_email
            }
    return out

def load_parameters(parameters, curdir):
    """Executes all functions that reads parameters from temporary files
    and returns a list
    """
    ret = []
    ret.append(get_refnum(parameters=parameters, curdir=curdir))
    ret.append(get_title(parameters=parameters, curdir=curdir))
    ret.append(get_author(parameters=parameters, curdir=curdir))

    return ret

def get_refnum(parameters, curdir):
    """Returns the reference number
    """
    # retrieve report number
    edsrn = parameters['edsrn']
    newrnin = parameters['newrnin']
    fp = open("%s/%s" % (curdir,edsrn),"r")
    rn = fp.read()
    fp.close()
    rn = re.sub("[\n\r]+","",rn)
    if newrnin != "" and os.path.exists("%s/%s" % (curdir,newrnin)):
        fp = open("%s/%s" % (curdir,newrnin),"r")
        additional_rn = fp.read()
        fp.close()
        additional_rn = re.sub("[\n\r]+","",additional_rn)
        fullrn = "%s and %s" % (additional_rn,rn)
    else:
        fullrn = rn
    fullrn = fullrn.replace("\n"," ")
    return fullrn

def get_title(parameters, curdir):
    """Returns the title
    """
    # The title is read from the file specified by 'titlefile'
    try:
        fp = open("%s/%s" % (curdir,parameters['titleFile']),"r")
        m_title = fp.read().replace("\n"," ")
        fp.close()
    except:
        m_title = "-"
    return m_title

def get_author(parameters, curdir):
    """Returns the author
    """
    # The name of the author is read from the file specified by 'authorfile'
    try:
        fp = open("%s/%s" % (curdir,parameters['authorfile']),"r")
        m_author = fp.read().replace("\n"," ")
        fp.close()
    except:
        m_author = "-"