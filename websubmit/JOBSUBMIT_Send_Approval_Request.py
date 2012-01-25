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

   ## Description:   function Send_Approval_Request
   ##                This function sends an email to the referee asking him/her
   ##             to approve/reject a document
   ## Author:         T.Baron
   ## PARAMETERS:    directory: parameter to the link manager program
   ##                addressesDAM: address of the referee(s)
   ##             categformatDAM: variable needed to extract the category
   ##                        of the document and use it to derive the
   ##                address.
   ##             authorfile: name of the file containing the author list
   ##             titleFile: name of the file containing the title

import os
import re

from invenio.config import CFG_SITE_NAME, \
     CFG_SITE_URL, \
     CFG_SITE_SUPPORT_EMAIL, \
     CFG_SITE_RECORD
from invenio.dbquery import run_sql
from invenio.access_control_admin import acc_get_role_users,acc_get_role_id
from invenio.websubmit_config import CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN
from invenio.mailutils import send_email
from invenio.websubmit_functions.JOBSUBMIT_Mail_Submitter import CFG_WEBSUBMIT_JOBS_SUPPORT_EMAIL, \
                                                                 CFG_WEBSUBMIT_JOBS_FROMADDR, \
                                                                 job_email_footer

def JOBSUBMIT_Send_Approval_Request (parameters, curdir, form, user_info=None):
    """
    This function sends an email to the referee in order to start the
    simple approval process.  This function is very CERN-specific and
    should be changed in case of external use.  Must be called after
    the Get_Report_Number function.

    Parameters:

       * addressesDAM: email addresses of the people who will receive
                       this email (comma separated list). this
                       parameter may contain the <CATEG> string. In
                       which case the variable computed from the
                       [categformatDAM] parameter replaces this
                       string.
                       eg.:"<CATEG>-email@cern.ch"

       * categformatDAM: contains a regular expression used to compute
                         the category of the document given the
                         reference of the document.

                         eg.: if [categformatAFP]="TEST-<CATEG>-.*"
                         and the reference of the document is
                         "TEST-CATEGORY1-2001-001", then the computed
                         category equals "CATEGORY1"

       * titleFile: name of the file in which the title is stored.

       * contactnamefile: name of the file in which the title is stored.

       * contactemailfile: name of the file in which the title is stored.

       * referencefile: name of the file in which the title is stored.

       * affiliationfile: name of the file in which the title is stored.

       * regionfile: name of the file in which the title is stored.

       * rankfile: name of the file in which the title is stored.

       * fieldfile: name of the file in which the title is stored.

       * experimentsfile: name of the file in which the title is stored.

       * urlfile: name of the file in which the title is stored.

       * datefile: name of the file in which the title is stored.

       * abstractfile: name of the file in which the title is stored.

       * directory: parameter used to create the URL to access the
                    files.
    """
    global rn,sysno
    # variables declaration
    doctype = re.search(".*/([^/]*)/([^/]*)/[^/]*$",curdir).group(2)
    otheraddresses = parameters['addressesDAM']
    categformat = parameters['categformatDAM']
    # retrieve category
    categformat = categformat.replace("<CATEG>","([^-]*)")
    m_categ_search = re.match(categformat, rn)
    if m_categ_search is not None:
        if len(m_categ_search.groups()) > 0:
            ## Found a match for the category of this document. Get it:
            category = m_categ_search.group(1)
        else:
            ## This document has no category.
            category = "unknown"
    else:
        category = "unknown"

    # get record data
    date = get_file_contents(curdir, "date")
    title = get_file_contents(curdir, parameters['titleFile']).replace("\n","")
    title += " - %s" % date
    contactname = get_file_contents(curdir, parameters['contactnamefile']).replace("\n",", ")
    contactemail = get_file_contents(curdir, parameters['contactemailfile']).replace("\n",", ")
    reference = get_file_contents(curdir, parameters['referencefile']).replace("\n",", ")
    affiliation = get_file_contents(curdir, parameters['affiliationfile']).replace("\n",", ")
    region = get_file_contents(curdir, parameters['regionfile']).replace("\n",", ")
    rank = get_file_contents(curdir, parameters['rankfile']).replace("\n",", ")
    field = get_file_contents(curdir, parameters['fieldfile']).replace("\n",", ")
    experiments = get_file_contents(curdir, parameters['experimentsfile']).replace("\n",", ")
    url = get_file_contents(curdir, parameters['urlfile']).replace("\n"," ")
    date = get_file_contents(curdir, parameters['datefile']).replace("\n","")
    abstract = get_file_contents(curdir, parameters['abstractfile'])

    # we get the referee password
    sth = run_sql("SELECT access FROM sbmAPPROVAL WHERE rn=%s", (rn,))
    if len(sth) >0:
        access = sth[0][0]
    # Build referee's email address
    refereeaddress = ""
    # Try to retrieve the referee's email from the referee's database
    for user in acc_get_role_users(acc_get_role_id("referee_%s_%s" % (doctype,category))):
        refereeaddress += user[1] + ","
    # And if there are general referees
    for user in acc_get_role_users(acc_get_role_id("referee_%s_*" % doctype)):
        refereeaddress += user[1] + ","
    refereeaddress = re.sub(",$","",refereeaddress)
    # Creation of the mail for the referee
    addresses = ""
    if refereeaddress != "":
        addresses = refereeaddress + ","
    if otheraddresses != "":
        addresses += otheraddresses
    else:
        addresses = re.sub(",$","",addresses)
    record_url = "%s/%s/%s" % (CFG_SITE_URL, CFG_SITE_RECORD, sysno)
    title_referee = "Request for approval of %s" % rn
    mail_referee = """
The document %(rn)s has been submitted to the Jobs database.\nYour approval is requested on it.

Title: %(title)s
Contact name(s): %(contactname)s
Contact email(s): %(contactemail)s
Reference(s): %(reference)s
Affliliation(s): %(affiliation)s

Region(s): %(region)s
Rank(s): %(rank)s
Field(s): %(field)s
Experiments(s): %(experiments)s

URL: %(url)s

Deadline date: %(date)s

Description:
%(abstract)s

The record will appear here:
%(recordlink)s

To approve/reject the document, you should go to this URL:\n<%(access)s>\n
    """ % {'rn' : rn,
           'title' : title,
           'contactname' : contactname,
           'contactemail' : contactemail,
           'reference' : reference,
           'affiliation' : affiliation,
           'region' : region,
           'rank' : rank,
           'region' : region,
           'field' : field,
           'experiments' : experiments,
           'url' : url,
           'date' : date,
           'abstract' : abstract,
           'access' : "%s/approve.py?access=%s" % (CFG_SITE_URL,access),
           'recordlink' : record_url
           }
    addresses += ",%s" % CFG_WEBSUBMIT_JOBS_SUPPORT_EMAIL
    #Send mail to referee
    send_email(fromaddr=CFG_WEBSUBMIT_JOBS_FROMADDR, toaddr=addresses, subject=title_referee, \
               content=mail_referee, footer=job_email_footer(), copy_to_admin=CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN)
    return ""

def get_file_contents(directory, filename):
    """
    Will return the contents found in given file located
    in given directory, if found.

    @param directory: path to the directory where the file is
    @type directory: str

    @param filename: filename of file to read
    @type filename: str

    @return: contents read from file
    @rtype: str
    """
    full_path = "%s/%s" % (directory,filename)
    content = ""
    if os.path.exists(full_path):
        fp = open(full_path, "r")
        content = fp.read()
        fp.close()
    return content

