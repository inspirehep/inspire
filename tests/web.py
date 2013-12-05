# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2012 CERN.
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


"""WebSearch Test Suite
This suite tests web functionality on INSPIRE"""

import os
import time
import unittest

from datetime import datetime

import ClientForm
import mechanize
import urllib2
import urllib

from invenio.w3c_validator import w3c_validate, \
                                  w3c_errors_to_str, \
                                  CFG_TESTS_REQUIRE_HTML_VALIDATION
from invenio.testutils import InvenioTestUtilsBrowserException, \
                              make_test_suite, \
                              run_test_suite

# Local config
try:
    from config import (CFG_SITE_URL,
                        CFG_SITE_RECORD,
                        CFG_SITE_SECURE_URL,
                        CFG_USERNAME,
                        CFG_PASSWORD)
    CFG_RESTRICTED_TOOLS = True
except ImportError:
    from invenio.config import (CFG_SITE_URL,
                                CFG_SITE_RECORD,
                                CFG_SITE_SECURE_URL)
    CFG_RESTRICTED_TOOLS = False

CFG_TESTUTILS_VERBOSE = 1
CFG_AUTHORTEST_ENABLE = False

def merge_error_messages(error_messages):
    out = ""
    if error_messages:
        out = "\n*** " + "\n*** ".join(error_messages)
    return out


class InvenioConnectorAuthError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return str(self.value)


class WebTest(unittest.TestCase):
    def tearDown(self):
        if 'inspirehep' in CFG_SITE_URL:
            time.sleep(3)


class WebSearchTests(WebTest):

    def test_root(self):
        url = CFG_SITE_URL + '/'
        check_web_page_content(self,
                              url,
                              expected_text=["HEP Search"])

    def test_css(self):
        url = CFG_SITE_URL + '/img/invenio_inspire.css?55f550a194e21b1712a73d2c82d34be4'
        r = urllib2.urlopen(url)
        self.assertEqual(r.code, 200)
        self.assert_(u'body {' in r.read())

    def test_author_page(self):
        url = CFG_SITE_URL + '/author/profile/S.Mele.1/'
        check_web_page_content(self,
                               url,
                               expected_text=["Mele, Salvatore"])

    def test_author_claims_page(self):
        url = CFG_SITE_URL + '/author/claim/S.Mele.1/'
        check_web_page_content(self,
                               url,
                               expected_text=["Mele, Salvatore", "Paper Short Info"])

    def test_author_manage_publications(self):
        url = CFG_SITE_URL + '/author/manage_profile/S.Mele.1'
        check_web_page_content(self,
                               url,
                               expected_text=["Mele, Salvatore", "Manage publications"])

    def test_author_help(self):
        url = CFG_SITE_URL + '/author/help'
        check_web_page_content(self,
                               url,
                               expected_text=["A step by step guide to the author management page"])

    def test_author_search(self):
        url = CFG_SITE_URL + '/author/search'
        check_web_page_content(self,
                               url,
                               expected_text=["Find author clusters by name. e.g: Ellis, J: "])

    def test_author_page_recompute(self):
        today_str = datetime.today().strftime('%Y-%m-%d')
        url = CFG_SITE_URL + '/author/profile/S.Mele.1?recompute=1'
        check_web_page_content(self,
                               url,
                               expected_text=["Mele, Salvatore", "Generated: %s" % today_str])

    def test_empty_search(self):
        url = CFG_SITE_URL + '/search?ln=en&p=&of=hb&action_search=Search'
        check_web_page_content(self,
                               url,
                               expected_text=["records found"])

    def test_advanced_search(self):
        url = CFG_SITE_URL + '/search?ln=en&as=1'
        check_web_page_content(self,
                               url,
                               expected_text=["records found"])

    def test_citesummary(self):
        url = CFG_SITE_URL + '/search?ln=en&p=&of=hcs&action_search=Search'
        check_web_page_content(self,
                               url,
                               expected_text=["Citations summary", "Renowned papers"])

    def test_extended_citesummary(self):
        url = CFG_SITE_URL + '/search?ln=en&p=&of=hcs2'
        check_web_page_content(self,
                               url,
                               expected_text=["Citesummary", "self-citation", "Renowned papers"])


class PopularQueriesTest(WebTest):
    popular_queries = [
        'find j "Phys.Rev.Lett.,105*"',
        'find ea witten, edward',
        'find a horvathy',
        'cited:20->300 year:1976',
    ]

    def test_queries(self):
        for query in self.popular_queries:
            url = CFG_SITE_URL + '/search?ln=en&p=%s&of=hb&action_search=Search'\
                  % (urllib.quote(query),)
            check_web_page_content(self,
                                   url,
                                   expected_text=["records found"])


