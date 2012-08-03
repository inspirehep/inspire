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
    fulladdress = bfo.fields("730__", repeatable_subfields_p=True)

    for printaddress in fulladdress:
        if printaddress.has_key('a'):
            out.append(separator.join(printaddress['a']) + "<br />")

    if len(out) >= 1:
        name_variants = """
<a href="#" id="more_names" style="color:green;background:white;">Show name variants</a>
<div id="content" style="display:none; padding-left:10px;">
<i>%(content)s</i>
</div>
<br />
<script type="text/javascript">
$("#more_names").click(function(event){
$("#content").toggle(easing='swing', function(){
var newText = $(this).is(':visible') ? 'Hide name variants' : 'Show name variants';
$("#more_names").text(newText);
})
event.preventDefault();
})
</script>
        """ % {'content': "".join(out)}
    return name_variants

def escape_values(bfo):
    return 0
