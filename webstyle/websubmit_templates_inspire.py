## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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

import cgi

from invenio.config import CFG_SITE_URL
from invenio.messages import gettext_set_language
from invenio.websubmit_templates import Template as DefaultTemplate


class Template(DefaultTemplate):

    def tmpl_page_interface(self, ln, docname, actname, curpage, nbpages, nextPg, access, nbPg, doctype, act, fields, javascript, mainmenu):
        """
        Produces a page with the specified fields (in the submit chain)

        Parameters:

          - 'ln' *string* - The language to display the interface in

          - 'doctype' *string* - The document type

          - 'docname' *string* - The document type name

          - 'actname' *string* - The action name

          - 'act' *string* - The action

          - 'curpage' *int* - The current page of submitting engine

          - 'nbpages' *int* - The total number of pages

          - 'nextPg' *int* - The next page

          - 'access' *string* - The submission number

          - 'nbPg' *string* - ??

          - 'fields' *array* - the fields to display in the page, with each record having the structure:

              - 'fullDesc' *string* - the description of the field

              - 'text' *string* - the HTML code of the field

              - 'javascript' *string* - if the field has some associated javascript code

              - 'type' *string* - the type of field (T, F, I, H, D, S, R)

              - 'name' *string* - the name of the field

              - 'rows' *string* - the number of rows for textareas

              - 'cols' *string* - the number of columns for textareas

              - 'val' *string* - the default value of the field

              - 'size' *string* - the size for text fields

              - 'maxlength' *string* - the maximum length for text fields

              - 'htmlcode' *string* - the complete HTML code for user-defined fields

              - 'typename' *string* - the long name of the type

          - 'javascript' *string* - the javascript code to insert in the page

          - 'mainmenu' *string* - the url of the main menu

        """

        # load the right message language
        _ = gettext_set_language(ln)

        # top menu
        out = """
              <form method="post" action="/submit" enctype="multipart/form-data" onsubmit="return tester();" accept-charset="UTF-8">
              <center><table cellspacing="0" cellpadding="0" border="0">
              <tr><td colspan="5" class="submitHeader">
                    <table border="0" cellspacing="0" cellpadding="15" width="100%%" class="submitBody"><tr><td>
                     <input type="hidden" name="nextPg" value="%(nextPg)s" />
                     <input type="hidden" name="access" value="%(access)s" />
                     <input type="hidden" name="curpage" value="%(curpage)s" />
                     <input type="hidden" name="nbPg" value="%(nbPg)s" />
                     <input type="hidden" name="doctype" value="%(doctype)s" />
                     <input type="hidden" name="act" value="%(act)s" />
                     <input type="hidden" name="mode" value="U" />
                     <input type="hidden" name="step" value="0" />
                     <input type="hidden" name="ln" value="%(ln)s" />
                """ % {
            'doctype': cgi.escape(doctype),
            'act': cgi.escape(act),
            'access': cgi.escape(access),
            'nextPg': cgi.escape(nextPg),
            'curpage': cgi.escape(curpage),
            'nbPg': cgi.escape(nbPg),
            'ln': cgi.escape(ln),
            }

        for field in fields:
            if field['javascript']:
                out += """<script language="JavaScript1.1"  type="text/javascript">
                          %s
                          </script>
                       """ % field['javascript']

            # now displays the html form field(s)
            out += "%s\n%s\n" % (field['fullDesc'], field['text'])

        out += javascript
        out += "<br />&nbsp;<br />&nbsp;</td></tr></table></td></tr>\n"

        # Display the navigation cell
        # Display "previous page" navigation arrows
        out += """<tr><td colspan="5"><table border="0" cellpadding="0" cellspacing="0" width="100%%"><tr>"""
        if int(curpage) != 1:
            out += """ <td class="submitHeader" align="left">&nbsp;
                         <a href='' onclick="if (tester2() == 1) {document.forms[0].curpage.value=%(prpage)s;user_must_confirm_before_leaving_page = false;document.forms[0].submit();return false;} else { return false; }">
                           <img src="%(images)s/left-trans.gif" alt="%(prevpage)s" border="0" />
                             <strong><font color="white">%(prevpage)s</font></strong>
                         </a>
                       </td>
            """ % {
                'prpage': int(curpage) - 1,
                'images': CFG_SITE_URL + '/img',
                'prevpage': _("Previous page"),
            }
        else:
            out += """ <td class="submitHeader">&nbsp;</td>"""
        # Display the submission number
        out += """ <td class="submitHeader" align="center"><small>%(submission)s: %(access)s</small></td>\n""" % {
            'submission': _("Submission number") + '(1)',
            'access': cgi.escape(access),
              }
        # Display the "next page" navigation arrow
        if int(curpage) != int(nbpages):
            out += """ <td class="submitHeader" align="right">
                         <a href='' onclick="if (tester2()){document.forms[0].curpage.value=%(nxpage)s;user_must_confirm_before_leaving_page = false;document.forms[0].submit();return false;} else {return false;}; return false;">
                          <strong><font color="white">%(nextpage)s</font></strong>
                          <img src="%(images)s/right-trans.gif" alt="%(nextpage)s" border="0" />
                        </a>
                       </td>
            """ % {
                'nxpage': int(curpage) + 1,
                'images': CFG_SITE_URL + '/img',
                'nextpage': _("Next page"),
            }
        else:
            out += """ <td class="submitHeader">&nbsp;</td>"""
        out += """</tr></table></td></tr></table></center></form>
                  <br />
                  <br />
                  <hr />
                  <small>%(take_note)s</small><br />
                  <small>%(explain_summary)s</small><br />
               """ % {
               'take_note': '(1) ' + _("This is your submission access number. It can be used to continue with an interrupted submission in case of problems."),
               'explain_summary': ""
               }
        return out

    def tmpl_page_endaction(self, ln, nextPg, startPg, access, curpage, nbPg, nbpages, doctype, act, docname, actname, mainmenu, finished, function_content, next_action):
        """
        Produces the pages after all the fields have been submitted.

        Parameters:

          - 'ln' *string* - The language to display the interface in

          - 'doctype' *string* - The document type

          - 'act' *string* - The action

          - 'docname' *string* - The document type name

          - 'actname' *string* - The action name

          - 'curpage' *int* - The current page of submitting engine

          - 'startPg' *int* - The start page

          - 'nextPg' *int* - The next page

          - 'access' *string* - The submission number

          - 'nbPg' *string* - total number of pages

          - 'nbpages' *string* - number of pages (?)


          - 'mainmenu' *string* - the url of the main menu

          - 'finished' *bool* - if the submission is finished

          - 'function_content' *string* - HTML code produced by some function executed

          - 'next_action' *string* - if there is another action to be completed, the HTML code for linking to it
        """

        # load the right message language
        _ = gettext_set_language(ln)

        out = """
          <form ENCTYPE="multipart/form-data" action="/submit" onsubmit="user_must_confirm_before_leaving_page=false;" method="post" accept-charset="UTF-8">
          <input type="hidden" name="nextPg" value="%(nextPg)s" />
          <input type="hidden" name="startPg" value="%(startPg)s" />
          <input type="hidden" name="access" value="%(access)s" />
          <input type="hidden" name="curpage" value="%(curpage)s" />
          <input type="hidden" name="nbPg" value="%(nbPg)s" />
          <input type="hidden" name="doctype" value="%(doctype)s" />
          <input type="hidden" name="act" value="%(act)s" />
          <input type="hidden" name="fromdir" value="" />
          <input type="hidden" name="mainmenu" value="%(mainmenu)s" />

          <input type="hidden" name="mode" value="U" />
          <input type="hidden" name="step" value="1" />
          <input type="hidden" name="deleted" value="no" />
          <input type="hidden" name="file_path" value="" />
          <input type="hidden" name="userfile_name" value="" />

          <input type="hidden" name="ln" value="%(ln)s" />
          <center><table cellspacing="0" cellpadding="0" border="0"><tr>
             <td class="submitHeader"><b>%(docname)s&nbsp;</b></td>
             <td class="submitHeader"><small>&nbsp;%(actname)s&nbsp;</small></td>
             <td valign="bottom">
                 <table cellspacing="0" cellpadding="0" border="0" width="100%%">
                 <tr><td class="submitEmptyPage">&nbsp;&nbsp;</td>
              """ % {
              'nextPg': cgi.escape(nextPg),
              'startPg': cgi.escape(startPg),
              'access': cgi.escape(access),
              'curpage': cgi.escape(curpage),
              'nbPg': cgi.escape(nbPg),
              'doctype': cgi.escape(doctype),
              'act': cgi.escape(act),
              'docname': docname,
              'actname': actname,
              'mainmenu': cgi.escape(mainmenu),
              'ln': cgi.escape(ln),
              }

        if finished == 1:
            out += """<td class="submitCurrentPage">%(finished)s</td>
                      <td class="submitEmptyPage">&nbsp;&nbsp;</td>
                     </tr></table>
                    </td>
                    <td class="submitEmptyPage" align="right">&nbsp;</td>
                   """ % {
                'finished': _("finished!"),
                   }
        else:
            for i in range(1, nbpages + 1):
                out += """<td class="submitPage"><small>&nbsp;
                            <a href='' onclick="document.forms[0].curpage.value=%s;document.forms[0].action='/submit';document.forms[0].step.value=0;user_must_confirm_before_leaving_page = false;document.forms[0].submit();return false;">%s</a>&nbsp;</small></td>""" % (i, i)
            out += """<td class="submitCurrentPage">%(end_action)s</td><td class="submitEmptyPage">&nbsp;&nbsp;</td></tr></table></td>
                      <td class="submitHeader" align="right">&nbsp;<a href='' onclick="window.open('/submit/summary?doctype=%(doctype)s&amp;act=%(act)s&amp;access=%(access)s&amp;ln=%(ln)s','summary','scrollbars=yes,menubar=no,width=500,height=250');return false;"><font color="white"><small>%(summary)s(2)</small></font></a>&nbsp;</td>""" % {
                        'end_action' : _("end of action"),
                        'summary' : _("SUMMARY"),
                        'doctype' : cgi.escape(doctype),
                        'act' : cgi.escape(act),
                        'access' : cgi.escape(access),
                        'ln' : cgi.escape(ln),
                      }
        out += """</tr>
                  <tr>
                    <td colspan="5" class="submitBody">
                      <small><br /><br />
                      %(function_content)s
                      %(next_action)s
                      <br /><br />
                    </td>
                </tr>
                <tr class="submitHeader">
                    <td class="submitHeader" colspan="5" align="center">""" % {
                       'function_content' : function_content,
                       'next_action' : next_action,
                     }
        if finished == 0:
            out += """<small>%(submission)s</small>&sup2;:
                      <small>%(access)s</small>""" % {
                        'submission' : _("Submission no"),
                        'access' : cgi.escape(access),
                      }
        else:
            out += "&nbsp;\n"
        out += """
            </td>
        </tr>
        </table>
        </center>
        </form>
        <br />
        <br />"""

        return out