class FormatExportTest(WebTest):

    def setUp(self):
        self.recid = "303"
        if 'inspirehep' in CFG_SITE_URL:
            self.recid = "1115227"

        self.expected_text = "Quark Elastic Scattering as a Source of High Transverse Momentum Mesons"

        self.formats = [
            'hb', 'hx', 'hm', 'xm', 'xn', 'xd', 'xe',
            'hlxu', 'hlxe', 'hlxh'
        ]

    def test_formats(self):
        for format in self.formats:
            url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD,
                               self.recid, 'export', format)
            check_web_page_content(self,
                                   url,
                                   expected_text=[self.expected_text],
                                   html=format.startswith('h'))


class DetailedRecordTests(WebTest):
    def setUp(self):
        self.hb_record_id = "1"
        self.norefs_record_id = "305"
        self.hasref_record_id = "302"
        self.hascites_record_id = "303"
        if 'inspirehep' in CFG_SITE_URL:
           self.hb_record_id = "212819"
           self.norefs_record_id = "1226366"
           self.hasref_record_id = "332965"
           self.hascites_record_id = "1115227"


    def test_detailed_record(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.hb_record_id)
        check_web_page_content(self,
                               url,
                               expected_text=["Charged Multiplicity of Hadronic Events Containing Heavy Quark Jets"])

    def test_hb_format_search(self):
        url = CFG_SITE_URL + '/search?p=001%%3A%s&of=hb' % (self.hb_record_id,)
        check_web_page_content(self,
                               url,
                               expected_text=["Charged Multiplicity of Hadronic Events Containing Heavy Quark Jets"])

    def test_references_tab_empty(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.norefs_record_id, 'references')
        check_web_page_content(self,
                               url,
                               expected_text=["Update these references", "No references were found for that record."])

    def test_references_tab_not_empty(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.hasref_record_id, 'references')
        check_web_page_content(self,
                               url,
                               expected_text=["Update these references", "Quark Elastic Scattering as a Source of High Transverse Momentum Mesons"])

    def test_references_tab_update_refs(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.hasref_record_id, 'export/hrf')
        check_web_page_content(self,
                               url,
                               expected_text=["Quark Elastic Scattering as a Source of High Transverse Momentum Mesons"])

    def test_references_bibedit_anonymous(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.hb_record_id, 'edit')
        check_web_page_content(self,
                               url,
                               expected_text=["Authorization failure"])

    def test_citations_tab(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.hascites_record_id, 'citations')
        check_web_page_content(self,
                               url,
                               expected_text=["Why multi-jet studies?"])


