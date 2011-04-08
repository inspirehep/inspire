# -*- coding: utf-8 -*-
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
"""
WebSearch templates. Customize the look of search of Inspire
"""
__revision__ = \
    "$Id$"

import cgi
import time
import cgi
import string
import re
import locale


from invenio.config import \
     CFG_SITE_LANG, \
     CFG_SITE_NAME, \
     CFG_SITE_NAME_INTL, \
     CFG_SITE_SUPPORT_EMAIL, \
     CFG_SITE_SECURE_URL, \
     CFG_SITE_URL, \
     CFG_VERSION, \
     CFG_WEBSTYLE_INSPECT_TEMPLATES, \
     CFG_WEBSTYLE_TEMPLATE_SKIN, \
     CFG_WEBSEARCH_LIGHTSEARCH_PATTERN_BOX_WIDTH, \
     CFG_WEBSEARCH_SIMPLESEARCH_PATTERN_BOX_WIDTH, \
     CFG_WEBSEARCH_ADVANCEDSEARCH_PATTERN_BOX_WIDTH, \
     CFG_WEBSEARCH_SPLIT_BY_COLLECTION, \
     CFG_WEBSEARCH_DEF_RECORDS_IN_GROUPS, \
     CFG_BIBRANK_SHOW_READING_STATS, \
     CFG_BIBRANK_SHOW_DOWNLOAD_STATS, \
     CFG_BIBRANK_SHOW_DOWNLOAD_GRAPHS, \
     CFG_BIBRANK_SHOW_CITATION_LINKS, \
     CFG_BIBRANK_SHOW_CITATION_STATS, \
     CFG_BIBRANK_SHOW_CITATION_GRAPHS, \
     CFG_WEBSEARCH_RSS_TTL, \
     CFG_SITE_SUPPORT_EMAIL, \
     CFG_SITE_ADMIN_EMAIL, \
     CFG_INSPIRE_SITE, \
     CFG_WEBSEARCH_DEFAULT_SEARCH_INTERFACE, \
     CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES, \
     CFG_WEBSEARCH_MAX_RECORDS_IN_GROUPS


from invenio.dbquery import run_sql
from invenio.messages import gettext_set_language
from invenio.urlutils import make_canonical_urlargd, drop_default_urlargd, create_html_link, create_url
#from invenio.htmlutils import nmtoken_from_string
#from invenio.webinterface_handler import wash_urlargd
#from invenio.bibrank_citation_searcher import get_cited_by_count
#from invenio.intbitset import intbitset
#from invenio.websearch_externacollections import external_collection_get_state, get_external_collection_engine
#from invenio.websearch_external_collections_utils import get_collection_id
#from invenio.websearch_external_collections_config import CFG_EXTERNAL_COLLECTION_MAXRESULTS


from invenio.messages import gettext_set_language
from invenio.dateutils import convert_datestruct_to_dategui, \
     convert_datecvs_to_datestruct
from invenio.websearch_templates import Template as DefaultTemplate

