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

__revision__ = "$Id$"

import os
from invenio.config import CFG_SITE_URL
from invenio.websubmit_functions.CONFSUBMIT_Mail_Submitter import CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL
# FIXME: cannot import Request_Print(), is defined in websubmit_engine.py

def CONFSUBMIT_Print_Success(parameters, curdir, form, user_info=None):
    """
    This function simply displays a text on the screen, telling the
    user the submission went fine. To be used in the 'Submit New
    Record' action.

    Parameters:

       * status: Depending on the value of this parameter, the
         function adds an additional text to the email. (Not applicable)

       * edsrn: Name of the file containing the reference of the
                document

       * newrnin: Name of the file containing the 2nd reference of the
                  document (if any)
    """
    t=""
    edsrn = parameters['edsrn']
    newrnin = parameters['newrnin']
    status = parameters['status']
    fp = open("%s/%s" % (curdir,edsrn),"r")
    rn = fp.read()
    fp.close()
    if newrnin != "" and os.path.exists("%s/%s" % (curdir,newrnin)):
        fp = open("%s/%s" % (curdir,newrnin),"r")
        additional_rn = fp.read()
        fp.close()
        additional_rn = " and %s" % additional_rn
    else:
        additional_rn = ""
    t=t+Request_Print("A",  "<br /><br /><b>Your Conference submission has been successfully completed!</b><br /><br />")
    t=t+Request_Print("A",  "Your listing has the following reference(s): <b>%s%s</b><br /><br />" % (rn,additional_rn))
    t=t+Request_Print("A",  "The listing will not be visible until it has been fully approved by one of our catalogers. You will be notified by e-mail once the submission has been processed.<br /><br />\n")
    t=t+Request_Print("A",  'If you experience any problems with the submission or have any questions, please contact us at <a href="mailto:%s">%s</a>.' % (CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL, CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL))
    t=t+Request_Print("A",  "Thank you for using the HEP Conference submission!")
    t=t+Request_Print("A",  '<br /><br /><a class="link_active" href="%s/collection/Conferences">Return to the Conference database</a><br /><br />' % (CFG_SITE_URL,))
    return t
