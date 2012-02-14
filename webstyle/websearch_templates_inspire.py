# -*- coding: utf-8 -*-
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2011 CERN.
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

from invenio.config import CFG_BIBRANK_SHOW_CITATION_LINKS
from invenio.config import CFG_WEBCOMMENT_ALLOW_COMMENTS
from invenio.config import CFG_WEBSEARCH_SHOW_COMMENT_COUNT
from invenio.config import CFG_SITE_RECORD
from invenio.config import CFG_WEBCOMMENT_ALLOW_REVIEWS
from invenio.config import CFG_WEBSEARCH_SHOW_REVIEW_COUNT
from invenio.search_engine_utils import get_fieldvalues
from invenio.bibrank_citation_searcher import get_cited_by_count

CFG_SEARCH_INSPIRE_OUTPUT_FORMATS = [
                   {'value' : "hb",
                    'text' : "Brief format"
                    },
                   {'value' : "hd",
                    'text' : "Detailed format"
                    },
                   {'value' : "hcs",
                    'text' : "Citesummary"
                    },
                   {'value' : "hlxe",
                    'text' : "LaTeX (EU)"
                    },
                   {'value' : "hlxu",
                    'text' : "LaTeX (US)"
                    },
                   {'value' : "hx",
                    'text' : "BibTeX"
                    },
                   {'value' : "tlcv",
                    'text' : "CV format (LaTeX)"
                    },
                   {'value' : "hcv",
                    'text' : "CV format (html)"
                    },
                   {'value' : "htcv",
                    'text' : "CV format (text)"
                    },
                   {'value' : "hlxh",
                    'text' : "Harvmac"
                    },
                   {'value' : "xw",
                    'text' : "RefWorks"
                    },
                   {'value' : "xe",
                    'text' : "EndNote"
                    }
               ]

CFG_SEARCH_INSPIRE_JOB_RANKS = [
                   {'value' : "senior",
                    'text' : "Senior"
                    },
                   {'value' : "junior",
                    'text' : "Junior"
                    },
                   {'value' : "postdoc",
                    'text' : "Postdoc"
                    },
                   {'value' : "student",
                    'text' : "Student"
                    },
                   {'value' : "visitor",
                    'text' : "Visiting Scientist"
                    },
                   {'value' : "staff",
                    'text' : "Staff"
                    }
               ]

CFG_SEARCH_INSPIRE_JOB_REGIONS = [
                   {'value' : "africa",
                    'text' : "Africa"
                    },
                   {'value' : "asia",
                    'text' : "Asia"
                    },
                   {'value' : "australasia",
                    'text' : "Australasia"
                    },
                   {'value' : "europe",
                    'text' : "Europe"
                    },
                   {'value' : "middle east",
                    'text' : "Middle East"
                    },
                   {'value' : "north america",
                    'text' : "North America"
                    },
                   {'value' : "south america",
                    'text' : "South America"
                    }
               ]

CFG_SEARCH_INSPIRE_JOB_FIELDS = [
                   {'value' : "astro-ph",
                    'text' : "astro-ph"
                    },
                   {'value' : "cond-mat",
                    'text' : "cond-mat"
                    },
                   {'value' : "cs",
                    'text' : "cs"
                    },
                   {'value' : "gr-qc",
                    'text' : "gr-qc"
                    },
                   {'value' : "hep-ex",
                    'text' : "hep-ex"
                    },
                   {'value' : "hep-lat",
                    'text' : "hep-lat"
                    },
                   {'value' : "hep-ph",
                    'text' : "hep-ph"
                    },
                   {'value' : "hep-th",
                    'text' : "hep-th"
                    },
                   {'value' : "math",
                    'text' : "math"
                    },
                   {'value' : "math-ph",
                    'text' : "math-ph"
                    },
                   {'value' : "nucl-ex",
                    'text' : "nucl-ex"
                    },
                   {'value' : "nucl-th",
                    'text' : "nucl-th"
                    },
                   {'value' : "physics.acc-phys",
                    'text' : "physics.acc-phys"
                    },
                   {'value' : "physics.ins-det",
                    'text' : "physics.ins-det"
                    },
                   {'value' : "physics-other",
                    'text' : "physics-other"
                    },
                   {'value' : "quant-ph",
                    'text' : "quant-ph"
                    }
               ]

