from cgi import escape

from invenio.webpage import page
from invenio.access_control_engine import acc_authorize_action
from invenio.dbquery import run_sql
from invenio.webuser import page_not_authorized

def index(req, p=""):
    auth_code, auth_message = acc_authorize_action(req, 'runsearchuser')
    if auth_code != 0:
        return page_not_authorized(req=req, text=auth_message)
    users = []
    if p:
        users = run_sql("SELECT id, nickname, email, last_login FROM user WHERE email<>'' AND nickname LIKE %s OR email LIKE %s ORDER BY email LIMIT 100", ('%%%s%%' % p, '%%%s%%' % p))
    body = """
<form>
<label for="searchuser">Search user:</label> <input name="p" id="searchuser" value="%s" /></input><input type="submit" value="Search" />
</form>
""" % escape(p, True)
    if users:
        body += """<h2>Users found</h2>
<p>This is the list of the first 100 users found matching the criteria.</p>
<table border="1">
  <thead><tr><th>ID</th><th>Nickname</th><th>Email</th><th>Last login</th></tr></thead>
  <tbody>
"""
        for user in users:
            body += """<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" % (user[0], escape(user[1]), escape(user[2]), escape(str(user[3])))
        body += """
  </tbody>
</table>
"""
    return page(req=req, title="Search users", body=body)



