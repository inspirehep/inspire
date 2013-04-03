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


import time
import unittest

from datetime import datetime

import ClientForm
import mechanize
import requests

from invenio.w3c_validator import w3c_validate, \
                                  w3c_errors_to_str, \
                                  CFG_TESTS_REQUIRE_HTML_VALIDATION
from invenio.testutils import InvenioTestUtilsBrowserException, \
                              make_test_suite, \
                              run_test_suite

# Local config
try:
    from config import CFG_SITE_URL, \
                       CFG_SITE_SECURE_URL
except ImportError:
    from invenio.config import CFG_SITE_URL, \
                               CFG_SITE_SECURE_URL

from config import CFG_USERNAME, \
                   CFG_PASSWORD, \
                   CFG_TESTUTILS_VERBOSE


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
        time.sleep(3)


class WebSearchTests(WebTest):

    def test_root(self):
        url = CFG_SITE_URL + '/'
        check_web_page_content(self,
                              url,
                              expected_text=["HEP Search"])

    def test_css(self):
        url = CFG_SITE_URL + '/img/invenio_inspire.css?55f550a194e21b1712a73d2c82d34be4'
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assert_(u'body {' in r.text)

    def test_author_page(self):
        url = CFG_SITE_URL + '/author/S.Mele.1/'
        check_web_page_content(self,
                               url,
                               expected_text=["Mele, Salvatore", "This is me.  Verify my publication list."])

    def test_author_claims_page_anonymous(self):
        url = CFG_SITE_URL + '/person/claimstub?person=S.Mele.1'
        check_web_page_content(self,
                               url,
                               expected_text=["You are going to claim papers"])

    def test_author_claims_page_logged_in(self):
        url = CFG_SITE_URL + '/person/S.Mele.1?open_claim=True'
        check_web_page_content(self,
                               url,
                               expected_text=["Mele, Salvatore", "Muon pair and tau pair production in two photon collisions at LEP"])

    def test_author_claim_action_anonymous(self):
        url = CFG_SITE_URL + '/person/action?repeal=True&selection=700:133386,501369&pid=273672'
        check_web_page_content(self,
                               url,
                               expected_text=["Please review your actions"])

    def test_author_page_recompute(self):
        today_str = datetime.today().strftime('%Y-%m-%d')
        url = CFG_SITE_URL + '/author/S.Mele.1/?recompute=1'
        check_web_page_content(self,
                               url,
                               expected_text=["Mele, Salvatore", "This is me.  Verify my publication list.", "Generated: %s" % today_str])

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
                               expected_text=["Citations summary", "Renowned papers", "</html>"])

    def test_extended_citesummary(self):
        url = CFG_SITE_URL + '/search?ln=en&p=&of=hcs2'
        check_web_page_content(self,
                               url,
                               expected_text=["Citations summary", "self-citation", "Renowned papers", "</html>"])


def build_queries_tests(cls):
    def generic_search(self, query):
        url = CFG_SITE_URL + '/search?ln=en&p=%s&of=hb&action_search=Search' % query
        check_web_page_content(self,
                               url,
                               expected_text=["records found", "</html>"])

    for index, query in enumerate(cls.popular_queries):
        def test(self):
            return generic_search(self, query)
        setattr(cls, 'test_query_%s' % index, test)

    return cls


@build_queries_tests
class PopularQueriesTest(WebTest):
    popular_queries = [
        'find j "Phys.Rev.Lett.,105*"',
        'find ea witten, edward',
        'find a horvathy',
        'find date > today',
        'zhitnitsky, a',
        'author:"J.D.Holt.1" AND collection:citeable',
        'author:"nishinaka, takahiro"',
        'exactauthor:J.Serra.3',
        'find field hep-ex and rank postdoc and region asia',
        'cited:50->30000 year:2011->2012',
    ]


class DetailedRecordTests(WebTest):


    def test_detailed_record(self):
        url = CFG_SITE_URL + '/record/1226366'
        check_web_page_content(self,
                               url,
                               expected_text=["Einstein's Space-Time: An Introduction to Special and General Relativity"])

    def test_hb_format(self):
        url = CFG_SITE_URL + '/search?p=001%3A1226366&of=hb'
        check_web_page_content(self,
                               url,
                               expected_text=["Einstein's Space-Time: An Introduction to Special and General Relativity"])

    def test_references_tab_empty(self):
        url = CFG_SITE_URL + '/record/1226366/references'
        check_web_page_content(self,
                               url,
                               expected_text=["Update these references", "No references were found for that record."])

    def test_references_tab_not_empty(self):
        url = CFG_SITE_URL + '/record/854529/references'
        check_web_page_content(self,
                               url,
                               expected_text=["Update these references", "A Higher Order Perturbative Parton Evolution Toolkit (HOPPET)"])

    def test_references_tab_update_refs(self):
        url = CFG_SITE_URL + '/record/854529/export/hrf'
        check_web_page_content(self,
                               url,
                               expected_text=["A Higher Order Perturbative Parton Evolution Toolkit (HOPPET)"])

    def test_references_bibedit_anonymous(self):
        url = CFG_SITE_URL + '/record/1226366/edit'
        check_web_page_content(self,
                               url,
                               expected_text=["Authorization failure"])