class Template(DefaultTemplate):
    """INSPIRE style templates."""

    def tmpl_searchfor_simple(self, ln, collection_id, collection_name, record_count,
                 middle_option='', searchvalue='', of='hb'):
        """Produces light *Search for* box for the current collection.

        Parameters:

          - 'ln' *string* - *str* The language to display
          - 'collection_id' - *str* The collection id
          - 'collection_name' - *str* The collection name in current language
          - 'searchvalue' - prepopulate search box with this value

        """
        # load the right message language
        _ = gettext_set_language(ln)

        out = '''
        <!--create_searchfor_simple()-->
        '''

        argd = drop_default_urlargd({'ln': ln, 'cc': collection_id, 'sc': CFG_WEBSEARCH_SPLIT_BY_COLLECTION},
                                    self.search_results_default_urlargd)

        # Only add non-default hidden values
        for field, value in argd.items():
            out += self.tmpl_input_hidden(field, value)


        # lets decorate the search box with some help if there is no value present
        if searchvalue:
            header = ''
        else:
            header = '''%(findtip)s <a href="%(siteurl)s/help/search-tips%(langlink)s">%(msg_search_tips)s</a>''' %  {
                'findtip' : _('Use "find " for SPIRES-style search'),
                'langlink' :  ln != CFG_SITE_LANG and '?ln=' + ln or '',
                'siteurl' : CFG_SITE_URL,
                'msg_search_tips' : _('(other tips)'),
                }

        asearchurl = self.build_search_interface_url(c=collection_id,
                                                     aas=max(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES),
                                                     ln=ln)
        #get examples
        example_html = self.tmpl_show_examples(collection_id, ln)

        langlink = ln != CFG_SITE_LANG and '?ln=' + ln or ''
        easy_search_link = ""
        middle_option = ""

        if collection_id == "HEP":
            # add easy search link
            easy_search_link = create_html_link("%s/help/easy-search%s" % (CFG_SITE_URL, langlink), {}, _("Easy Search")) + "<br/>"

            # add output format select box for HEP
            middle_option = '<td class="searchboxbody" align="left">%s</td>' % \
                (self.tmpl_select(
                 fieldname='of',
                 selected=of,
                 values=self._add_mark_to_field(value=of, fields=CFG_SEARCH_INSPIRE_OUTPUT_FORMATS, chars=3, ln=ln),
                 css_class=''),)
        # print commentary start:
        if collection_id == "Jobs":
            # print Jobs Search form:
            out += self.tmpl_searchfor_jobs(ln, collection_id, filters="", keywords="", of="")
            return out
        out += '''
            <table class="searchbox lightsearch">
            <thead>
              <tr align="left">
               <th class="searchboxheader">%(header)s</th>
              </tr>
             </thead>
             <tbody>
              <tr valign="baseline">
               <td class="searchboxbody searchboxbodyinput" align="right"><input type="text" id="mainlightsearchfield" name="p" size="%(sizepattern)d" class="lightsearchfield searchboxbodyinput" value="%(searchvalue)s"/><br/>
               </td>
               %(middle_option)s
               <td class="searchboxbody" align="left">
                 <input class="formbutton" type="submit" name="action_search" value="%(msg_search)s" />
               </td>
               <td class="searchboxbody searchboxbodymoresearch" align="left" rowspan="2" valign="top">
                 %(esearch)s
                 %(asearch)s
               </td>
               </tr>
               <tr>
                 <td class="searchboxexample">
                   %(example_query_html)s
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
                   'langlink': langlink,
                   'siteurl' : CFG_SITE_URL,
                   'esearch' : easy_search_link,
                   'asearch' : create_html_link(asearchurl, {}, _('Advanced Search')),
                   'header' : header,
                   'msg_search' : _('Search'),
                   'msg_browse' : _('Browse'),
                   'msg_easy_search' : _('Easy Search'),
                   'example_query_html': example_html,
                   'searchvalue' : searchvalue,
                   'middle_option' : middle_option
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
                                                                               aas= 0,
                                                                               cc=collection_name),
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

            example_query_html += '''%(example)s<span id="more_example_sep" style="display:none;">&nbsp;&nbsp;::&nbsp;</span>%(more)s
            ''' % {'example': _("%(x_sample_search_query)s") % \
                   {'x_sample_search_query': example_query_link},
                   'more': more}

            return example_query_html


    #disabled at the moment...

    def tmpl_searchfor_easy(self, ln, collection_id, collection_name, record_count,
                            searchoptions, sortoptions, rankoptions, displayoptions, formatoptions):
        """
          Produces SPIRES-style easy search box. NOT USED

          Parameters:

            - 'ln' *string* - The language to display

            - 'searchoptions' *string* - HTML code for the search options

            - 'sortoptions' *string* - HTML code for the sort options

            - 'rankoptions' *string* - HTML code for the rank options

            - 'displayoptions' *string* - HTML code for the display options

            - 'formatoptions' *string* - HTML code for the format options

        """

        # load the right message language
        _ = gettext_set_language(ln)

        out = '''
        <!--create_searchfor_easy()-->
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

        <table class="advancedsearch">
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
            <option>JINST</option>

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
                %(ssearch)s::
                %(advanced_search)s
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
               'ssearch' : create_html_link(ssearchurl, {}, _("Regular Search")),
               'advanced_search': create_html_link(self.build_search_url(rm=rm,
                                                                        aas=max(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES),
                                                                        cc=cc,
                                                                        jrec=jrec,
                                                                        ln=ln,
                                                                        rg=rg),
                                                  {}, _("Advanced Search")),

               'leading' : leadingtext,
               'search_url' : (CFG_SITE_URL + '/search?p=QUERY&action_search=Search'),
               'header' : header,

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
                  <!--/create_searchfor_easy()-->
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

    def tmpl_searchfor_jobs(self, ln, collection_id, filters, keywords, of='hb'):
        """Produces Search filter box for the Jobs collection.

        Parameters:

          - 'ln' *string* - *str* The language to display
          - 'collection_id' - *str* The collection id. For example: Jobs
          - 'filters' - *str* The first search string (p1) used for filters (rank etc.)
          - 'keywords' - *str* The first search string (p2) used for keywords
          - 'of' - *str* Currently selected output format
        """
        # load the right message language
        _ = gettext_set_language(ln)

        out = '''
        <!--create_searchfor_jobs()-->
        '''

        argd = drop_default_urlargd({'ln': ln, 'cc': collection_id, 'sc': CFG_WEBSEARCH_SPLIT_BY_COLLECTION},
                                    self.search_results_default_urlargd)

        # Only add non-default hidden values
        for field, value in argd.items():
            out += self.tmpl_input_hidden(field, value)


        # lets decorate the search box with some help
        header = _('Optionally add some keywords to the search:')

        asearchurl = self.build_search_interface_url(c=collection_id,
                                                     aas=max(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES),
                                                     ln=ln)

        #get examples
        example_html = self.tmpl_show_examples(collection_id, ln)

        langlink = ln != CFG_SITE_LANG and '?ln=' + ln or ''

        clear_button = '<span id="reset_search">%s</span>' % (_("Reset search"))
        msg_search = _('Search')
        msg_header = "Select search filters (multiples allowed):"

        rank_selected = [item['value'] for item in CFG_SEARCH_INSPIRE_JOB_RANKS if '"' + item['value'] + '"' in filters]
        rank_select = self.tmpl_select_multiple(fieldname="rank", \
                                                values=CFG_SEARCH_INSPIRE_JOB_RANKS, \
                                                selected=rank_selected, \
                                                css_id='rank', \
                                                size=5)

        region_selected = [item['value'] for item in CFG_SEARCH_INSPIRE_JOB_REGIONS if '"' + item['value'] + '"' in filters]
        region_select = self.tmpl_select_multiple(fieldname="region", \
                                                values=CFG_SEARCH_INSPIRE_JOB_REGIONS, \
                                                selected=region_selected, \
                                                css_id='region', \
                                                size=5)

        field_selected = [item['value'] for item in CFG_SEARCH_INSPIRE_JOB_FIELDS if item['value'] in filters]
        field_select = self.tmpl_select_multiple(fieldname="field", \
                                                values=CFG_SEARCH_INSPIRE_JOB_FIELDS, \
                                                selected=field_selected, \
                                                css_id='field', \
                                                size=5)

        out += '''
        <script type="text/javascript">
        $(document).ready(function(){
            // Disable default search on Enter key and launch job search.
            $(window).keydown(function(event){ if(event.keyCode === 13) { event.preventDefault(); perform_job_search(); return false; } });
        });
        </script>
        <h3 class="jobfilter_header">%(msg_header)s</h3>
        <table id="jobfilters">
        <thead>
        <th><label for="rank">Rank:</label></th>
        <th><label for="region">Region:</label></th>
        <th><label for="field">Field:</label></th>
        </thead>
        <tbody>
        <tr>
        <td>%(rank_select)s</td>
        <td>%(region_select)s</td>
        <td>%(field_select)s</td>
        <td class="searchboxbody searchboxbodymoresearch" align="left" rowspan="2" valign="top">
          <em>Crtl + click</em> to select multiple<br />
          <em>Crtl + click</em> existing to remove<br />
          %(clear_search)s
        </td>
        </tr>
        </tbody>
        </table>

        <table class="searchbox lightsearch">
        <thead>
          <tr align="left">
           <th class="searchboxheader">%(header)s</th>
          </tr>
         </thead>
         <tbody>
          <tr valign="baseline">
           <td class="searchboxbody searchboxbodyinput" align="right">
               <input type="text" id="mainlightsearchfield" name="p2" size="%(sizepattern)d" class="lightsearchfield searchboxbodyinput" value="%(keywords)s"/><br/>
           </td>
           <td class="searchboxbody" align="left">
             <input class="formbutton" type="button" name="action_search" value="%(msg_search)s" onclick="perform_job_search('%(search_url)s')" />
           </td>
           </tr>
           <tr>
             <td class="searchboxexample">
               %(example_query_html)s
             </td>
          </tr>
          </table>
          <!--<tr valign="baseline">
           <td class="searchboxbody" colspan="2" align="left">
           </td>
          </tr>
         </tbody>
        </table>-->
        ''' % {'ln' : ln,
               'sizepattern' : CFG_WEBSEARCH_LIGHTSEARCH_PATTERN_BOX_WIDTH,
               'langlink': langlink,
               'siteurl' : CFG_SITE_URL,
               'clear_search' : clear_button,
               'header' : header,
               'msg_search' : msg_search,
               'example_query_html': example_html,
               'keywords' : keywords,
               'search_url' : '/search?p1=QUERY&op1=a&p2=KEYWORD&action_search=Search&cc=Jobs',
               'msg_header' : msg_header,
               'rank_select' : rank_select,
               'region_select' : region_select,
               'field_select' : field_select
              }

        return out

    def tmpl_search_box(self, ln, aas, cc, cc_intl, ot, sp,
                        action, fieldslist, f1, f2, f3, m1, m2, m3,
                        p1, p2, p3, op1, op2, rm, p, f, coll_selects,
                        d1y, d2y, d1m, d2m, d1d, d2d, dt, sort_fields,
                        sf, so, ranks, sc, rg, formats, of, pl, jrec, ec,
                        show_colls=True, show_title=True):

        """
          Displays the *Nearest search terms* box

        Parameters:

          - 'ln' *string* - The language to display

          - 'aas' *bool* - Should we display an advanced search box? -1 -> 1, from simpler to more advanced

          - 'cc_intl' *string* - the i18nized current collection name, used for display

          - 'cc' *string* - the internal current collection name

          - 'ot', 'sp' *string* - hidden values

          - 'action' *string* - the action demanded by the user

          - 'fieldslist' *list* - the list of all fields available, for use in select within boxes in advanced search

          - 'p, f, f1, f2, f3, m1, m2, m3, p1, p2, p3, op1, op2, op3, rm' *strings* - the search parameters

          - 'coll_selects' *array* - a list of lists, each containing the collections selects to display

          - 'd1y, d2y, d1m, d2m, d1d, d2d' *int* - the search between dates

          - 'dt' *string* - the dates' types (creation dates, modification dates)

          - 'sort_fields' *array* - the select information for the sort fields

          - 'sf' *string* - the currently selected sort field

          - 'so' *string* - the currently selected sort order ("a" or "d")

          - 'ranks' *array* - ranking methods

          - 'rm' *string* - selected ranking method

          - 'sc' *string* - split by collection or not

          - 'rg' *string* - selected results/page

          - 'formats' *array* - available output formats

          - 'of' *string* - the selected output format

          - 'pl' *string* - `limit to' search pattern

          - show_colls *bool* - propose coll selection box?

          - show_title *bool* show cc_intl in page title?
        """

        # load the right message language
        _ = gettext_set_language(ln)

        # FIXME: temporarily switch off 'Search collections:'
        # drop-down box until INSPIRE collection tree is clarified and
        # properly set up:
        show_colls = False

        # These are hidden fields the user does not manipulate
        # directly
        if aas == -1:
            argd = drop_default_urlargd({
                'ln': ln, 'aas': aas,
                'ot': ot, 'sp': sp, 'ec': ec,
                }, self.search_results_default_urlargd)
        else:
            argd = drop_default_urlargd({
                'cc': cc, 'ln': ln, 'aas': aas,
                'ot': ot, 'sp': sp, 'ec': ec,
                }, self.search_results_default_urlargd)

        out = ""
        if show_title:
            # display cc name if asked for
            out += '''
            <h1 class="headline">%(ccname)s</h1>''' % {'ccname' : cgi.escape(cc_intl), }

        out += '''
        <form name="search" action="%(siteurl)s/search" method="get">
        ''' % {'siteurl' : CFG_SITE_URL}

        # Only add non-default hidden values
        for field, value in argd.items():
            out += self.tmpl_input_hidden(field, value)

        leadingtext = _("Search")

        if action == 'browse':
            leadingtext = _("Browse")

        if cc == "Jobs":
            # print Jobs Search form:
            # If p is specified use it instead of p2
            keywords = p and p or p2
            out += self.tmpl_searchfor_jobs(ln=ln, collection_id=cc, filters=p1, keywords=keywords, of=of)
        elif aas == 1:
            # print Advanced Search form:
            # define search box elements:
            out += '''
            <table class="advancedsearch">
             <thead>
              <tr>
               <th colspan="3" class="searchboxheader">
                %(leading)s:
               </th>
              </tr>
             </thead>
             <tbody>
              <tr valign="top" style="white-space:nowrap;">
                <td class="searchboxbody">%(matchbox1)s
                  <input type="text" name="p1" size="%(sizepattern)d" value="%(p1)s" class="advancedsearchfield"/>
                </td>
                <td class="searchboxbody">%(searchwithin1)s</td>
                <td class="searchboxbody">%(andornot1)s</td>
              </tr>
              <tr valign="top">
                <td class="searchboxbody">%(matchbox2)s
                  <input type="text" name="p2" size="%(sizepattern)d" value="%(p2)s" class="advancedsearchfield"/>
                </td>
                <td class="searchboxbody">%(searchwithin2)s</td>
                <td class="searchboxbody">%(andornot2)s</td>
              </tr>
              <tr valign="top">
                <td class="searchboxbody">%(matchbox3)s
                  <input type="text" name="p3" size="%(sizepattern)d" value="%(p3)s" class="advancedsearchfield"/>
                </td>
                <td class="searchboxbody">%(searchwithin3)s</td>
                <td class="searchboxbody"  style="white-space:nowrap;">
                  <input class="formbutton" type="submit" name="action_search" value="%(search)s" />
                  <input class="formbutton" type="submit" name="action_browse" value="%(browse)s" />&nbsp;
                </td>
              </tr>
              <tr valign="bottom">
                <td colspan="3" align="right" class="searchboxbody">
                  <small>
                    %(easy_search)s ::
                    %(simple_search)s
                  </small>
                </td>
              </tr>
             </tbody>
            </table>
            ''' % {
                'simple_search': create_html_link(self.build_search_url(p=p1, f=f1, rm=rm, cc=cc, ln=ln, jrec=jrec, rg=rg),
                                                  {}, _("Simple Search")),
                'easy_search': create_html_link(CFG_SITE_URL+'/help/easy-search',   # OK to hardcode; this is what we test
                                                  {}, _("Easy Search")),

                'leading' : leadingtext,
                'sizepattern' : CFG_WEBSEARCH_ADVANCEDSEARCH_PATTERN_BOX_WIDTH,
                'matchbox1' : self.tmpl_matchtype_box('m1', m1, ln=ln),
                'p1' : cgi.escape(p1, 1),
                'searchwithin1' : self.tmpl_searchwithin_select(
                                  ln=ln,
                                  fieldname='f1',
                                  selected=f1,
                                  values=self._add_mark_to_field(value=f1, fields=fieldslist, ln=ln)
                                ),
              'andornot1' : self.tmpl_andornot_box(
                                  name='op1',
                                  value=op1,
                                  ln=ln
                                ),
              'matchbox2' : self.tmpl_matchtype_box('m2', m2, ln=ln),
              'p2' : cgi.escape(p2, 1),
              'searchwithin2' : self.tmpl_searchwithin_select(
                                  ln=ln,
                                  fieldname='f2',
                                  selected=f2,
                                  values=self._add_mark_to_field(value=f2, fields=fieldslist, ln=ln)
                                ),
              'andornot2' : self.tmpl_andornot_box(
                                  name='op2',
                                  value=op2,
                                  ln=ln
                                ),
              'matchbox3' : self.tmpl_matchtype_box('m3', m3, ln=ln),
              'p3' : cgi.escape(p3, 1),
              'searchwithin3' : self.tmpl_searchwithin_select(
                                  ln=ln,
                                  fieldname='f3',
                                  selected=f3,
                                  values=self._add_mark_to_field(value=f3, fields=fieldslist, ln=ln)
                                ),
              'search' : _("Search"),
              'browse' : _("Browse"),
              'siteurl' : CFG_SITE_URL,
              'ln' : ln,
              'langlink': ln != CFG_SITE_LANG and '?ln=' + ln or '',
            }
        elif aas == 0:
            # print Simple Search form:

            out += self.tmpl_searchfor_simple(ln, cc, cgi.escape(cc_intl), 0,
                            middle_option='', searchvalue=cgi.escape(p, 1), of=of)

        else:
            # EXPERIMENTAL
            # print light search form:
            search_in = ''
            if cc_intl != CFG_SITE_NAME_INTL.get(ln, CFG_SITE_NAME):
                search_in = '''
            <input type="radio" name="cc" value="%(collection_id)s" id="searchCollection" checked="checked"/>
            <label for="searchCollection">%(search_in_collection_name)s</label>
            <input type="radio" name="cc" value="%(root_collection_name)s" id="searchEverywhere" />
            <label for="searchEverywhere">%(search_everywhere)s</label>
            ''' % {'search_in_collection_name': _("Search in %(x_collection_name)s") % \
                  {'x_collection_name': cgi.escape(cc_intl)},
                  'collection_id': cc,
                  'root_collection_name': CFG_SITE_NAME,
                  'search_everywhere': _("Search everywhere")}
            out += '''
            <table class="searchbox lightsearch">
              <tr valign="top">
                <td class="searchboxbody"><input type="text" name="p" size="%(sizepattern)d" value="%(p)s" class="lightsearchfield"/></td>
                <td class="searchboxbody">
                  <input class="formbutton" type="submit" name="action_search" value="%(search)s" />
                </td>
                <td class="searchboxbody" align="left" rowspan="2" valign="top">
                  <small><small>
                  <a href="%(siteurl)s/help/search-tips%(langlink)s">%(search_tips)s</a><br/>
                  %(advanced_search)s
                </td>
              </tr>
            </table>
            <small>%(search_in)s</small>
            ''' % {
              'sizepattern' : CFG_WEBSEARCH_LIGHTSEARCH_PATTERN_BOX_WIDTH,
              'advanced_search': create_html_link(self.build_search_url(p1=p,
                                                                        f1=f,
                                                                        rm=rm,
                                                                        aas=max(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES),
                                                                        cc=cc,
                                                                        jrec=jrec,
                                                                        ln=ln,
                                                                        rg=rg),
                                                  {}, _("Advanced Search")),

              'leading' : leadingtext,
              'p' : cgi.escape(p, 1),
              'searchwithin' : self.tmpl_searchwithin_select(
                                  ln=ln,
                                  fieldname='f',
                                  selected=f,
                                  values=self._add_mark_to_field(value=f, fields=fieldslist, ln=ln)
                                ),
              'search' : _("Search"),
              'browse' : _("Browse"),
              'siteurl' : CFG_SITE_URL,
              'ln' : ln,
              'langlink': ln != CFG_SITE_LANG and '?ln=' + ln or '',
              'search_tips': _("Search Tips"),
              'search_in': search_in
            }
        ## secondly, print Collection(s) box:

        if show_colls and aas > -1:
            # display collections only if there is more than one
            selects = ''
            for sel in coll_selects:
                selects += self.tmpl_select(fieldname='c', values=sel)

            out += """
                <table class="searchbox">
                 <thead>
                  <tr>
                   <th colspan="3" class="searchboxheader">
                    %(leading)s %(msg_coll)s:
                   </th>
                  </tr>
                 </thead>
                 <tbody>
                  <tr valign="bottom">
                   <td valign="top" class="searchboxbody">
                     %(colls)s
                   </td>
                  </tr>
                 </tbody>
                </table>
                 """ % {
                   'leading' : leadingtext,
                   'msg_coll' : _("collections"),
                   'colls' : selects,
                 }

        ## thirdly, print search limits, if applicable:
        if action != _("Browse") and pl:
            out += """<table class="searchbox">
                       <thead>
                        <tr>
                          <th class="searchboxheader">
                            %(limitto)s
                          </th>
                        </tr>
                       </thead>
                       <tbody>
                        <tr valign="bottom">
                          <td class="searchboxbody">
                           <input type="text" name="pl" size="%(sizepattern)d" value="%(pl)s" />
                          </td>
                        </tr>
                       </tbody>
                      </table>""" % {
                        'limitto' : _("Limit to:"),
                        'sizepattern' : CFG_WEBSEARCH_ADVANCEDSEARCH_PATTERN_BOX_WIDTH,
                        'pl' : cgi.escape(pl, 1),
                      }

        ## fourthly, print from/until date boxen, if applicable:
        if action == _("Browse") or (d1y == 0 and d1m == 0 and d1d == 0 and d2y == 0 and d2m == 0 and d2d == 0):
            pass # do not need it
        else:
            cell_6_a = self.tmpl_inputdatetype(dt, ln) + self.tmpl_inputdate("d1", ln, d1y, d1m, d1d)
            cell_6_b = self.tmpl_inputdate("d2", ln, d2y, d2m, d2d)
            out += """<table>
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
                          <td class="searchboxbody">%(added_or_modified)s %(date1)s</td>
                          <td class="searchboxbody">%(date2)s</td>
                        </tr>
                       </tbody>
                      </table>""" % {
                        'added' : _("Added/modified since:"),
                        'until' : _("until:"),
                        'added_or_modified': self.tmpl_inputdatetype(dt, ln),
                        'date1' : self.tmpl_inputdate("d1", ln, d1y, d1m, d1d),
                        'date2' : self.tmpl_inputdate("d2", ln, d2y, d2m, d2d),
                      }

        ## fifthly, print Display results box, including sort/rank, formats, etc:
        if action != _("Browse") and aas > -1:

            rgs = []
            for i in [10, 25, 50, 100, 250, 500]:
                if i <= CFG_WEBSEARCH_MAX_RECORDS_IN_GROUPS:
                    rgs.append({ 'value' : i, 'text' : "%d %s" % (i, _("results"))})
            # enrich sort fields list if we are sorting by some MARC tag:
            sort_fields = self._add_mark_to_field(value=sf, fields=sort_fields, ln=ln)

            formatoptions = ""
            formatoptions_label = ""
            if aas != 0 or cc != "HEP":
                # add format options
                formatoptions = '<td class="searchboxbody" align="left">%s</td>' % \
                    (self.tmpl_select(
                     css_class="address",
                     fieldname='of',
                     selected=of,
                     values=self._add_mark_to_field(value=of, fields=CFG_SEARCH_INSPIRE_OUTPUT_FORMATS, chars=3, ln=ln)),)
                formatoptions_label = '<th class="searchboxheader">%s</th>' % (_("Output format:"),)

            # create sort by HTML box:
            out += """<table>
                 <thead>
                  <tr>
                   <th class="searchboxheader">
                    %(sort_by)s
                   </th>
                   <th class="searchboxheader">
                    %(display_res)s
                   </th>
                   %(output_format_label)s
                  </tr>
                 </thead>
                 <tbody>
                  <tr valign="bottom">
                   <td valign="top" class="searchboxbody">
                     %(select_sf)s %(select_so)s %(select_rm)s
                   </td>
                   <td valign="top" class="searchboxbody">
                     %(select_rg)s %(select_sc)s
                   </td>
                   %(select_of)s
                  </tr>
                 </tbody>
                </table>""" % {
                  'sort_by' : _("Sort by:"),
                  'display_res' : _("Display results:"),
                  'output_format_label' : formatoptions_label,
                  'select_sf' : self.tmpl_select(fieldname='sf', values=sort_fields, selected=sf, css_class='address'),
                  'select_so' : self.tmpl_select(fieldname='so', values=[{
                                    'value' : 'a',
                                    'text' : _("asc.")
                                  }, {
                                    'value' : 'd',
                                    'text' : _("desc.")
                                  }], selected=so, css_class='address'),
                  'select_rm' : self.tmpl_select(fieldname='rm', values=ranks, selected=rm, css_class='address'),
                  'select_rg' : self.tmpl_select(fieldname='rg', values=rgs, selected=rg, css_class='address'),
                  'select_sc' : self.tmpl_select(fieldname='sc', values=[{
                                    'value' : 0,
                                    'text' : _("single list")
                                  }, {
                                    'value' : 1,
                                    'text' : _("split by collection")
                                  }], selected=sc, css_class='address'),
                  'select_of' : formatoptions
                }

        ## last but not least, print end of search box:
        out += """</form>"""
        return out


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
                                formatoptions,
                                of='hb'
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

        argd = drop_default_urlargd({'ln': ln, 'aas': 1, 'cc': collection_id, 'sc': CFG_WEBSEARCH_SPLIT_BY_COLLECTION},
                                    self.search_results_default_urlargd)

        # Only add non-default hidden values
        for field, value in argd.items():
            out += self.tmpl_input_hidden(field, value)


        header = _("Search %s records for") % \
                 self.tmpl_nbrecs_info(record_count, "", "")
        header += ':'

        # this is not Jobs, we build normal interface

        ssearchurl = self.build_search_interface_url(c=collection_id, aas=min(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES), ln=ln)

        # replace format options
        formatoptions = self.tmpl_select(
                             fieldname='of',
                             selected=of,
                             values=self._add_mark_to_field(value=of, fields=CFG_SEARCH_INSPIRE_OUTPUT_FORMATS, chars=3, ln=ln),
                             css_class='address')

        out += '''
        <table class="advancedsearch">
         <thead>
          <tr>
           <th class="searchboxheader" colspan="3">%(header)s</th>
          </tr>
         </thead>
         <tbody>
          <tr valign="bottom">
            <td class="searchboxbody" style="white-space: nowrap;">
                %(matchbox_m1)s<input type="text" name="p1" size="%(sizepattern)d" value="" class="advancedsearchfield"/>
            </td>
            <td class="searchboxbody" style="white-space: nowrap;">%(middle_option_1)s</td>
            <td class="searchboxbody">%(andornot_op1)s</td>
          </tr>
          <tr valign="bottom">
            <td class="searchboxbody" style="white-space: nowrap;">
                %(matchbox_m2)s<input type="text" name="p2" size="%(sizepattern)d" value="" class="advancedsearchfield"/>
            </td>
            <td class="searchboxbody">%(middle_option_2)s</td>
            <td class="searchboxbody">%(andornot_op2)s</td>
          </tr>
          <tr valign="bottom">
            <td class="searchboxbody" style="white-space: nowrap;">
                %(matchbox_m3)s<input type="text" name="p3" size="%(sizepattern)d" value="" class="advancedsearchfield"/>
            </td>
            <td class="searchboxbody">%(middle_option_3)s</td>
            <td class="searchboxbody" style="white-space: nowrap;">
              <input class="formbutton" type="submit" name="action_search" value="%(msg_search)s" />
              <input class="formbutton" type="submit" name="action_browse" value="%(msg_browse)s" /></td>
          </tr>
          <tr valign="bottom">
            <td colspan="3" class="searchboxbody" align="right">
              <small>
                <a href="%(siteurl)s/help/easy-search%(langlink)s">%(msg_easy_search)s</a> ::
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
               'msg_browse' : _("Browse"),
               'msg_search_tips' : _("Search Tips"),
               'msg_easy_search' : _("Easy Search"),
        }

        if (searchoptions):
            out += """<table>
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

        out += """<table>
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
                  <table>
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

    def tmpl_record_links(self, recid, ln, sf='', so='d', sp='', rm=''):
        """
          Displays the *More info* and *Find similar* links for a record

        Parameters:

          - 'ln' *string* - The language to display

          - 'recid' *string* - the id of the displayed record
        """

        # load the right message language
        _ = gettext_set_language(ln)

        out = '''<br /><span class="moreinfo">%(detailed)s - %(similar)s</span>''' % {
            'detailed': create_html_link(self.build_search_url(recid=recid, ln=ln),
                                         {},
                                         _("Detailed record"), {'class': "moreinfo"})}

        if CFG_BIBRANK_SHOW_CITATION_LINKS:
            num_timescited = get_cited_by_count(recid)
            if num_timescited:
                out += '''<span class="moreinfo"> - %s </span>''' % \
                       create_html_link(self.build_search_url(p='refersto:recid:%d' % recid,
                                                              sf=sf,
                                                              so=so,
                                                              sp=sp,
                                                              rm=rm,
                                                              ln=ln),
                                        {}, _("Cited by %i records") % num_timescited, {'class': "moreinfo"})

        return out


    def tmpl_print_record_brief_links(self, ln, recID, sf='', so='d', sp='', rm='', display_claim_link=False):
        """Displays links for brief record on-the-fly

        Parameters:

          - 'ln' *string* - The language to display

          - 'recID' *int* - The record id
        """
        from invenio.webcommentadminlib import get_nb_reviews, get_nb_comments

        # load the right message language
        _ = gettext_set_language(ln)

        out = '<div class="moreinfo"><span class="moreinfo">%s</span>' % \
               create_html_link(self.build_search_url(recid=recID, ln=ln),
                                {}, _("Detailed record"),
                                {'class': "moreinfo"})

        if CFG_BIBRANK_SHOW_CITATION_LINKS:
            num_timescited = get_cited_by_count(recID)
            if num_timescited:
                out += '<span class="moreinfo"> - %s</span>' % \
                       create_html_link(self.build_search_url(p="refersto:recid:%d" % recID,
                                                              sf=sf,
                                                              so=so,
                                                              sp=sp,
                                                              rm=rm,
                                                              ln=ln),
                                        {}, num_timescited > 1 and _("Cited by %i records") % num_timescited
                                        or _("Cited by 1 record"),
                                        {'class': "moreinfo"})
            else:
                out += "<!--not showing citations links-->"
        if display_claim_link: #Maybe we want not to show the link to who cannot use id?
            out += '<span class="moreinfo"> - %s</span>' % \
                create_html_link(CFG_SITE_URL + '/person/action', {'claim':'True', 'selection':str(recID)},
                                                                        'Attribute this paper',
                                                                        {'class': "moreinfo"})

        if CFG_WEBCOMMENT_ALLOW_COMMENTS and CFG_WEBSEARCH_SHOW_COMMENT_COUNT:
            num_comments = get_nb_comments(recID, count_deleted=False)
            if num_comments:
                out += '<span class="moreinfo"> - %s</span>' % \
                        create_html_link(CFG_SITE_URL + '/' + CFG_SITE_RECORD + '/' + str(recID)
                        + '/comments?ln=%s' % ln, {}, num_comments > 1 and _("%i comments")
                        % (num_comments) or _("1 comment"),
                        {'class': "moreinfo"})
            else:
                out += "<!--not showing reviews links-->"

        if CFG_WEBCOMMENT_ALLOW_REVIEWS and CFG_WEBSEARCH_SHOW_REVIEW_COUNT:
            num_reviews = get_nb_reviews(recID, count_deleted=False)
            if num_reviews:
                out += '<span class="moreinfo"> - %s</span>' % \
                        create_html_link(CFG_SITE_URL + '/' + CFG_SITE_RECORD + '/' + str(recID)
                        + '/reviews?ln=%s' % ln, {}, num_reviews > 1 and _("%i reviews")
                        % (num_reviews) or _("1 review"), {'class': "moreinfo"})
            else:
                out += "<!--not showing reviews links-->"


        out += '</div>'
        return out

    def tmpl_select_multiple(self, fieldname, values, selected=None, css_id='',
                             css_class='', size=3):
        """
          Produces a generic select box

        Parameters:

          - 'css_class' *string* - optional, a css class to display this select with

          - 'fieldname' *list* - the name of the select box produced

          - 'selected' *list* - which of the values is selected

          - 'values' *list* - the list of values in the select
        """
        if css_class != '':
            class_field = ' class="%s"' % css_class
        else:
            class_field = ''
        if css_id != '':
            id_field = ' id="%s"' % css_id
        else:
            id_field = ''
        out = '<select name="%(fieldname)s" multiple="multiple" size=%(size)d %(class)s %(id)s>' % {
            'fieldname' : fieldname,
            'size' : size,
            'class' : class_field,
            'id' : id_field
            }

        for pair in values:
            if pair.get('selected', False) or pair['value'] in selected:
                flag = ' selected="selected"'
            else:
                flag = ''

            out += '<option value="%(value)s"%(selected)s>%(text)s</option>' % {
                     'value'    : cgi.escape(str(pair['value'])),
                     'selected' : flag,
                     'text'     : cgi.escape(pair['text'])
                   }

        out += """</select>"""
        return out
