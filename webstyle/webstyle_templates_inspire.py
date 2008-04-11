## $Id$

## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

__revision__ = \
    "$Id$"

import cgi
from invenio.config import CFG_SITE_LANG, CFG_SITE_NAME, CFG_SITE_NAME_INTL, CFG_SITE_URL, CFG_SITE_SECURE_URL, CFG_SITE_SUPPORT_EMAIL
from invenio.messages import gettext_set_language
from invenio.webstyle_templates import Template as DefaultTemplate

class Template(DefaultTemplate):
    """INSPIRE style templates."""

    def tmpl_pageheader(self, req, ln=CFG_SITE_LANG, headertitle="",
                        description="", keywords="", userinfobox="",
                        navtrailbox="", pageheaderadd="", uid=0,
                        secure_page_p=0, navmenuid="admin", metaheaderadd="",rssurl=CFG_SITE_URL+"/rss"):

        """Creates a page header

           Parameters:


          - 'ln' *string* - The language to display

          - 'headertitle' *string* - the second part of the page HTML title

          - 'description' *string* - description goes to the metadata in the header of the HTML page

          - 'keywords' *string* - keywords goes to the metadata in the header of the HTML page

          - 'userinfobox' *string* - the HTML code for the user information box

          - 'navtrailbox' *string* - the HTML code for the navigation trail box

          - 'pageheaderadd' *string* - additional page header HTML code

          - 'uid' *int* - user ID

          - 'secure_page_p' *int* (0 or 1) - are we to use HTTPS friendly page elements or not?

          - 'navmenuid' *string* - the id of the navigation item to highlight for this page

          - 'metaheaderadd' *string* - list of further tags to add to the <HEAD></HEAD> part of the page

          - 'rssurl' *string* - the url of the RSS feed for this page

           Output:

          - HTML code of the page headers
        """

        # load the right message language
        _ = gettext_set_language(ln)

        if headertitle == CFG_SITE_NAME_INTL.get(ln, CFG_SITE_NAME):
            headertitle = _("Home")

        out = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
 <title>%(sitename)s: %(headertitle)s</title>
 <link rev="made" href="mailto:%(sitesupportemail)s" />

 <link rel="stylesheet" href="%(cssurl)s/img/cds.css" type="text/css" />
 <link rel="stylesheet" href="%(cssurl)s/img/inspire.css" type="text/css" />

 <link rel="alternate" type="application/rss+xml" title="%(sitename)s RSS" href="%(siteurl)s/rss" />
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
 <meta name="description" content="%(description)s" />
 <meta name="keywords" content="%(keywords)s" />
 %(metaheaderadd)s
</head>
<body>
<span class="warning"><small>Welcome to an <a class="nearestterms" href="https://twiki.cern.ch/twiki/bin/view/Inspire/WebHome">Inspire</a> test server.
Please go to <a class="nearestterms" href="http://www.slac.stanford.edu/spires/">SPIRES</a> if you are here by mistake.</small></span>
<div style="color: #039; font-size: x-small; width: 150px; margin-bottom: 5px; float: right; margin-top: 25px;">%(userinfobox)s</div>
<div><a href="%(siteurl)s"><img border="0" src="%(cssurl)s/img/inspire_logo.gif" alt="INSPIRE" /></a></div>
<div class="navbar">
<a id="nav-hep" href="%(siteurl)s">Hep</a>
::
<a id="nav-inst" href="%(siteurl)s/collection/Institutions">Institutions</a>
::
<a id="nav-exp" href="%(sitesecureurl)s/youraccount/display?ln=%(ln)s">%(msg_personalize)s</a>
::
<a id="nav-jobs" href="%(siteurl)s/help/%(langlink)s">%(msg_help)s</a>
</div>
<table class="navtrailbox">
 <tr>
  <td class="navtrailboxbody">
   %(navtrailbox)s
  </td>
 </tr>
</table>
<!-- end replaced page header -->
%(pageheaderadd)s
</div>
        """ % {
          'siteurl' : CFG_SITE_URL,
          'sitesecureurl' : CFG_SITE_SECURE_URL,
          'cssurl' : secure_page_p and CFG_SITE_SECURE_URL or CFG_SITE_URL,
          'ln' : ln,
          'langlink': ln != CFG_SITE_LANG and '?ln=' + ln or '',

          'sitename' : CFG_SITE_NAME_INTL.get(ln, CFG_SITE_NAME),
          'headertitle' : cgi.escape(headertitle),

          'sitesupportemail' : CFG_SITE_SUPPORT_EMAIL,

          'description' : cgi.escape(description),
          'keywords' : cgi.escape(keywords),
          'metaheaderadd' : metaheaderadd,

          'userinfobox' : userinfobox,
          'navtrailbox' : navtrailbox,

          'pageheaderadd' : pageheaderadd,

          'search_selected': navmenuid == 'search' and "selected" or "",
          'submit_selected': navmenuid == 'submit' and "selected" or "",
          'personalize_selected': navmenuid.startswith('your') and "selected" or "",
          'help_selected': navmenuid == 'help' and "selected" or "",

          'msg_search' : _("Search"),
          'msg_submit' : _("Submit"),
          'msg_personalize' : _("Personalize"),
          'msg_help' : _("Help"),
          'languagebox' : self.tmpl_language_selection_box(req, ln),

        }
        return out
