## This file is part of Invenio.
## Copyright (C) 2004, 2005, 2006, 2007, 2008, 2010, 2011 CERN.
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

__revision__ = "$Id$"

import os
import re

from invenio.search_engine import perform_request_search
from invenio.bibformat_elements import bfe_INSPIRE_bibtex
from invenio.bibformat_engine import BibFormatObject
from invenio.bibformat import format_record


def Bibtex(parameters, curdir, form, user_info=None):
    """
    This is the function called by the BiblioTools web app.
    It extracts a list of references from a LaTeX file and it converts
    them to BibTex or LaTeX US/EU

    """
    btxt_str = ""

    # get file name and hold it in a string
    dirname = os.path.join(curdir, 'files', 'BibTex_input')
    file_name = ""
    for dummy1, dummy2, myfile in os.walk(dirname):
        file_name = os.path.join(dirname, myfile[0])

    lines = ""
    if (os.path.exists(file_name)):
        input_tex = open(file_name)
        lines = input_tex.read()
        input_tex.close()

    #Get out_format field
    try:
        format_path = os.path.join(curdir, 'OUT_FORMAT')
        filep = open(format_path)
        output_format = filep.read().replace("\n", " ")
        filep.close()
    except:
        output_format = ""
    references = get_references(lines)
    btxt_str = process_references(references, output_format)
    if not btxt_str:
        btxt_str = "No references found. Please try another file."
    btxt_str = ('<div style=\"color:#222222;background:white\"><pre>'
                    + btxt_str + '</pre></div>')
    return btxt_str


def get_references(lines):
    """
    Extract references from LaTeX string (whole file)

    """

    references = []
    #strip TeX comments from text strings, possibly multiline
    cstrip = re.compile(r'(?<!\\)%.*$', re.M)
    lines = cstrip.sub('', lines)

    #extract cites
    cites = re.findall(r'\\cite\s*\{(.*?)\}', lines, re.M | re.DOTALL)

    #extract multiple references separated by commas
    for ref_line in cites:
        ref_list = ref_line.split(',')
        for one_ref in ref_list:
            one_ref = re.sub(r'\s', '', one_ref)
            if not one_ref in references:
                references.append(one_ref)

    return references

def process_references(references, output_format):
    """
    Process a list of references and convert them to a
    given output_format

    """

    btxt_str = '' # result string
    for ref in references:
        index = None
        if re.search(r'.*\:\d{4}\w\w\w?', ref):
            index = 'texkey'
        elif re.search(r'.*\/\d{7}', ref):
            index = 'eprint'
        elif re.search(r'\d{4}\.\d{4}', ref):
            index = 'eprint'
        elif re.search(r'\w\.\w+\.\w', ref):
            index = 'j'
            ref = re.sub(r'\.', ',', ref)
        elif re.search(r'\w\-\w', ref):
            index = 'r'
        if index:
            # hack to match more records
            recid_list = ''
            if index == 'texkey':
                p_to_find = '035__z:' + ref
                recid_list = perform_request_search(p=p_to_find)
                if not recid_list:
                    #try 035__a
                    p_to_find = '035__a:' + ref
                    recid_list = perform_request_search(p=p_to_find)
            else:
                p_to_find = 'find ' + index + ' ' + ref
                recid_list = perform_request_search(p=p_to_find)

            if recid_list:
                bfo = BibFormatObject(recid_list[0])
                if (output_format == 'hlxu' or
                        output_format == 'hlxe' or
                        output_format == 'hx'):
                    formated_rec = format_record(recid_list[0],
                                    output_format, 'en')
                    # update bibitem and cite if they don't match
                    if not re.search('bibitem{' + ref + '}', formated_rec):
                        ref = re.sub(',', '.', ref)
                        if output_format != 'hx':
                            #laTeX
                            formated_rec = re.sub('bibitem{(.*)}',
                                    'bibitem{' + ref + '}', formated_rec)
                            formated_rec = re.sub('cite{(.*)}',
                                            'cite{' + ref + '}', formated_rec)
                        else:
                            #bibtex
                            if not re.search(r'\@article\{' + ref + '}',
                                              formated_rec):
                                formated_rec = re.sub(r'\@article\{(.*)\,',
                                        r'@article{' + ref + ',', formated_rec)
                    btxt_str = btxt_str + formated_rec + '\n'
                else:
                    btxt_str = (btxt_str +
                                bfe_INSPIRE_bibtex.format_element(bfo) + '\n')
            else:
                btxt_str = (btxt_str + '*** Not Found: ' + ref + ' ' +
                            p_to_find + '\n\n')

    return btxt_str
