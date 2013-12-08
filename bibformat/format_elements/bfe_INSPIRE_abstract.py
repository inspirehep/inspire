# -*- coding: utf-8 -*-
##
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
"""BibFormat element - Prints English abstract.
"""


def format_element(bfo, prefix_en, suffix_en, escape="3", separator_en="<br/>"):
    """ Prints the abstract of a record in HTML in English.

    @param prefix_en: a prefix for english abstract (printed only if english abstract exists)
    @param suffix_en: a suffix for english abstract(printed only if english abstract exists)
    @param escape: escaping method (overrides default escape parameter to not escape separators)
    @param separator_en: a separator between each english abstract
    """
    out = ''
    # arXiv abstract should be last, so let's store it in a special variable
    arxiv = ''

    toggle_script = """
<script type="text/javascript">
function toggle_abstract(event, element) {
    $(element).next().next().toggle();
    event.preventDefault();
};
</script>
"""

    def create_abstract_element(field, hide=False):
        if field.get('a'):
            element = ""
            source = field.get('9')
            if hide:
                element += '<a href="#" onclick="toggle_abstract(event, this)">' + prefix_en
                if source:
                    element += '(' + source + ')'
                element += '</a>'
                element += "<br/>"
                element += "<span style='display: none;'>" + field.get('a')
                element += separator_en + '</span>'
            else:
                element += prefix_en
                if source:
                    element += '(' + source + ')'
                element += '</a>'
                element += "<br/>"
                element += "<span>" + field.get('a')
                element += separator_en + '</span>'

            return element

    try:
        escape_mode_int = int(escape)
    except ValueError:
        escape_mode_int = 0

    abstract_list = bfo.fields('520__', escape=escape_mode_int)

    other_abstract = []
    for abstract in abstract_list:
        if abstract.get('9', "").lower() == 'arxiv':
            # there should be only one arXiv abstract, so we can overwrite the arxiv variable
            arxiv = abstract
        else:
            other_abstract.append(abstract)

    if other_abstract:
        out = create_abstract_element(other_abstract[0], hide=False)
        for abstract in other_abstract[1:]:
            out += create_abstract_element(abstract, hide=True)
        if arxiv:
            out += create_abstract_element(arxiv, hide=True)
    else:
        if arxiv:
            out = create_abstract_element(arxiv, hide=False)

    if out:
        out += suffix_en
        out += toggle_script

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
