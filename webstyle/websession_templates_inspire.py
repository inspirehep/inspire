## This file is part of Invenio.
## Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012 CERN.
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
"""
WebSession templates. Customize the look of search of Inspire
"""

__revision__ = "$Id$"

import cgi

from invenio.config import CFG_SITE_SECURE_URL

from invenio.access_control_config import (CFG_EXTERNAL_AUTH_USING_SSO,
                                           CFG_EXTERNAL_AUTH_LOGOUT_SSO,
                                           CFG_WEB_API_KEY_STATUS,
                                           CFG_OPENID_PROVIDERS,
                                           CFG_OAUTH2_PROVIDERS,
                                           CFG_OAUTH1_PROVIDERS,
                                           CFG_OPENID_AUTHENTICATION,
                                           CFG_OAUTH2_AUTHENTICATION,
                                           CFG_OAUTH1_AUTHENTICATION)

from invenio.urlutils import (make_canonical_urlargd,
                              create_url,
                              create_html_link)
from invenio.htmlutils import (escape_html,
                               nmtoken_from_string)
from invenio.messages import (gettext_set_language,
                              language_list_long)
from invenio.websession_config import CFG_WEBSESSION_GROUP_JOIN_POLICY

from invenio.websession_templates import Template as DefaultTemplate


class Template(DefaultTemplate):
    """INSPIRE style templates."""

    def tmpl_login_form(self, ln, referer, internal, register_available,
                        methods, selected_method, msg=None):
        """
        Displays a login form

        Parameters:

          - 'ln' *string* - The language to display the interface in

          - 'referer' *string* - The referer URL - will be redirected upon after login

          - 'internal' *boolean* - If we are producing an internal authentication

          - 'register_available' *boolean* - If users can register freely in the system

          - 'methods' *array* - The available authentication methods

          - 'selected_method' *string* - The default authentication method

          - 'msg' *string* - The message to print before the form, if needed
        """

        # load the right message language
        _ = gettext_set_language(ln)
        register_available = False

        out = "<div style='float:left'>"

        if msg is "":
            out_msg = "If you already have an account, please login using the form below."
            out += "<p>%(please_login)s</p>" % {
                'please_login': cgi.escape(_(out_msg))
            }
        else:
            out += "<p>%s</p>" % msg

        out += """
               <form method="post" action="%(CFG_SITE_SECURE_URL)s/youraccount/login">
               <table>
               """ % {'CFG_SITE_SECURE_URL': CFG_SITE_SECURE_URL}

        if len(methods) - CFG_OPENID_AUTHENTICATION - CFG_OAUTH2_AUTHENTICATION - CFG_OAUTH1_AUTHENTICATION > 1:
            # more than one method, must make a select
            login_select = """<select name="login_method" id="login_method">"""
            for method in methods:
                # OpenID/OAuth shouldn't be shown in this list.
                if not method in ['openid', 'oauth1', 'oauth2']:
                    login_select += """<option value="%(method)s" %(selected)s>%(method)s</option>""" % {
                        'method': cgi.escape(method, True),
                        'selected': (method == selected_method and 'selected="selected"' or "")
                    }
            login_select += "</select>"
            out += """
                   <tr>
                      <td align="right"><strong><label for="login_method">%(login_title)s</label></strong></td>
                      <td>%(login_select)s</td>
                   </tr>""" % {
                     'login_title' : cgi.escape(_("Login method:")),
                     'login_select' : login_select,
                   }
        else:
            # only one login method available
            out += """<input type="hidden" name="login_method" value="%s" />""" % cgi.escape(methods[0], True)

        out += """<tr>
                   <td align="right">
                     <input type="hidden" name="ln" value="%(ln)s" />
                     <input type="hidden" name="referer" value="%(referer)s" />
                     <strong><label for="p_un">%(username)s:</label></strong>
                   </td>
                   <td><input type="text" size="25" name="p_un" id="p_un" value="" /></td>
                  </tr>
                  <tr>
                   <td align="right"><strong><label for="p_pw">%(password)s:</label></strong></td>
                   <td align="left"><input type="password" size="25" name="p_pw" id="p_pw" value="" /></td>
                  </tr>
                  <tr>
                   <td></td>
                   <td align="left"><input type="checkbox" name="remember_me" id="remember_me"/><em><label for="remember_me">%(remember_me)s</label></em></td>
                  <tr>
                   <td></td>
                   <td align="center" colspan="3"><input class="formbutton" type="submit" name="action" value="%(login)s" />""" % {
                       'ln': cgi.escape(ln, True),
                       'referer' : cgi.escape(referer, True),
                       'username' : cgi.escape(_("Username")),
                       'password' : cgi.escape(_("Password")),
                       'remember_me' : cgi.escape(_("Remember login on this computer.")),
                       'login' : cgi.escape(_("login")),
                       }
        if internal:
            out += """&nbsp;&nbsp;&nbsp;(<a href="./lost?ln=%(ln)s">%(lost_pass)s</a>)""" % {
                     'ln' : cgi.escape(ln, True),
                     'lost_pass' : cgi.escape(_("Lost your password?"))
                   }
        out += """</td>
                    </tr>
                  </table></form>"""

        out += """<p><strong>%(note)s:</strong> %(note_text)s</p>""" % {
               'note' : cgi.escape(_("Note")),
               'note_text': cgi.escape(_("You can use your nickname or your email address to login."))}

        out += "</div>"

        if CFG_OPENID_AUTHENTICATION or \
                CFG_OAUTH2_AUTHENTICATION or \
                CFG_OAUTH1_AUTHENTICATION:
            # If OpenID or OAuth authentication is enabled, we put the login
            # forms of providers.
            out += self.tmpl_external_login_panel(ln, referer)

        return out
