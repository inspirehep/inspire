# -*- coding: utf-8 -*-
##
## $Id$
##
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
"""BibFormat element - Prints authors
"""
__revision__ = "$Id$"

def format(bfo, limit, separator='; ',
           extension='[...]',
           print_links="yes",
           print_affiliations='no',
           affiliation_prefix = ' (',
           affiliation_suffix = ')',
           print_affiliation_first='no',
           interactive="no",
           highlight="no",
           main_authors_only="no",
           main_and_sec_authors_sep="",
           affiliations_separator=" ; ",
           name_last_first="yes"
           ):
    """
    Prints the list of authors of a record.
    
    @param limit the maximum number of authors to display
    @param separator the separator between authors.
    @param extension a text printed if more authors than 'limit' exist
    @param print_links if yes, prints the authors as HTML link to their publications
    @param print_affiliations if yes, make each author name followed by its affiliation
    @param affiliation_prefix prefix printed before each affiliation
    @param affiliation_suffix suffix printed after each affiliation
    @param print_affiliation_first if 'yes', affiliation is printed before the author
    @param interactive if yes, enable user to show/hide authors when there are too many (html + javascript)
    @param highlight highlights authors corresponding to search query if set to 'yes'
    @param main_authors_only If 'yes', only print main authors
    @param main_and_sec_authors_sep a separator printed between main authors (100__) and secondary authors (700__). If value is empty string, then 'separator' is used.
    @param affiliations_separator separates affiliation groups
    @param name_last_first if yes (default) print last, first  otherwise first last
    """
    from urllib import quote
    from cgi import escape
    import re
#FIXME temporary while some inspire sites migrating from .92->.99
    try:
        from invenio.config import CFG_SITE_URL
    except:
        from invenio.config import weburl as CFG_SITE_URL

    # from invenio.config import instlink   ### FIXME

    instlink = '<a class="afflink" href="http://www.slac.stanford.edu/spires/find/inst/www?key='

    from invenio.messages import gettext_set_language

    _ = gettext_set_language(bfo.lang)    # load the right message language

    authors = []
    authors_1 = bfo.fields('100__', repeatable_subfields_p=True)
    if main_authors_only.lower() == 'yes':
        authors_2 = []
    else:
        authors_2 = bfo.fields('700__', repeatable_subfields_p=True)

    if main_and_sec_authors_sep == "":
        main_and_sec_authors_sep = separator
    if len(authors_2) == 0 or len(authors_1) == 0:
        main_and_sec_authors_sep = ''

    coll = bfo.field('980__a')

    # We will merge authors_1 and authors_2 in order to process
    # them with the same piece of code. But we first need
    # to tag them in order to differentiate them
    authors_1 = [(author.setdefault('field','100__') and author) \
                 for author in authors_1]
    authors_2 = [(author.setdefault('field','700__') and author) \
                 for author in authors_2]

    # Merge
    authors.extend(authors_1)
    authors.extend(authors_2)

    # Keep real num of authorsfix + affiliations_separator.join(author['u']) + \
    nb_authors = len(authors)

    # Limit num of authors, so that we do not process
    # the authors that will not be shown. This can only
    # be done in non-interactive mode, as interactive mode
    # allows to show all of them.
    if limit.isdigit() and nb_authors > int(limit) \
           and interactive != "yes":
        if bfo.field('710g'):   #check for colln note
            authors = authors[:1]
        else:               
            authors = authors[:int(limit)]
        

    lastpairs = ()
    # Process authors to add link, affiliation and highlight
    for author in authors:
        
        if author.has_key('a'):
            author['a'] = author['a'][0] # There should not be
                                         # repeatable subfields here.
            if highlight == 'yes':
                from invenio import bibformat_utils
                author['a'] = bibformat_utils.highlight(author['a'],
                                                        bfo.search_pattern)

            #check if we need to reverse last, first
            #we don't try to reverse it if it isn't stored with a comma.
            display_name=author['a']
            if name_last_first.lower()=="no":
                match=re.search('^([^,]+)\s*,\s*(.*)$',author['a'])
                if match:
                    display_name=match.group(2)+' '+match.group(1)


            if print_links.lower() == "yes":

                from invenio.bibformat_elements.bfe_server_info import format as bfe_server
                author['a'] = '<a class="authorlink" href="' + CFG_SITE_URL + \
                              '/search?f=author&amp;p='+ quote(author['a']) + \
                              '&amp;ln='+ bfo.lang + \
                              '">'+escape(display_name)+'</a>'

        if print_affiliations == "yes":
            if author.has_key('e'):
                author['e'] = affiliation_prefix + affiliations_separator.join(author['e']) + \
                              affiliation_suffix

            if author.has_key('i'):
                pairs = zip(author['i'], author['u'])
                author['i'] = [instlink+code+'">'+string.lstrip()+'</a>' for code,string in pairs]
                author['u'] = affiliation_prefix + affiliations_separator.join(author['i']) + \
                              affiliation_suffix
                 

            elif author.has_key('u'):
                author['u'] = affiliation_prefix + affiliations_separator.join(author['u'].lstrip()) + \
                              affiliation_suffix