class RestrictedToolsTest(WebTest):

    def setUp(self):
        pass

    if CFG_RESTRICTED_TOOLS:
        def test_admin_index(self):
            url = CFG_SITE_SECURE_URL + '/youraccount/'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Configure BibFormat"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_references_bibedit(self):
            url = CFG_SITE_SECURE_URL + '/record/123/edit'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Record Editor"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_multiedit(self):
            url = CFG_SITE_SECURE_URL + '/record/multiedit/'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Record Editor"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_info_space_manager(self):
            url = CFG_SITE_SECURE_URL + '/info/manage'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Info Space Manager"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_manage_format_templates(self):
            url = CFG_SITE_SECURE_URL + '/admin/bibformat/bibformatadmin.py/format_templates_manage'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Manage Format Templates"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_edit_template_html_brief(self):
            url = CFG_SITE_SECURE_URL + '/admin/bibformat/bibformatadmin.py/format_template_show?bft=Default_HTML_brief.bft'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Format Template Default HTML brief"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_edit_template_html_detailed(self):
            url = CFG_SITE_SECURE_URL + '/admin/bibformat/bibformatadmin.py/format_template_show?bft=Default_HTML_detailed.bft'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Format Template Default HTML detailed"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_manage_kb(self):
            url = CFG_SITE_SECURE_URL + '/kb'
            check_web_page_content(self,
                                   url,
                                   expected_text=["BibKnowledge Admin", "CODENS", "PDG", "SUBJECT"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_kb_codens(self):
            url = CFG_SITE_SECURE_URL + '/kb?kb=6&search='
            check_web_page_content(self,
                                   url,
                                   expected_text=["Knowledge Base CODENS", "APPOA"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_bibindex_indexes_list(self):
            url = CFG_SITE_SECURE_URL + '/admin/bibindex/bibindexadmin.py'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Manage Indexes", "global", "year"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_bibindex_edit_index(self):
            url = CFG_SITE_SECURE_URL + '/admin/bibindex/bibindexadmin.py/editindex?idxID=1'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Edit Index", "global"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_bibrank(self):
            url = CFG_SITE_SECURE_URL + '/admin/bibrank/bibrankadmin.py'
            check_web_page_content(self,
                                   url,
                                   expected_text=["BibRank Admin Interface", "citation", "inst_papers", "selfcites"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_oaiharvest(self):
            url = CFG_SITE_SECURE_URL + '/admin/oaiharvest/oaiharvestadmin.py'
            check_web_page_content(self,
                                   url,
                                   expected_text=["OAI Harvest Admin Interface"],
                                   unexpected_text=["FAILED", "DONE WITH ERRORS"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_oairepository(self):
            url = CFG_SITE_SECURE_URL + '/admin/bibrank/bibrankadmin.py'
            check_web_page_content(self,
                                   url,
                                   expected_text=["BibRank Admin Interface", "citation", "inst_papers", "selfcites"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

        def test_query_history(self):
            url = CFG_SITE_SECURE_URL + '/search?p=001%3A50'
            check_web_page_content(self,
                                   url,
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)
            url = CFG_SITE_SECURE_URL + '/youralerts/display'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Your Searches", "001:50"],
                                   username=CFG_USERNAME,
                                   password=CFG_PASSWORD)

class CollectionsTest(WebTest):

    def setUp(self):
        self.hepnames_id = "62"
        self.inst_id = "306"
        self.conf_id = "4"
        self.jobs_id = "102"
        self.exp_id = "41"
        self.journal_id = "315"
        if 'inspirehep' in CFG_SITE_URL:
           self.hepnames_id = "1002589"
           self.inst_id = "903206"
           self.conf_id = "974612"
           self.jobs_id = "1088203"
           self.exp_id = "1110662"
           self.journal_id = "1214495"


    def test_hepnames_home(self):
        url = CFG_SITE_URL + '/collection/HepNames'
        check_web_page_content(self,
                               url,
                               expected_text=["HEPNames Search"])

    def test_hepnames_detailed(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.hepnames_id)
        check_web_page_content(self,
                               url,
                               expected_text=["Josef Kluson"])

    def test_hepnames_search(self):
            url = CFG_SITE_URL + '/search?ln=en&cc=HepNames&p=Steven+Chu&action_search=Search&sf=&so=d&rm=&rg=25&sc=0&of=hb'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Steven Chu"])

    def test_institutions_home(self):
        url = CFG_SITE_URL + '/collection/Institutions'
        check_web_page_content(self,
                               url,
                               expected_text=["Institutions Search"])

    def test_institutions_detailed(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.inst_id)
        check_web_page_content(self,
                               url,
                               expected_text=["SLAC"])

    def test_institutions_search(self):
            url = CFG_SITE_URL + '/search?ln=no&p=find+address+menlo+park&cc=Institutions'
            check_web_page_content(self,
                                   url,
                                   expected_text=["SLAC", "SLAC National Accelerator Laboratory"])

    def test_conferences_home(self):
        url = CFG_SITE_URL + '/collection/Conferences'
        check_web_page_content(self,
                               url,
                               expected_text=["Conferences Search"])

    def test_conferences_detailed(self):
        url = os.path.join(CFG_SITE_URL, CFG_SITE_RECORD, self.conf_id)
        check_web_page_content(self,
                               url,
                               expected_text=["Workshop on Nuclear Physics at JHF"])

    def test_conferences_search(self):
            url = CFG_SITE_URL + '/search?ln=no&p=Las+Vegas&cc=Conferences'
            check_web_page_content(self,
                                   url,
                                   expected_text=["RPSD, IRD, BMD 2010 Joint Topical Meeting"])

    def test_conferences_submit(self):
        url = CFG_SITE_URL + '/submit?doctype=CONFSUBMIT&act=SBI&comboCONFSUBMIT=CONF'
        check_web_page_content(self,
                               url,
                               expected_text=["Submit a Conference"])

    def test_jobs_home(self):
        url = CFG_SITE_URL + '/collection/Jobs'
        check_web_page_content(self,
                               url,
                               expected_text=["Jobs Search"])

    def test_jobs_detailed(self):
        url = CFG_SITE_URL + '/record/' + self.jobs_id
        check_web_page_content(self,
                               url,
                               expected_text=["Proton spin polarizabilites"])

    def test_jobs_search(self):
            url = CFG_SITE_URL + '/search?p1=&op1=a&p2=&action_search=Search&cc=Jobs'
            check_web_page_content(self,
                                   url,
                                   expected_text=["records found"],
                                   unexpected_text=["0 records found"])

    def test_jobs_submit(self):
        url = CFG_SITE_URL + '/submit?doctype=JOBSUBMIT&act=SBI&comboJOBSUBMIT=JOB'
        check_web_page_content(self,
                               url,
                               expected_text=["Submit a Job Vacancy"])

    def test_jobs_rss(self):
        url = CFG_SITE_URL + '/rss?cc=Jobs&ln=en'
        check_web_page_content(self,
                               url,
                               expected_text=["<rss", "<item>", "<title>",
                                              "</title>", "</item>", "</rss>"],
                               html=False)

    def test_experiments_home(self):
        url = CFG_SITE_URL + '/collection/Experiments'
        check_web_page_content(self,
                               url,
                               expected_text=["Experiments Search"])

    def test_experiments_detailed(self):
        url = CFG_SITE_URL + '/record/' + self.exp_id
        check_web_page_content(self,
                               url,
                               expected_text=["CERN-ISOLDE"])

    def test_experiments_search(self):
            url = CFG_SITE_URL + '/search?p1=&op1=a&p2=&action_search=Search&cc=Experiments'
            check_web_page_content(self,
                                   url,
                                   expected_text=["records found"],
                                   unexpected_text=["0 records found"])

    def test_journals_home(self):
        url = CFG_SITE_URL + '/collection/Journals'
        check_web_page_content(self,
                               url,
                               expected_text=["Journals Search"])

    def test_journals_detailed(self):
        url = CFG_SITE_URL + '/record/' + self.journal_id
        check_web_page_content(self,
                               url,
                               expected_text=["Physical Review Letters"])

    def test_journals_search(self):
            url = CFG_SITE_URL + '/search?ln=en&cc=Journals&p=Physical+Review+Letters&action_search=Search&sf=&so=d&rm=&rg=25&sc=0&of=hb'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Physical Review Letters"])


class OtherPagesTests(WebTest):
    def test_help(self):
        url = CFG_SITE_URL + '/help/'
        check_web_page_content(self,
                               url,
                               expected_text=["Citation Metrics"])

    def test_easy_search(self):
        url = CFG_SITE_URL + '/help/easy-search'
        check_web_page_content(self,
                               url,
                               expected_text=["Easy Search"])

    def test_bibtools(self):
        url = CFG_SITE_URL + '/submit?ln=en&doctype=bibtex&act=SBI'
        check_web_page_content(self,
                               url,
                               expected_text=["BiblioTools: Generating Your Bibliography"])
    if 'inspirehep' in CFG_SITE_URL:

        def test_terms_of_use(self):
            url = CFG_SITE_URL + '/info/general/terms-of-use'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Terms of Use"])

        def test_privacy_policy(self):
            url = CFG_SITE_URL + '/info/general/privacy-policy'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Privacy Policy"])


class _SGMLParserFactory(mechanize.DefaultFactory):
    def __init__(self, i_want_broken_xhtml_support=False):
        forms_factory = mechanize.FormsFactory(
            form_parser_class=ClientForm.XHTMLCompatibleFormParser)
        mechanize.Factory.__init__(
            self,
            forms_factory=forms_factory,
            links_factory=mechanize.LinksFactory(),
            title_factory=mechanize.TitleFactory(),
            response_type_finder=mechanize._html.ResponseTypeFinder(
                allow_xhtml=i_want_broken_xhtml_support),
        )


def login(browser, username, password):
    url = CFG_SITE_SECURE_URL + "/youraccount/login"
    try:
        browser.open(url)
    except mechanize.HTTPError, msg:
        msg = 'ERROR: Page %s (login %s) not accessible. %s' % \
                                                           (url, username, msg)
        raise InvenioTestUtilsBrowserException(msg)

    browser.select_form(nr=0)
    browser.form['p_un'] = username
    browser.form['p_pw'] = password
    browser.submit()

    username_account_page_body = browser.response().read()
    try:
        msg = "You are logged in as %s" % username
        username_account_page_body.index(msg)
    except ValueError:
        msg = 'ERROR: Cannot login as %s.' % username
        raise InvenioTestUtilsBrowserException(msg)

def check_web_page_content(test,
                           url,
                           username="guest",
                           password="",
                           expected_text=[],
                           unexpected_text=[],
                           expected_link_target=[],
                           expected_link_label=[],
                           require_validate_p=CFG_TESTS_REQUIRE_HTML_VALIDATION,
                           html=True,
                           browser_cache={}):
    try:
        browser = read_url(url, username, password)
    except InvenioTestUtilsBrowserException, msg:
        test.fail('ERROR: Page %s (login %s) led to an error: %s' %
                                                          (url, username, msg))

    url_body = browser.response().read()

    # Checks for exepected text
    try:
        iter(expected_text)
    except ValueError:
        expected_texts = [expected_text]
    else:
        expected_texts = expected_text

    if html:
        expected_text.append('</html>')

    for cur_expected_text in expected_texts:
        try:
            url_body.index(cur_expected_text)
        except ValueError:
            msg = 'ERROR: Page %s (login %s) does not contain %s,' \
                  ' but contains %s'
            msg = msg % (url, username, cur_expected_text, url_body)
            test.fail(msg)

    # Checks for unexepected text
    try:
        iter(unexpected_text)
    except ValueError:
        unexpected_texts = [unexpected_text]
    else:
        unexpected_texts = unexpected_text

    for cur_unexpected_text in unexpected_texts:
        try:
            url_body.index(cur_unexpected_text)
            msg = 'ERROR: Page %s (login %s) contains %s.' % \
                                           (url, username, cur_unexpected_text)
            test.fail(msg)
        except ValueError:
            pass

    # Test for expected_link_target and expected_link_label:
    if expected_link_target or expected_link_label:
        # At first normalize expected_link_target and expected_link_label
        try:
            iter(expected_link_target)
        except ValueError:
            expected_link_targets = [expected_link_target]
        else:
            expected_link_targets = expected_link_target

        try:
            iter(expected_link_label)
        except ValueError:
            expected_link_labels = [expected_link_label]
        else:
            expected_link_labels = expected_link_label

        # and then test
        for cur_expected_link_target, cur_expected_link_label \
                       in zip(expected_link_targets, expected_link_labels):
            try:
                browser.find_link(url=cur_expected_link_target,
                                  text=cur_expected_link_label)
            except mechanize.LinkNotFoundError:
                raise InvenioTestUtilsBrowserException(
                      'ERROR: Page %s (login %s) does not contain link'
                      ' to %s entitled %s.' %
                      (url, username, cur_expected_link_target,
                       cur_expected_link_label)
                )

    # Test for validation if required
    if require_validate_p:
        valid_p, errors, warnings = w3c_validate(url_body)
        if not valid_p:
            error_text = 'ERROR: Page %s (login %s) does not' \
                         ' validate:\n %s' % \
                         (url, username,
                          w3c_errors_to_str(errors, warnings))
            raise InvenioTestUtilsBrowserException(error_text)

    if CFG_TESTUTILS_VERBOSE >= 9:
        print "%s check_web_page_content(), tested page `%s', login `%s'," \
              " expected text `%s', unexpected text `%s'." % \
              (time.strftime("%Y-%m-%d %H:%M:%S -->", time.localtime()),
               url, username, expected_text, unexpected_text)

    return browser


class LoggedInBrowser(mechanize.Browser):
    def __init__(self, username, password, *args, **kwargs):
        # super(LoggedInBrowser, self).__init__(*args, **kwargs)
        mechanize.Browser.__init__(self, *args, **kwargs)
        self.set_handle_robots(False)
        login(self, username, password)

    def __del__(self):
        # Logout after tests:
        self.open(CFG_SITE_SECURE_URL + "/youraccount/logout")
        self.response().read()
        self.close()



def read_url(url,
             username="guest",
             password="",
             browser_cache={}):

    if (username, password) in browser_cache:
        browser = browser_cache[(username, password)]
    else:
        # browser = mechanize.Browser(factory=_SGMLParserFactory(i_want_broken_xhtml_support=True))
        if username == "guest":
            browser = mechanize.Browser()
        else:
            browser = LoggedInBrowser(username, password)
        browser.set_handle_robots(False)

    try:
        browser.open(url)
    except mechanize.HTTPError, msg:
        msg = 'ERROR: Page %s (login %s) not accessible. %s' % \
                                                           (url, username, msg)
        raise InvenioTestUtilsBrowserException(msg)

    return browser


TEST_SUITE = make_test_suite(WebSearchTests,
                             DetailedRecordTests,
                             CollectionsTest,
                             PopularQueriesTest,
                             OtherPagesTests,
                             FormatExportTest,
                             RestrictedToolsTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE, warn_user=True)
