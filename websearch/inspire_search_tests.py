# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

# pylint: disable=C0301
# pylint: disable=E1102

"""Tests of SPIRES search syntax in INSPIRE."""

__revision__ = "$Id$"

import unittest
import re
import urlparse, cgi
import sys

if sys.hexversion < 0x2040000:
    # pylint: disable=W0622
    from sets import Set as set
    # pylint: enable=W0622

from mechanize import Browser, LinkNotFoundError

from invenio.config import CFG_SITE_URL, CFG_SITE_NAME, CFG_SITE_LANG
from invenio.testutils import make_test_suite, \
                              run_test_suite, \
                              make_url, make_surl, test_web_page_content, \
                              merge_error_messages
from invenio.search_engine import perform_request_search

def assertInPage(page, text):
    try:
        assert not test_web_page_content(page, expected_text=text)
    except AssertionError:
        print "\n\nWe did not find '" + text + "' in page " + page + "!\n"
        raise AssertionError

def assertLinkToInPage(page, linktarget):
    try:
        assert not test_web_page_content(page, expected_link_target=linktarget)
    except AssertionError:
        print "\n\nWe did not find a link to " + linktarget + " in page " + page + "!\n"
        raise AssertionError

def assertNotInPage(page, text):
    try:
        assert not test_web_page_content(page, unexpected_text=text)
    except AssertionError:
        print "\n\nWe found text '" + text + "' in page " + page + "!\n"
        raise AssertionError

class InspirePagesAvailabilityTest(unittest.TestCase):
    """Check whether Inspire's pages are around."""

    def test_easy_search_page_presence(self):
        """Does easy search exist?"""
        assertInPage(CFG_SITE_URL + '/help/easy-search', "Easy Search")

TEST_SUITE = make_test_suite(InspirePagesAvailabilityTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
