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
                                                   expected_text="[127, 220, 520, 717, 799, 806, 826]"))
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+j+AA&of=id',
                                                   expected_text="[127, 220, 520, 717, 799, 806, 826]"))
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=journal:Astron.Astrophys.&of=id',
                                                   expected_text="[127, 220, 520, 717, 799, 806, 826]"))

class KBsSubjectTest(unittest.TestCase):
    """ Check the mapping of subject abbreviations """

    def test_results_for_theory(self):
        """ kbs - test results for subject theory-HEP """
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+subject+Theory-HEP&of=id',
                                                   expected_text="[1, 4, 7, 10, 12, 14, 17, 46, 50, 51, 60, 79, 83, 85, 97, 100, 104, 111, 119, 121, 124, 162, 173, 176, 178, 183, 195, 203, 207, 208, 218, 254, 256, 257, 267, 273, 277, 279, 283, 289, 291, 293, 302, 310, 311, 313, 315, 319, 322, 323, 324, 326, 328, 329, 330, 331, 333, 334, 338, 341, 344, 345, 346, 347, 348, 350, 357, 358, 360, 361, 366, 368, 369, 373, 374, 376, 377, 378, 379, 384, 385, 386, 387, 388, 393, 394, 395, 398, 403, 404, 405, 406, 409, 410, 411, 413, 415, 416, 418, 419, 422, 423, 425, 427, 430, 431, 432, 433, 438, 441, 443, 444, 447, 450, 456, 457, 458, 460, 461, 464, 465, 466, 467, 470, 477, 488, 498, 507, 508, 509, 510, 514, 519, 527, 528, 530, 531, 545, 548, 550, 551, 553, 554, 557, 560, 564, 565, 566, 571, 574, 576, 581, 588, 589, 597, 599, 601, 603, 607, 609, 630, 633, 637, 638, 643, 644, 649, 658, 661, 663, 667, 671, 673, 675, 676, 678, 682, 684, 685, 686, 694, 702, 709, 711, 718, 727, 728, 731, 732, 734, 741, 742, 744, 745, 746, 766, 770, 775, 777, 781, 785, 789, 808, 814, 817]"))
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+subject+T&of=id',
                                                   expected_text="[1, 4, 7, 10, 12, 14, 17, 46, 50, 51, 60, 79, 83, 85, 97, 100, 104, 111, 119, 121, 124, 162, 173, 176, 178, 183, 195, 203, 207, 208, 218, 254, 256, 257, 267, 273, 277, 279, 283, 289, 291, 293, 302, 310, 311, 313, 315, 319, 322, 323, 324, 326, 328, 329, 330, 331, 333, 334, 338, 341, 344, 345, 346, 347, 348, 350, 357, 358, 360, 361, 366, 368, 369, 373, 374, 376, 377, 378, 379, 384, 385, 386, 387, 388, 393, 394, 395, 398, 403, 404, 405, 406, 409, 410, 411, 413, 415, 416, 418, 419, 422, 423, 425, 427, 430, 431, 432, 433, 438, 441, 443, 444, 447, 450, 456, 457, 458, 460, 461, 464, 465, 466, 467, 470, 477, 488, 498, 507, 508, 509, 510, 514, 519, 527, 528, 530, 531, 545, 548, 550, 551, 553, 554, 557, 560, 564, 565, 566, 571, 574, 576, 581, 588, 589, 597, 599, 601, 603, 607, 609, 630, 633, 637, 638, 643, 644, 649, 658, 661, 663, 667, 671, 673, 675, 676, 678, 682, 684, 685, 686, 694, 702, 709, 711, 718, 727, 728, 731, 732, 734, 741, 742, 744, 745, 746, 766, 770, 775, 777, 781, 785, 789, 808, 814, 817]"))

class KBsTypeTest(unittest.TestCase):
    """ Check the aliasing of types """

    def test_results_for_(self):
        """ kbs - test results for type thesis """
        """ note that this secretly does collection search, not a type search, as there is no type index """
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+type+thesis&of=id',
                                                   expected_text="[448, 481, 575, 614, 692, 726, 821, 822]"))
        self.assertEqual([], test_web_page_content(CFG_SITE_URL + '/search?p=fin+type+T&of=id',
                                                   expected_text="[448, 481, 575, 614, 692, 726, 821, 822]"))


TEST_SUITE = make_test_suite(
                             KBsJournalTest,
                             KBsSubjectTest,
                             KBsTypeTest,
                            )


if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
