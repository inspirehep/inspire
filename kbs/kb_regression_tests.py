# -*- coding: utf-8 -*-
##
## This file is part of Inspire.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
##
## Inspire is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Inspire is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Inspire; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

# pylint: disable=C0301
# pylint: disable=E1102

"""WebSearch module regression tests."""

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
from invenio.urlutils import same_urls_p

def parse_url(url):
    parts = urlparse.urlparse(url)
    query = cgi.parse_qs(parts[4], True)

    return parts[2].split('/')[1:], query

class KBsJournalTest(unittest.TestCase):
    """ Check the translation of journal names """

    def test_results_for_astrophys(self):
        """ kbs - test results for journal astrophys """
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+j+aap&of=id',
                                                   expected_text="[903, 910, 930]"))
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+j+AA&of=id',
                                                   expected_text="[903, 910, 930]"))
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=journal:Astron.Astrophys.&of=id',
                                                   expected_text="[903, 910, 930]"))

class KBsSubjectTest(unittest.TestCase):
    """ Check the mapping of subject abbreviations """

    def test_results_for_theory(self):
        """ kbs - test results for subject theory-HEP """
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+subject+Theory-HEP&of=id',
                                                   expected_text="[105, 108, 111, 114, 116, 118, 121, 150, 154, 155, 164, 183, 187, 189, 201, 204, 208, 215, 223, 225, 228, 266, 277, 280, 282, 287, 299, 307, 311, 312, 322, 358, 360, 361, 371, 377, 381, 383, 387, 393, 395, 397, 406, 414, 415, 417, 419, 423, 426, 427, 428, 430, 432, 433, 434, 435, 437, 438, 442, 445, 448, 449, 450, 451, 452, 454, 461, 462, 464, 465, 470, 472, 473, 477, 478, 480, 481, 482, 483, 488, 489, 490, 491, 492, 497, 498, 499, 502, 507, 508, 509, 510, 513, 514, 515, 517, 519, 520, 522, 523, 526, 527, 529, 531, 534, 535, 536, 537, 542, 545, 547, 548, 551, 554, 560, 561, 562, 564, 565, 568, 569, 570, 571, 574, 581, 592, 602, 611, 612, 613, 614, 618, 623, 631, 632, 634, 635, 649, 652, 654, 655, 657, 658, 661, 664, 668, 669, 670, 675, 678, 680, 685, 692, 693, 701, 703, 705, 707, 711, 713, 734, 737, 741, 742, 747, 748, 753, 762, 765, 767, 771, 775, 777, 779, 780, 782, 786, 788, 789, 790, 798, 806, 813, 815, 822, 831, 832, 835, 836, 838, 845, 846, 848, 849, 850, 870, 874, 879, 881, 885, 889, 893, 912, 918, 921]"))
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+subject+T&of=id',
                                                   expected_text="[105, 108, 111, 114, 116, 118, 121, 150, 154, 155, 164, 183, 187, 189, 201, 204, 208, 215, 223, 225, 228, 266, 277, 280, 282, 287, 299, 307, 311, 312, 322, 358, 360, 361, 371, 377, 381, 383, 387, 393, 395, 397, 406, 414, 415, 417, 419, 423, 426, 427, 428, 430, 432, 433, 434, 435, 437, 438, 442, 445, 448, 449, 450, 451, 452, 454, 461, 462, 464, 465, 470, 472, 473, 477, 478, 480, 481, 482, 483, 488, 489, 490, 491, 492, 497, 498, 499, 502, 507, 508, 509, 510, 513, 514, 515, 517, 519, 520, 522, 523, 526, 527, 529, 531, 534, 535, 536, 537, 542, 545, 547, 548, 551, 554, 560, 561, 562, 564, 565, 568, 569, 570, 571, 574, 581, 592, 602, 611, 612, 613, 614, 618, 623, 631, 632, 634, 635, 649, 652, 654, 655, 657, 658, 661, 664, 668, 669, 670, 675, 678, 680, 685, 692, 693, 701, 703, 705, 707, 711, 713, 734, 737, 741, 742, 747, 748, 753, 762, 765, 767, 771, 775, 777, 779, 780, 782, 786, 788, 789, 790, 798, 806, 813, 815, 822, 831, 832, 835, 836, 838, 845, 846, 848, 849, 850, 870, 874, 879, 881, 885, 889, 893, 912, 918, 921]"))

class KBsTypeTest(unittest.TestCase):
    """ Check the aliasing of types """

    def test_results_for_(self):
        """ kbs - test results for type thesis """
        """ note that this secretly does collection search, not a type search, as there is no type index """
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+type+thesis&of=id',
                                                   expected_text="[552, 585, 679, 718, 796, 830, 925, 926]"))
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+type+T&of=id',
                                                   expected_text="[552, 585, 679, 718, 796, 830, 925, 926]"))

TEST_SUITE = make_test_suite(
                             KBsJournalTest,
                             KBsSubjectTest,
                             KBsTypeTest,
                            )

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