#
#  Consolidate repeated affiliations 
#

    last = ''
    authors.reverse()
    for author in authors:
        if not author.has_key('u'):
            author['u'] = ''
        #print 'this->'+ author['a']+'\n'
        if last == author['u']:
            author['u']=''
        else:
            last = author['u']

    authors.reverse()
    
    # Flatten author instances
    if print_affiliations == 'yes':
##      100__a (100__e)  700__a (100__e) (100__u)
        if print_affiliation_first.lower() != 'yes':
            authors = [author.get('a', '') + \
                       ((author['field'] == '700__' and author.get('e', '')) or '') +\
                       author.get('u', '') 
                       for author in authors]

        else:
            authors = [author.get('e', '') + author.get('a', '') +\
                       ((author['field'] == '700__' and author.get('u', '')) or '') 
                       for author in authors]

        
    else:
        authors = [author.get('a', '')
                   for author in authors]
        
    if limit.isdigit() and nb_authors > int(limit) and interactive != "yes":
        if int(limit) <= len(authors_1):
            p_sep = ''
        else:
            p_sep = main_and_sec_authors_sep
        return separator.join(authors[:len(authors_1)]) + \
               p_sep + \
               separator.join(authors[len(authors_1):]) + \
               extension

        #return separator.join(authors) + extension

    elif limit.isdigit() and nb_authors > int(limit) and interactive == "yes":
        out = '''
        <script>
        function toggle_authors_visibility(){
            var more = document.getElementById('more');
            var link = document.getElementById('link');
            var extension = document.getElementById('extension');
            if (more.style.display=='none'){
                more.style.display = '';
                extension.style.display = 'none';
                link.innerHTML = "%(show_less)s"
            } else {
                more.style.display = 'none';
                extension.style.display = '';
                link.innerHTML = "%(show_more)s"
            }
            link.style.color = "rgb(204,0,0);"
        }

        function set_up(){
            var extension = document.getElementById('extension');
            extension.innerHTML = "%(extension)s";
            toggle_authors_visibility();
        }
        
        </script>
        '''%{'show_less':_("Hide"),
             'show_more':_("Show all %i authors") % nb_authors,
             'extension':extension}
            
        out += '<a name="show_hide" />'
        if int(limit) > len(authors_1):
            # separator between main and sec authors is before
            # the limit
            out += separator.join(authors[:len(authors_1)]) + \
                   main_and_sec_authors_sep + \
                   separator.join(authors[len(authors_1):int(limit)])
            out += '<span id="more" style="">' + separator + \
                   separator.join(authors[int(limit):]) + '</span>'
        else:
            if int(limit) == len(authors_1):
                p_sep = ''
            else:
                p_sep = separator
            out += separator.join(authors[:int(limit)])
            out += '<span id="more" style="">' + p_sep + \
               separator.join(authors[int(limit):len(authors_1)]) +\
               main_and_sec_authors_sep + \
               separator.join(authors[len(authors_1):]) +'</span>'
        #out += separator.join(authors[:int(limit)])
        #out += '<span id="more" style="">' + separator + \
        #       separator.join(authors[int(limit):]) + '</span>'
        out += ' <span id="extension"></span>'
        out += ' <small><i><a id="link" href="#" onclick="toggle_authors_visibility()" style="color:rgb(204,0,0);"></a></i></small>'
        out += '<script>set_up()</script>'
        return out
    elif nb_authors > 0:
        return separator.join(authors[:len(authors_1)]) + \
               main_and_sec_authors_sep + \
               separator.join(authors[len(authors_1):])
        #return separator.join(authors)
        
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
