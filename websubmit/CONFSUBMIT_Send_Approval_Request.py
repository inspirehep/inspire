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
from invenio.websubmit_functions.CONFSUBMIT_Mail_Submitter import CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL, CFG_WEBSUBMIT_CONF_FROMADDR, email_footer

def CONFSUBMIT_Send_Approval_Request (parameters, curdir, form, user_info=None):
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

       * submitteremailfile: name of the file in which the title is stored.

       * submitternamefile: name of the file in which the title is stored.

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

       * seriesnamefile: name of the file where the series name is stored.

       * seriesnumberfile: name of the file where the series number is stored.

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
    submitteremail = get_file_contents(curdir, parameters['submitteremailfile']).replace("\n",", ")
    submittername = get_file_contents(curdir, parameters['submitternamefile']).replace("\n",", ")
    contactname = get_file_contents(curdir, parameters['contactnamefile']).replace("\n",", ")
    contactemail = get_file_contents(curdir, parameters['contactemailfile']).replace("\n",", ")
    subtitle = get_file_contents(curdir, parameters['subtitle']).replace("\n",", ")
    city = get_file_contents(curdir, parameters['cityfile']).replace("\n",", ")
    country = get_file_contents(curdir, parameters['countryfile']).replace("\n",", ")
    state = get_file_contents(curdir, parameters['statefile']).replace("\n",", ")
    stdate = get_file_contents(curdir, parameters['stdatefile']).replace("\n",", ")
    fndate = get_file_contents(curdir, parameters['fndatefile']).replace("\n",", ")
    field = get_file_contents(curdir, parameters['fieldfile']).replace("\n",", ")
    url = get_file_contents(curdir, parameters['urlfile']).replace("\n"," ")
    shorttitle = get_file_contents(curdir, parameters['shorttitle']).replace("\n"," ")
    keywords = get_file_contents(curdir, parameters['keywords']).replace("\n"," ")
    proceedings = get_file_contents(curdir, parameters['proceedings']).replace("\n"," ")
    seriesname = get_file_contents(curdir, parameters['seriesnamefile']).replace("\n"," ")
    seriesnumber = get_file_contents(curdir, parameters['seriesnumberfile']).replace("\n"," ")
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
The document %(rn)s has been submitted to the Conferences database and it will appear here:\n%(recordlink)s.
To approve/reject the document, you should go to this URL:\n%(access)s\n

Title: %(title)s
Date: from %(stdate)s to %(fndate)s
Place: %(city)s, %(state)s, %(country)s
Series name: %(seriesname)s
Series number: %(seriesnumber)s

URL: %(url)s

Field(s): %(field)s

Description:
%(abstract)s

Contact name(s): %(contactname)s
Contact email(s): %(contactemail)s
Submitter name(s): %(submittername)s
Submitter email(s): %(submitteremail)s
    """ % {'rn' : rn,
           'title' : title,
           'submitteremail' : submitteremail,
           'submittername' : submittername,
           'contactname' : contactname,
           'contactemail' : contactemail,
           'field' : field,
           'city' : city,
           'state' : state,
           'country' : country,
           'stdate' : stdate,
           'fndate' : fndate,
           'url' : url,
           'subtitle' : subtitle,
           'shorttitle' : shorttitle,
           'proceedings' : proceedings,
           'keywords' : keywords,
           'access' : "%s/approve.py?access=%s" % (CFG_SITE_URL,access),
           'recordlink' : record_url,
           'abstract' : abstract,
           'seriesname' : seriesname,
           'seriesnumber' : seriesnumber
           }
    #Send mail to referee
    send_email(fromaddr=CFG_WEBSUBMIT_CONF_FROMADDR, toaddr=CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL, subject=title_referee, \
               content=mail_referee, footer=email_footer(support_email=CFG_WEBSUBMIT_CONF_SUPPORT_EMAIL),
               copy_to_admin=CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN, bccaddr=addresses, replytoaddr=contactemail)
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

