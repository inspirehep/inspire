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
from os.path import join, getsize
from invenio.search_engine import perform_request_search
from invenio.bibformat_elements import bfe_INSPIRE_bibtex
from invenio.bibformat_engine import BibFormatObject
from invenio.bibformat import format_record

def Bibtex(parameters, curdir, form, user_info=None):
    """
       This is the function called by the BiblioTools web app. 
       It extracts a list of references from a LaTeX file and it converts them to BibTex or LaTeX US/EU
    """
    btxt_str ="" 
    
    # get file name and hold it in a string
    dirname = os.path.join(curdir, 'files', 'input_elem')
    for r, d, f in os.walk(dirname):
        file_name = os.path.join(dirname, f[0])    
    
    if (os.path.exists(file_name)):
	inputTeX = open(file_name)
    	lines = inputTeX.read()
    	inputTeX.close()
 
    #Get out_format field
    try:
        format_path = os.path.join(curdir, 'OUT_FORMAT')
        fp = open(format_path)
        format = fp.read().replace("\n"," ")
        fp.close()
    except:
        format = ""
    references = get_references(lines)
    btxt_str = process_references(references, format)
    btxt_str = '<div style=\"color:#222222;background:white\"><pre>' + btxt_str + '</pre></div>'
    
    return btxt_str

def get_references(lines):
    """ 
       Extract references from LaTeX string (whole file) 
    """
    references = []
    #remove comments
    #lines = re.sub('(?<!\\\\)%.*?\n', '', lines, re.MULTILINE)
    """ strip TeX comments from text strings, possibly multiline"""
    cstrip = re.compile(r'(?<!\\)%.*$',re.M)
    lines = cstrip.sub('',lines)
    
    #extract cites
    cites = re.findall(r'\\cite\s*\{(.*?)\}', lines, re.M|re.DOTALL) 
    
    #extract multiple references separated by commnas
    for a in cites:
        r = a.split(',')
        for c in r:
            c = re.sub('\s','', c)
            if not c in references:
                references.append(c)

    return references

def process_references(references, format):
    """ 
       Process a list of references and convert them to a given format
    """
     
    btxt_str = '' #result string
    for x in references:
        index = None
        if re.search('.*\:\d{4}\w\w\w?',x) : index = 'texkey'
        elif re.search('.*\/\d{7}',x)      : index = 'eprint'
        elif re.search('\d{4}\.\d{4}',x)   : index = 'eprint'
        elif re.search('\w\.\w+\.\w',x) : 
            index = 'j'
            x = re.sub('\.',',',x)
        elif re.search('\w\-\w',x) : index = 'r'
        if index :
            #hack to match more records   
            if index == 'texkey':
                p_to_find = '035__z: ' + x
            else: 
                p_to_find = 'find ' + index + ' ' + x
            
            recid_list = perform_request_search(p= p_to_find)
            if recid_list:
                bfo = BibFormatObject(recid_list[0])
                if (format == 'hlxu' or format == 'hlxe' or format == 'hx'):
                    formated_rec = format_record(recid_list[0], format, 'en')
                    #update bibitem and cite if they don't match   
                    if not re.search('bibitem{' + x + '}', formated_rec):
                        x = re.sub(',', '.', x)
                        if format != 'hx':
                            #laTek
                            formated_rec = re.sub('bibitem{(.*)}', 'bibitem{' + x + '}', formated_rec)
                            formated_rec = re.sub('cite{(.*)}', 'cite{' + x + '}', formated_rec)
                        else:
                            #bibtex
                            if not re.search('\@article\{' + x + '}', formated_rec):
                                formated_rec = re.sub('\@article\{(.*)\,', '@article{' + x + ',', formated_rec)
                    btxt_str = btxt_str + formated_rec + '\n'
                else:
                    btxt_str = btxt_str + bfe_INSPIRE_bibtex.format_element(bfo) + '\n'
            else:
                btxt_str = btxt_str + '*** Not Found: ' + x + ' ' + p_to_find + '\n\n'
    return btxt_str
