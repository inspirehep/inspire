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


"""DocExtract templates for the web API"""


class Template(object):

    def tmpl_web_form(self):
        """Template for extraction page"""
        return """
        <style type="text/css">
            #extract_form input.urlinput { width: 600px; }
            #extract_form textarea { width: 500px; height: 500px; }
        </style>

        <p>
           With this tool you can simulate the reference extraction
           on INSPIRE.
        </p>
        <p>
           Simply upload a PDF file, insert an arXiv identifier or the URL of
           a PDF file, or paste a reference list into the text box.
        </p>
        <p>
           As a result you get the reference list as it would appear on
           INSPIRE. For long reference lists and cases where we have to get the
           PDF from the URL, it might take some time. If you submit more than
           200 references, the tool will very likely time out.
        </p>
        <p>
            If you check and correct your references before submitting a
            paper to arXiv you help us to make sure that your references will
            appear correctly. INSPIRE so far only recognises references in the
            form of arXiv identifiers, report numbers, journal references
            and DOIs.
        </p>
        <p>
            The documents you provide are immediately deleted after simulating
            the reference extraction.  We do not collect nor retain any
            information.
        </p>

        <form action="" method="post" id="extract_form"
              enctype="multipart/form-data">
            <p>
                <label for="pdf">PDF:</label>
                <input type="file" name="pdf" />
            </p>
            <p>
                <label for="arxiv">arXiv:</label>
                <input type="text" name="arxiv" />
            </p>
            <p>
                <label for="url">URL:</label>
                <input type="text" name="url" class="urlinput" />
            </p>
            <p>
                <label for="txt">Text [please submit your references as plain
                text in ASCII]:</label>
            </p>
            <p>
                <textarea name="txt"></textarea>
            </p>
            <p><input type="submit" /></p>
        </form>
        """

    def tmpl_web_result(self, references_html):
        """Template header for extraction page result"""
        head = """
        <style type="text/css">
            #referenceinp_link_box { display: none; }
        </style>
        """
        foot = """
        <p>
            If one of your references couldn’t be matched to one of the records
            in INSPIRE, it might be due to one of the following reasons:
            <ol>
                <li>
                    The reference couldn’t be recognised. Matching to records on INSPIRE
                    works best when you cite
                    <ul>
                        <li>journal article references such as Nucl.Phys. B869 (2013) 598-607</li>
                        <li>arXiv identifiers, e.g. arXiv:1301.0223 [hep-th]</li>
                        <li>report numbers such as LPT-ENS-12-47</li>
                        <li>DOIs, e.g. 10.1142/S0217751X13500334</li>
                    </ul>
                    You might even want to create your reference list with the
                    help of our <a href="http://inspirehep.net/info/hep/tools/bibliography_generate">
                    LaTeX and BibTeX output formats</a> as this increases the likelihood
                    that the references will be extracted and linked correctly.
                </li>
                <li>
                    We don’t have the paper you’re citing in our database.
                    If it’s of relevance for HEP (please see our <a href="https://inspirehep.net/info/hep/collection-policy">collection policy</a>
                    for details), you can suggest that the paper should be added
                    to INSPIRE by using this <a href="http://www.slac.stanford.edu/spires/hep/additions_form.shtml">form</a>
                </li>
            </ol>
        </p>
        """
        return head + references_html + foot
