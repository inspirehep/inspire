# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
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
"""BibFormat element - Prints address for Institution.
"""

def format_element(bfo, separator=""):
    """Print Address marc fields for an Inst record"""
    out = []
    fulladdress = bfo.fields("371__", repeatable_subfields_p=True)

    for printaddress in fulladdress:
        if printaddress.has_key('x'):
            ## only print all a's and d
            ## loop over a fields
            if printaddress.has_key('a') and printaddress.has_key('d'):
                out.append(separator.join(printaddress['a']))
                out.append(", ")
                out.append(separator.join(printaddress['d']))
                out.append("<br>")

    if len(out):
        return """<a href="#" onclick="toggle2('content', this)">Show secondary addresses</a>
<div id="content" style="display:none; padding-left:10px;">
<i>%(content)s</i>
</div>
<br>
<script type="text/javascript">
function toggle2(id, link) {
var e = document.getElementById(id);
if (e.style.display == '') {
e.style.display = 'none';
link.innerHTML = 'Show secondary addresses';
}
else
{
e.style.display = '';
link.innerHTML = 'Hide secondary addresses';
}
}
</script>
        """ % {'content': "".join(out)}
    else:
        return ""

def escape_values(bfo):
    return 0