class RestrictedToolsTest(WebTest):
    def test_admin_index(self):
        url = CFG_SITE_URL + '/youraccount/'
        check_web_page_content(self,
                               url,
                               expected_text=["Configure BibFormat"],
                               username=CFG_USERNAME,
                               password=CFG_PASSWORD)

    def test_references_bibedit(self):
        url = CFG_SITE_URL + '/record/1226366/edit'
        check_web_page_content(self,
                               url,
                               expected_text=["Record Editor"],
                               username=CFG_USERNAME,
                               password=CFG_PASSWORD)

class CollectionsTest(WebTest):
    def test_hepnames(self):
        url = CFG_SITE_URL + '/collection/HepNames'
        check_web_page_content(self,
                               url,
                               expected_text=["HEPNames Search"])

    def test_hepnames_search(self):
            url = CFG_SITE_URL + '/search?ln=en&cc=HepNames&ln=en&cc=HepNames&p=Lopez+Paz&action_search=Search&sf=&so=d&rm=&rg=25&sc=0&of=hb'
            check_web_page_content(self,
                                   url,
                                   expected_text=["Lopez Paz, Ivan"])


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


def check_web_page_content(test,
                          url,
                          username="guest",
                          password="",
                          expected_text="</html>",
                          unexpected_text="",
                          expected_link_target=None,
                          expected_link_label=None,
                          require_validate_p=CFG_TESTS_REQUIRE_HTML_VALIDATION):

    error_messages = []
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    try:
        if username == "guest":
            pass
        else:
            browser = mechanize.Browser(factory=_SGMLParserFactory(i_want_broken_xhtml_support=True))
            browser.set_handle_robots(False)
            browser.open(CFG_SITE_SECURE_URL + "/youraccount/login")
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

        browser.open(url)
        url_body = browser.response().read()

        try:
            iter(expected_text)
        except ValueError:
            expected_texts = [expected_text]
        else:
            expected_texts = expected_text

        for cur_expected_text in expected_texts:
            try:
                url_body.index(cur_expected_text)
            except ValueError:
                msg = 'ERROR: Page %s (login %s) does not contain %s,' \
                      ' but contains %s'
                msg = msg % (url, username, cur_expected_text, url_body)
                raise InvenioTestUtilsBrowserException(msg)

        try:
            iter(unexpected_text)
        except ValueError:
            unexpected_texts = [unexpected_text]
        else:
            unexpected_texts = unexpected_text

        for cur_unexpected_text in unexpected_texts:
            try:
                url_body.index(cur_unexpected_text)
                raise InvenioTestUtilsBrowserException(
                      'ERROR: Page %s (login %s) contains %s.' %
                      (url, username, cur_unexpected_text)
                )
            except ValueError:
                pass

        # Test for EXPECTED_LINK_TARGET and EXPECTED_LINK_LABEL:
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

    except mechanize.HTTPError, msg:
        error_messages.append('ERROR: Page %s (login %s) not accessible. %s' %
                              (url, username, msg))
    except InvenioTestUtilsBrowserException, msg:
        error_messages.append('ERROR: Page %s (login %s) led to an error: %s' %
                              (url, username, msg))

    # Logout after tests:
    browser.open(CFG_SITE_SECURE_URL + "/youraccount/logout")
    browser.response().read()
    browser.close()

    if CFG_TESTUTILS_VERBOSE >= 9:
        print "%s check_web_page_content(), tested page `%s', login `%s'," \
              " expected text `%s', errors `%s'." % \
              (time.strftime("%Y-%m-%d %H:%M:%S -->", time.localtime()),
               url, username, expected_text,
               ",".join(error_messages))

    if error_messages:
        test.fail(merge_error_messages(error_messages))

    return error_messages


TEST_SUITE = make_test_suite(WebSearchTests,
                             DetailedRecordTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE, warn_user=True)