class Template(DefaultTemplate):
    """INSPIRE style templates."""

    def tmpl_searchfor_simple(self, ln, collection_id, collection_name, record_count,
                 middle_option='',  ):
        """Produces light *Search for* box for the current collection.

        Parameters:

          - 'ln' *string* - *str* The language to display
          - 'collection_id' - *str* The collection id
          - 'collection_name' - *str* The collection name in current language

        """
        # load the right message language
        _ = gettext_set_language(ln)

        out = ''


        argd = drop_default_urlargd({'ln': ln, 'sc': CFG_WEBSEARCH_SPLIT_BY_COLLECTION},
                                    self.search_results_default_urlargd)

        # Only add non-default hidden values
        for field, value in argd.items():
            out += self.tmpl_input_hidden(field, value)


        header = _('Use "find" for SPIRES-style searches')

        asearchurl = self.build_search_interface_url(c=collection_id,
                                                     aas=max(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES),
                                                     ln=ln)
        #get examples
        example_html = self.tmpl_show_examples(collection_id, ln)

        # print commentary start:
        out += '''
        <table class="searchbox lightsearch">
        <thead>
          <tr align="left">
           <th colspan="3" class="searchboxheader">%(header)s</th>
          </tr>
         </thead>
         <tbody>
          <tr valign="baseline">
           <td class="searchboxbody" align="right"><input type="text" id="mainlightsearchfield" name="p" size="%(sizepattern)d" class="lightsearchfield"/><br/>
             <small><small>%(example_query_html)s</small></small>
           </td>
           <td class="searchboxbody" align="left">
             <input class="formbutton" type="submit" name="action_search" value="%(msg_search)s" />
           </td>
           <td class="searchboxbody" align="left" rowspan="2" valign="top">
             <small><small>
             <a href="%(siteurl)s/help/search-tips%(langlink)s">%(msg_search_tips)s</a><br/>
             %(asearch)s
             </small></small>
           </td>
          </tr></table>
          <!--<tr valign="baseline">
           <td class="searchboxbody" colspan="2" align="left">
           </td>
          </tr>
         </tbody>
        </table>-->
        ''' % {'ln' : ln,
               'sizepattern' : CFG_WEBSEARCH_LIGHTSEARCH_PATTERN_BOX_WIDTH,
               'langlink': ln != CFG_SITE_LANG and '?ln=' + ln or '',
               'siteurl' : CFG_SITE_URL,
               'asearch' : create_html_link(asearchurl, {}, _('Easy Search')),
               'header' : header,
               'msg_search' : _('Search'),
               'msg_browse' : _('Browse'),
               'msg_search_tips' : _('Search Tips'),
               'example_query_html': example_html
              }

        return out


    def tmpl_show_examples(self, collection_name, ln):
        "returns html with js controls for example searches"

      # load the right message language
        _ = gettext_set_language(ln)

        def get_example_search_queries(name):
            """Returns list of sample search queries for this collection.
            """
            res = run_sql("""SELECT example.body FROM example LEFT JOIN collection_example ON example.id=collection_example.id_example LEFT JOIN collection ON collection_example.id_collection=collection.id WHERE collection.name=%s ORDER BY collection_example.score""", (name,))
            return [query[0] for query in res]


                # Build example of queries for this collection
        example_search_queries = get_example_search_queries(collection_name)
        example_search_queries_links = [create_html_link(self.build_search_url(p=example_query,
                                                                               ln=ln,
                                                                               aas= -1,
                                                                               c=collection_name),
                                                         {},
                                                         cgi.escape(example_query),
                                                         {'class': 'examplequery'}) \
                                        for example_query in example_search_queries]

        example_query_html = ''
        if len(example_search_queries) > 0:
            example_query_link = example_search_queries_links[0]

            help_links = '''
            %(also)s
            <a href="%(siteurl)s/help/search-tips%(langlink)s">
            %(msg_search_tips)s</a> and
            <a href="%(siteurl)s/help%(langlink)s">
            %(msg_help)s</a>''' % {
                'also' : _('See also'),
                'msg_search_tips' : _('Search Tips'),
                'msg_help' : _('Full Help'),
                'langlink' : ln != CFG_SITE_LANG and '?ln=' + ln or '',
                'siteurl': CFG_SITE_URL
                }


            # offers more examples if possible
            more = ''
            if len(example_search_queries_links) > 1:
                more = '''
                <script type="text/javascript">
                function toggle_more_example_queries_visibility(){
                    var more = document.getElementById('more_example_queries');
                    var link = document.getElementById('link_example_queries');
                    var sep = document.getElementById('more_example_sep');
                    if (more.style.display=='none'){
                        more.style.display = '';
                        link.innerHTML = "%(show_less)s"
                        link.style.color = "rgb(204,0,0)";
                        sep.style.display = 'none';
                    } else {
                        more.style.display = 'none';
                        link.innerHTML = "%(show_more)s"
                        link.style.color = "rgb(0,0,204)";
                        sep.style.display = '';
                    }
                    return false;
                }
                </script>
                <span id="more_example_queries"
            style="display:none;text-align:right"><br/>%(more_example_queries)s<br/>%(help_links)s<br/></span>
                <a id="link_example_queries" href="#" onclick="toggle_more_example_queries_visibility()" style="display:none"></a>
                <script type="text/javascript">
                    var link = document.getElementById('link_example_queries');
                    var sep = document.getElementById('more_example_sep');
                    link.style.display = '';
                    link.innerHTML = "%(show_more)s";
                    sep.style.display = '';
                </script>
                ''' % {'more_example_queries': '<br/>'.join(example_search_queries_links[1:]),
                       'show_less':_("less"),
                       'show_more':_("more"),
                       'help_links':help_links
                       }

            example_query_html += '''<p style="text-align:right;margin:0px;">
            %(example)s<span id="more_example_sep" style="display:none;">&nbsp;&nbsp;::&nbsp;</span>%(more)s
            </p>
            ''' % {'example': _("Example: %(x_sample_search_query)s") % \
                   {'x_sample_search_query': example_query_link},
                   'more': more}

            return example_query_html



    def tmpl_searchfor_advanced(self,
                                ln, # current language
                                collection_id,
                                collection_name,
                                record_count,
                                middle_option_1, middle_option_2, middle_option_3,
                                searchoptions,
                                sortoptions,
                                rankoptions,
                                displayoptions,
                                formatoptions
                                ):
        """
          Produces advanced *Search for* box for the current collection.

          Parameters:

            - 'ln' *string* - The language to display

            - 'middle_option_1' *string* - HTML code for the first row of options (any field, specific fields ...)

            - 'middle_option_2' *string* - HTML code for the second row of options (any field, specific fields ...)

            - 'middle_option_3' *string* - HTML code for the third row of options (any field, specific fields ...)

            - 'searchoptions' *string* - HTML code for the search options

            - 'sortoptions' *string* - HTML code for the sort options

            - 'rankoptions' *string* - HTML code for the rank options

            - 'displayoptions' *string* - HTML code for the display options

            - 'formatoptions' *string* - HTML code for the format options

        """

        # load the right message language
        _ = gettext_set_language(ln)

        out = '''
        <!--create_searchfor_advanced()-->
        '''

        argd = drop_default_urlargd({'ln': ln, 'aas': 0, 'cc': collection_id, 'sc': CFG_WEBSEARCH_SPLIT_BY_COLLECTION},
                                    self.search_results_default_urlargd)

        # Only add non-default hidden values
        for field, value in argd.items():
            out += self.tmpl_input_hidden(field, value)


        header = _("Search %s records for") % \
                 self.tmpl_nbrecs_info(record_count, "", "")
        header += ':'
        ssearchurl = self.build_search_interface_url(c=collection_id, 
                                    aas=min(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES), ln=ln)

        out += '''

        <script type="text/javascript">
            function perform_easy_search() {
                // get values
                author = document.getElementById('author').value;
                title = document.getElementById('title').value;
                c = document.getElementById('c').value;
                rn = document.getElementById('rn').value;
                aff = document.getElementById('aff').value;
                cn = document.getElementById('cn').value;
                k = document.getElementById('k').value;
                eprinttype = document.getElementById('eprinttype');
                eprinttype = eprinttype.options[eprinttype.selectedIndex].value;
                eprintnumber = document.getElementById('eprintnumber').value;
                topcite = document.getElementById('topcite');
                topcite = topcite.options[topcite.selectedIndex].value;
                j = document.getElementById('j');
                j = j.options[j.selectedIndex].value;
                jvol = document.getElementById('jvol').value;
                jpage = document.getElementById('jpage').value;

                // filter and build
                query = 'find';
                if (author != '') { query += ' and a ' + author; }
                if (title != '') { query += ' and t ' + title; }
                if (c != '') { query += ' and c ' + c; }
                if (rn != '') { query += ' and rn ' + rn; }
                if (aff != '') { query += ' and aff ' + aff; }
                if (cn != '') { query += ' and cn ' + cn; }
                if (k != '') { query += ' and k ' + k; }
                if (eprinttype != '' && eprintnumber != '') {
                    query += ' and eprint ' + eprinttype + ' ' + eprintnumber;
                }
                else {
                    if (eprinttype != '') {
                        query += ' and eprint ' + eprinttype;
                    }
                    if (eprintnumber != '') {
                        query += ' and eprint ' + eprintnumber;
                    }
                }
                if (topcite != '') { query += ' and topcite ' + topcite; }
                if (j != '' && jvol != '' && jpage != '') { query += ' and j ' + j + ','+ jvol + ',' + jpage; }
                else {
                    if (j != '') { query += ' and j ' + j; }
                    if (jvol != '') { query += ' and jvol ' + jvol; }
                    if (jpage != '') { query += ' and jp ' + jpage; }
                }

                query = query.replace(/topcite (\d+)?\+/, 'topcite $1->99999');
                query = query.replace(' and ', ' ');
                query = query.replace(/ /g, '+');
                search_url = '%(search_url)s'.replace('QUERY', query);
                window.location = search_url;
            };
        </script>

        <table class="searchbox advancedsearch">
         <thead>
          <tr>
           <th class="searchboxheader" colspan="3">%(header)s</th>
          </tr>
         </thead>

         <tbody>
         <table border="0">
          <tr valign="bottom">
            <td class="searchboxbody" style="white-space: nowrap;">

          <tr>
            <th align="right">Author:</th>
            <td align="left"><input size="40" id="author"/></td>
          </tr>
         
          <tr>
            <th align="right">Title:</th>
            <td align="left"><input size="40" id="title" /></td>
          </tr>

          <tr>
            <th align="right">Citation:</th>
            <td align="left"><input size="40" id="c" /></td>
          </tr>

          <tr>
            <th align="right">Report Number:</th>
            <td align="left"><input size="40" id="rn" /></td>
          </tr>

          <tr>
            <th align="right">Affiliation:</th>
            <td align="left"><input size="40" id="aff" /></td>
          </tr>

          <tr>
            <th align="right">Collaboration:</th>
            <td align="left"><input size="40" id="cn" /></td>
          </tr>

          <tr>
            <th align="right">Keywords:</th>
            <td align="left"><input size="40" id="k" /></td>
          </tr>
          
          <tr>
            <th align="right">Eprint:</th>
            <td align="left"><select id="eprinttype">
            <option value="" selected="selected">Any Type</option>
            <option>ACC-PHYS</option>
            <option>ASTRO-PH</option>
            <option>GR-QC</option>

            <option>HEP-EX</option>
            <option>HEP-LAT</option>
            <option>HEP-PH</option>
            <option>HEP-TH</option>

            <option>NUCL-EX</option>
            <option>NUCL-TH</option>

            <option>PHYSICS</option>
            <option>QUANT-PH</option>
            </select>&nbsp;&nbsp; Number
	        <input size="14" id="eprintnumber" />
	        </td>
        </tr>

        <tr>
          <th align="right">Topcite:</th>
          <td align="left">
	      <select id="topcite">
            <option value="" selected="selected">Don\'t care</option>
            <option>50+</option>
            <option>100+</option>
            <option>250+</option>
            <option>500+</option>
            <option>1000+</option>
            <option>50->99</option>
            <option>100->249</option>
            <option>250->499</option>
            <option>500->999</option>
            </select>
	      </td>
        </tr>
        
        <tr>
          <th align="right">Journal:</th>
          <td align="left"><select id="j">
            <option value="" selected="selected">Any Journal</option>
            <option>Acta Phys.Austr.</option>

            <option>Acta Phys.Polon.</option>
            <option>Ann.Poincare</option>
            <option>Ann.Phys.(N.Y.)</option>
            <option>Astropart.Phys.</option>
            <option>Astrophys.J.</option>
            <option>Can.J.Phys.</option>

            <option>Class.Quant.Grav.</option>
            <option>Comm.Nucl.Part.Phys.</option>
            <option>Commun.Math.Phys.</option>
            <option>Commun. Theor. Phys.</option>
            <option>Comput. Phys. Commun.</option>
            <option>Czech. J. Phys.</option>

            <option>Europhys. Lett.</option>
            <option>Eur. Phys. J.</option>
            <option>Few Body Syst.</option>
            <option>Fiz. Elem. Chast. At. Yadra</option>
            <option>Fizika</option>
            <option>Fortschr. Phys.</option>

            <option>Found. Phys.</option>
            <option>Gen. Rel. Grav.</option>
            <option>Hadronic J.</option>
            <option>Helv. Phys. Acta</option>
            <option>High Energy Phys. Nucl. Phys.</option>
            <option>Ieee Trans. Magnetics</option>

            <option>Ieee Trans. Nucl. Sci.</option>
            <option>Instrum. Exp. Tech.</option>
            <option>Int. J. Mod. Phys.</option>
            <option>Int. J. Theor. Phys.</option>
	        <option>Jcap</option>
            <option>Jhep</option>

            <option>J. Math. Phys.</option>
            <option>J. Phys. - A -</option>
            <option>J. Phys. - G -</option>
            <option>J. Phys. Soc. Jap.</option>
            <option>Jetp Lett.</option>
            <option>Lett. Math. Phys.</option>

            <option>Lett. Nuovo Cim.</option>
	        <option>Living Rev. Rel.</option>
	        <option>Mod. Phys. Lett.</option>
	        <option>Mon.Not.Roy.Astron.Soc.</option>
            <option>New J.Phys.</option>
            <option>Nucl.Instrum.Meth.</option>
            <option>Nucl.Phys.</option>

            <option>Nucl.Phys.(Proc.Suppl.)</option>
            <option>Nuovo Cim.</option>
            <option>Part. Accel.</option>
            <option>Phys. Atom. Nucl.</option>
            <option>Phys.Lett.</option>
            <option>Phys.Rept.</option>

            <option>Phys.Rev.</option>
            <option>Phys.Rev.Lett.</option>
            <option>Phys. Scripta</option>
            <option>Physica</option>
            <option>Pisma Zh. Eksp. Teor. Fiz.</option>
            <option>Pramana</option>

            <option>Prog. Part. Nucl. Phys.</option>
            <option>Prog. Theor. Phys.</option>
            <option>Rept. Math. Phys.</option>
            <option>Rept. Prog. Phys.</option>
            <option>Rev. Mod. Phys.</option>
            <option>Rev. Sci. Instrum.</option>

            <option>Riv. Nuovo Cim.</option>
            <option>Russ. Phys. J. (Sov. Phys. J.)</option>
            <option>Sov. J. Nucl. Phys.</option>
            <option>Sov. Phys. Jetp</option>
            <option>Teor. Mat. Fiz.</option>
            <option>Theor. Math. Phys.</option>

            <option>Yad. Fiz.</option>
            <option>Z. Phys.</option>
            <option>Zh. Eksp. Teor. Fiz.</option>
            </select>&nbsp;&nbsp; 
            vol:<input size="8" id="jvol" />
            pg: <input size="8" id="jpage" /></td>
        </tr>

        <tr>
          <td class="searchboxbody" style="white-space: nowrap;" align="center">
              <input type="button" onclick="perform_easy_search()" name="action_search" value="%(msg_search)s" />
          </td>
        </tr>
        
        <tr valign="bottom">
            <td colspan="3" class="searchboxbody" align="right">
              <small>
                <a href="%(siteurl)s/help/search-tips%(langlink)s">%(msg_search_tips)s</a> ::
                %(ssearch)s
              </small>
            </td>
        </tr>
        
        </tbody>
        </table>

        <!-- @todo - more imports -->
        ''' % {'ln' : ln,
               'sizepattern' : CFG_WEBSEARCH_ADVANCEDSEARCH_PATTERN_BOX_WIDTH,
               'langlink': ln != CFG_SITE_LANG and '?ln=' + ln or '',
               'siteurl' : CFG_SITE_URL,
               'ssearch' : create_html_link(ssearchurl, {}, _("Simple Search")),
               'search_url' : (CFG_SITE_URL + '/search?p=QUERY&action_search=Search'),
               'header' : header,

               'matchbox_m1' : self.tmpl_matchtype_box('m1', ln=ln),
               'middle_option_1' : middle_option_1,
               'andornot_op1' : self.tmpl_andornot_box('op1', ln=ln),

               'matchbox_m2' : self.tmpl_matchtype_box('m2', ln=ln),
               'middle_option_2' : middle_option_2,
               'andornot_op2' : self.tmpl_andornot_box('op2', ln=ln),

               'matchbox_m3' : self.tmpl_matchtype_box('m3', ln=ln),
               'middle_option_3' : middle_option_3,

               'msg_search' : _("Search"),
               'msg_search_tips' : _("Search Tips")
            }

        if (searchoptions):
            out += """<table class="searchbox">
                      <thead>
                       <tr>
                         <th class="searchboxheader">
                           %(searchheader)s
                         </th>
                       </tr>
                      </thead>
                      <tbody>
                       <tr valign="bottom">
                        <td class="searchboxbody">%(searchoptions)s</td>
                       </tr>
                      </tbody>
                     </table>""" % {
                       'searchheader' : _("Search options:"),
                       'searchoptions' : searchoptions
                     }

        out += """<table class="searchbox">
                   <thead>
                    <tr>
                      <th class="searchboxheader">
                        %(added)s
                      </th>
                      <th class="searchboxheader">
                        %(until)s
                      </th>
                    </tr>
                   </thead>
                   <tbody>
                    <tr valign="bottom">
                      <td class="searchboxbody">%(added_or_modified)s %(date_added)s</td>
                      <td class="searchboxbody">%(date_until)s</td>
                    </tr>
                   </tbody>
                  </table>
                  <table class="searchbox">
                   <thead>
                    <tr>
                      <th class="searchboxheader">
                        %(msg_sort)s
                      </th>
                      <th class="searchboxheader">
                        %(msg_display)s
                      </th>
                      <th class="searchboxheader">
                        %(msg_format)s
                      </th>
                    </tr>
                   </thead>
                   <tbody>
                    <tr valign="bottom">
                      <td class="searchboxbody">%(sortoptions)s %(rankoptions)s</td>
                      <td class="searchboxbody">%(displayoptions)s</td>
                      <td class="searchboxbody">%(formatoptions)s</td>
                    </tr>
                   </tbody>
                  </table>
                  <!--/create_searchfor_advanced()-->
              """ % {
                    'added' : _("Added/modified since:"),
                    'until' : _("until:"),
                    'added_or_modified': self.tmpl_inputdatetype(ln=ln),
                    'date_added' : self.tmpl_inputdate("d1", ln=ln),
                    'date_until' : self.tmpl_inputdate("d2", ln=ln),

                    'msg_sort' : _("Sort by:"),
                    'msg_display' : _("Display results:"),
                    'msg_format' : _("Output format:"),
                    'sortoptions' : sortoptions,
                    'rankoptions' : rankoptions,
                    'displayoptions' : displayoptions,
                    'formatoptions' : formatoptions
                  }
        return out
