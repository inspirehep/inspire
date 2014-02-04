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

import re
import time
import sys
import traceback
import time
import requests
import xml.dom.minidom
from xml.dom.minidom import parse
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from os import listdir, rename, fdopen
from os.path import join, exists, walk
from tarfile import TarFile
from tempfile import mkdtemp, mkstemp
from urllib import urlretrieve
from zipfile import ZipFile

from invenio.errorlib import register_exception
from invenio.bibrecord import record_add_field, record_xml_output
try:
    from invenio.config import CFG_CONTRASTOUT_DOWNLOADDIR
except ImportError:
    CFG_CONTRASTOUT_DOWNLOADDIR = os.path.join(CFG_TMPSHAREDDIR, "contrast_out")
from invenio.config import (CFG_TMPSHAREDDIR, CFG_ETCDIR,
                            CFG_REFEXTRACT_KBS_OVERRIDE)
from invenio.shellutils import run_shell_command
from invenio.bibtask import task_low_level_submission
from invenio.scoap3utils import (create_logger,
                                 progress_bar,
                                 MissingFFTError,
                                 FileTypeError)
from invenio.contrast_out_utils import find_package_name
from invenio.minidom_utils import (get_value_in_tag,
                                   xml_to_text,
                                   format_arxiv_id)
from invenio.refextract_api import extract_references_from_string_xml

CFG_SCOAP3DTDS_PATH = join(CFG_ETCDIR, 'scoap3dtds')

CFG_ELSEVIER_ART501_PATH = join(CFG_SCOAP3DTDS_PATH, 'ja5_art501.zip')
CFG_ELSEVIER_ART510_PATH = join(CFG_SCOAP3DTDS_PATH, 'ja5_art510.zip')
CFG_ELSEVIER_ART520_PATH = join(CFG_SCOAP3DTDS_PATH, 'ja5_art520.zip')
CFG_ELSEVIER_SI510_PATH = join(CFG_SCOAP3DTDS_PATH, 'si510.zip')
CFG_ELSEVIER_SI520_PATH = join(CFG_SCOAP3DTDS_PATH, 'si520.zip')
CFG_ELSEVIER_JID_MAP = {'PLB': 'Physics letters B',
                        'NUPHB': 'Nuclear Physics B',
                        'CEMGE': 'Chemical Geology',
                        'SOLMAT': 'Solar Energy Materials & Solar Cells',
                        'APCATB': 'Applied Catalysis B: Environmental',
                        'NUMA': 'Journal of Nuclear Materials'}


class ElsevierPackage(object):
    """
    This class is specialized in parsing an Elsevier package
    and creating a SCOAP3-compatible bibupload containing the original
    PDF, XML, and every possible metadata filled in.

    @param package_name: the path to a tar.gz file to expand and parse
    @param path: the actual path of an already expanded package.

    @note: either C{package_name} or C{path} don't have to be passed to the
    constructor, in this case the Elsevier server will be harvested.
    """
    def __init__(self, package_name=None, path=None, CONSYN=False):
        self.package_name = package_name
        self.path = path
        self.found_articles = []
        self._found_issues = []
        self.logger = create_logger("Elsevier")
        self.CONSYN = CONSYN
        if not path and package_name:
            self.logger.info("Got package: %s" % (package_name,))
            self._extract_package()
        elif not path and not package_name:
            print "Starting harves"
            from invenio.contrast_out import ContrastOutConnector
            self.conn = ContrastOutConnector(self.logger)
            self.conn.run()
        self._crawl_elsevier_and_find_main_xml()
        self._crawl_elsevier_and_find_issue_xml()
        self._build_doi_mapping()
        if CONSYN:
            self._build_journal_mappings()

    def _extract_package(self):
        """
        Extract a package in a new temporary directory.
        """
        self.path = mkdtemp(prefix="scoap3_package_", dir=CFG_TMPSHAREDDIR)
        self.logger.debug("Extracting package: %s" % (self.package_name,))
        try:
            if ".tar" in self.package_name:
                TarFile.open(self.package_name).extractall(self.path)
            elif ".zip" in self.package_name:
                ZipFile(self.package_name).extractall(self.path)
            else:
                raise FileTypeError("It's not a TAR or ZIP archive.")
        except Exception, err:
            register_exception(alert_admin=True, prefix="Elsevier error extracting package.")
            self.logger.error("Error extraction package file: %s %s" % (self.path, err))
            print >> sys.stdout, "\nError extracting package file: %s %s" % (self.path, err)


    def _build_journal_mappings(self):
        try:
            kb_loc = CFG_REFEXTRACT_KBS_OVERRIDE['journals']
            kb = open(kb_loc,'r')
            self.journal_mappings = {}
            for line in kb.readlines():
                if line.startswith('#'):
                    continue
                if line.lstrip():
                    key = line.split('---')[0]
                    value = line.split('---')[1]
                    self.journal_mappings[key] = value
        except KeyError:
            return
        


    def _crawl_elsevier_and_find_main_xml(self):
        """
        A package contains several subdirectory corresponding to each article.
        An article is actually identified by the existence of a main.pdf and
        a main.xml in agiven directory.
        """
        self.found_articles = []
        if not self.path and not self.package_name:
            for doc in self.conn.found_articles:
                dirname = doc['xml'].rstrip('/main.xml')
                try:
                    self._normalize_article_dir_with_dtd(dirname)
                    self.found_articles.append(dirname)
                except Exception, err:
                    register_exception()
                    print >> sys.stderr, "ERROR: can't normalize %s: %s" % (dirname, err)
        else:
            def visit(arg, dirname, names):
                if "main.xml" in names and "main.pdf" in names:
                    try:
                        self._normalize_article_dir_with_dtd(dirname)
                        self.found_articles.append(dirname)
                    except Exception, err:
                        register_exception()
                        print >> sys.stderr, "ERROR: can't normalize %s: %s" % (dirname, err)
            walk(self.path, visit, None)

    def _crawl_elsevier_and_find_issue_xml(self):
        """
        Information about the current volume, issue, etc. is available in a file
        called issue.xml that is available in a higher directory.
        """
        self._found_issues = []
        if not self.path and not self.package_name:
            for issue in self.conn._get_issues():
                dirname = issue.rstrip('/issue.xml')
                try:
                    self._normalize_issue_dir_with_dtd(dirname)
                    self._found_issues.append(dirname)
                except Exception, err:
                    register_exception()
                    print >> sys.stderr, "ERROR: can't normalize %s: %s" % (dirname, err)
        else:
            def visit(arg, dirname, names):
                if "issue.xml" in names:
                    try:
                        self._normalize_issue_dir_with_dtd(dirname)
                        self._found_issues.append(dirname)
                    except Exception, err:
                        register_exception()
                        print >> sys.stderr, "ERROR: can't normalize %s: %s" % (dirname, err)
            walk(self.path, visit, None)

    def _normalize_issue_dir_with_dtd(self, path):
        """
        issue.xml from Elsevier assume the existence of a local DTD.
        This procedure install the DTDs next to the issue.xml file
        and normalize it using xmllint in order to resolve all namespaces
        and references.
        """
        if exists(join(path, 'resolved_issue.xml')):
            return
        if 'si510.dtd' in open(join(path, 'issue.xml')).read():
            ZipFile(CFG_ELSEVIER_SI510_PATH).extractall(path)
            for filename in listdir(join(path, 'si510')):
                rename(join(path, 'si510', filename), join(path, filename))
        elif 'si520.dtd' in open(join(path, 'issue.xml')).read():
            ZipFile(CFG_ELSEVIER_SI520_PATH).extractall(path)
            for filename in listdir(join(path, 'si520')):
                rename(join(path, 'si520', filename), join(path, filename))
        else:
            self.logger.error("It looks like the path %s does not contain an si510 or si520 issue.xml file" % path)
            raise ValueError("It looks like the path %s does not contain an si510 or si520 issue.xml file" % path)
        cmd_exit_code, cmd_out, cmd_err = run_shell_command("xmllint --format --loaddtd %s --output %s", (join(path, 'issue.xml'), join(path, 'resolved_issue.xml')))
        if cmd_err:
            self.logger.error("Error in cleaning %s: %s" % (join(path, 'issue.xml'), cmd_err))
            raise ValueError("Error in cleaning %s: %s" % (join(path, 'issue.xml'), cmd_err))


    def _normalize_article_dir_with_dtd(self, path):
        """
        main.xml from Elsevier assume the existence of a local DTD.
        This procedure install the DTDs next to the main.xml file
        and normalize it using xmllint in order to resolve all namespaces
        and references.
        """
        if exists(join(path, 'resolved_main.xml')):
            return
        if 'art520' in open(join(path, 'main.xml')).read():
            ZipFile(CFG_ELSEVIER_ART520_PATH).extractall(path)
            for filename in listdir(join(path, 'art520')):
                rename(join(path, 'art520', filename), join(path, filename))
        elif 'art501' in open(join(path, 'main.xml')).read():
            ZipFile(CFG_ELSEVIER_ART501_PATH).extractall(path)
            for filename in listdir(join(path, 'art501')):
                rename(join(path, 'art501', filename), join(path, filename))
        else:
            self.logger.error("It looks like the path %s does not contain an art520 or art501 main.xml file" % path)
            raise ValueError("It looks like the path %s does not contain an art520 or art501 main.xml file" % path)

        cmd_exit_code, cmd_out, cmd_err = run_shell_command("xmllint --format --loaddtd %s --output %s", (join(path, 'main.xml'), join(path, 'resolved_main.xml')))
        if cmd_err:
            self.logger.error("Error in cleaning %s: %s" % (join(path, 'issue.xml'), cmd_err))
            raise ValueError("Error in cleaning %s: %s" % (join(path, 'main.xml'), cmd_err))

    def _build_doi_mapping(self):
        self._dois = {}
        for path in self._found_issues:
            xml = parse(open(join(path, "resolved_issue.xml")))
            jid = get_value_in_tag(xml, "jid")
            journal = CFG_ELSEVIER_JID_MAP.get(jid, jid)
            issn = get_value_in_tag(xml, "ce:issn")
            volume = get_value_in_tag(xml, "vol-first")
            issue = get_value_in_tag(xml, "iss-first")
            year = get_value_in_tag(xml, "start-date")[:4]
            start_date = get_value_in_tag(xml, "start-date")
            if len(start_date) is 8:
                start_date = time.strftime('%Y-%m-%d', time.strptime(start_date, '%Y%m%d'))
            elif len(start_date) is 6:
                start_date = time.strftime('%Y-%m', time.strptime(start_date, '%Y%m'))

            for included_item in xml.getElementsByTagName("ce:include-item"):
                doi = get_value_in_tag(included_item, "ce:doi")
                first_page = get_value_in_tag(included_item, "ce:first-page")
                last_page = get_value_in_tag(included_item, "ce:last-page")
                self._dois[doi] = (journal, issn, volume, issue, first_page, last_page, year, start_date)


    def _add_references(self,references,rec,doi):
        if self.CONSYN:
            for label, authors, r_doi, issue, page, title, volume, year, textref, ext_link, journal, links, comment, journal_title, publisher in references:
                subfields = []
                if textref and not authors:
                    if label:
                       subfields.append(('o', label))
                    ref_xml = extract_references_from_string_xml(textref)
                    dom = xml.dom.minidom.parseString(ref_xml)
                    fields = dom.getElementsByTagName("datafield")[0].getElementsByTagName("subfield")
                    for field in fields:
                        data = field.firstChild.data
                        code = field.getAttribute("code")
                        if code == 's':
                            try:
                                journal_title = data.split(',')[0]
                                journal_title = journal_title.replace(". ",".")
                                volume = data.split(',')[1]
                                if journal_title[-1] >= 'A' and journal_title[-1] <='Z':
                                    volume = journal_title[-1] + volume
                                    journal_title = journal_title[:-1]
                                try:
                                    journal_title = self.journal_mappings[journal_title].strip()
                                except:
                                    pass
                                try:
                                    page = data.split(',')[2]
                                    subfields.append((code,journal_title+", "+volume+", "+page))
                                except:
                                    subfields.append((code,journal_title+", "+volume))
                            except:
                                pass
                        subfields.append((code,data))
                    if subfields:
                        record_add_field(rec, '999', ind1='C', ind2='5', subfields=subfields)
                elif journal:
                    if doi:
                        subfields.append(('a', r_doi))
                    for author in authors:
                        subfields.append(('h', author))
                    if title:
                        subfields.append(('t', title))
                    if journal_title and volume and page:
                        journal_title = journal_title.replace(". ",".")
                        if journal_title[-1] >= 'A' and journal_title[-1] <='Z':
                            volume = journal_title[-1] + volume
                            journal_title = journal_title[:-1]
                        try:
                            journal_title = self.journal_mappings[journal_title].strip()
                        except:
                            pass
                        subfields.append(('s', journal_title+","+volume+","+page))
                    if ext_link:
                        subfields.append(('r', ext_link))
                    if year:
                        subfields.append(('y', year))
                    if label:
                        subfields.append(('o', label[1:-1]))
                    if subfields:
                        record_add_field(rec, '999', ind1='C', ind2='5', subfields=subfields)
                else:
                    if doi:
                        subfields.append(('a', r_doi))
                    for author in authors:
                        subfields.append(('h', author))
                    if issue:
                        subfields.append(('n', issue))
                    if label:
                       subfields.append(('o', label))
                    if page:
                        subfields.append(('p', page))
                    if ext_link:
                        subfields.append(('r', ext_link))
                    if title and volume and year and page:
                        subfields.append(('s', '%s %s (%s) %s' % (title, volume, year, page)))
                    elif textref:
                        subfields.append(('m', textref))
                    if publisher:
                        subfields.append(('m',publisher))
                    if title:
                        subfields.append(('t', title))
                    if volume:
                        subfields.append(('v', volume))
                    if year:
                        subfields.append(('y', year))
                    if comment:
                        subfields.append(('m', comment))
                    if subfields:
                        record_add_field(rec, '999', ind1='C', ind2='5', subfields=subfields)
        else:
            for label, authors, r_doi, issue, page, title, volume, year, textref, ext_link in references:
                subfields = []
                if doi:
                    subfields.append(('a', r_doi))
                for author in authors:
                    subfields.append(('h', author))
                if issue:
                    subfields.append(('n', issue))
                if label:
                    if not self.CONSYN:
                        subfields.append(('o', label[1:-1]))
                    else:
                        subfields.append(('o', label))
                if page:
                    subfields.append(('p', page))
                if ext_link:
                    subfields.append(('r', ext_link))
                if title and volume and year and page:
                    subfields.append(('s', '%s %s (%s) %s' % (title, volume, year, page)))
                elif textref:
                    subfields.append(('m', textref))
                if title:
                    subfields.append(('t', title))
                if volume:
                    subfields.append(('v', volume))
                if year:
                    subfields.append(('y', year))
                if subfields:
                    record_add_field(rec, '999', ind1='C', ind2='5', subfields=subfields)
            

    def _get_doi(self, xml):
        try:
            return get_value_in_tag(xml, "ce:doi")
        except Exception, err:
            print >> sys.stderr, "Can't find doi"

    def get_title(self, xml):
        try:
            return get_value_in_tag(xml, "ce:title")
        except Exception, err:
            print >> sys.stderr, "Can't find title"

    def get_abstract(self, xml):
        try:
            return get_value_in_tag(xml.getElementsByTagName("ce:abstract-sec")[0], "ce:simple-para")
        except Exception, err:
            print >> sys.stderr, "Can't find abstract"

    def get_keywords(self, xml):
        if self.CONSYN:
            try:
                head = xml.getElementsByTagName("ja:head")[0]
                return [get_value_in_tag(keyword, "ce:text") for keyword in head.getElementsByTagName("ce:keyword")]
            except Exception, err:
                print >> sys.stderr, "Can't find keywords"
        else:
            try:
                return [get_value_in_tag(keyword, "ce:text") for keyword in xml.getElementsByTagName("ce:keyword")]
            except Exception, err:
                print >> sys.stderr, "Can't find keywords"

    def get_copyright(self, xml):
        try:
            return get_value_in_tag(xml, "ce:copyright")
        except Exception, err:
            print >> sys.stderr, "Can't find copyright"

    def get_ref_link(self, xml, name):
        links = xml.getElementsByTagName('ce:inter-ref')
        ret = None
        for link in links:
            if name in link.getAttribute("xlink:href").encode('utf-8'):
                ret = xml_to_text(link).strip()
        return ret

    def get_authors(self, xml):
        authors = []
        for author in xml.getElementsByTagName("ce:author"):
            tmp = {}
            surname = get_value_in_tag(author, "ce:surname")
            if surname:
                tmp["surname"] = surname
            given_name = get_value_in_tag(author, "ce:given-name")
            if given_name:
                tmp["given_name"] = given_name
            initials = get_value_in_tag(author, "ce:initials")
            if initials:
                tmp["initials"] = initials
            orcid = author.getAttribute('orcid').encode('utf-8')
            if orcid:
                tmp["orcid"] = orcid
            emails = author.getElementsByTagName("ce:e-address")
            for email in emails:
                if email.getAttribute("type").encode('utf-8') in ('email', ''):
                    tmp["email"] = xml_to_text(email)
                    break
            cross_refs = author.getElementsByTagName("ce:cross-ref")
            if cross_refs:
                tmp["cross_ref"] = []
                for cross_ref in cross_refs:
                    tmp["cross_ref"].append(cross_ref.getAttribute("refid").encode('utf-8'))
            authors.append(tmp)
        affiliations = {}
        for affiliation in xml.getElementsByTagName("ce:affiliation"):
            aff_id = affiliation.getAttribute("id").encode('utf-8')
            text = re.sub(r'^(\d+\ ?)', "", get_value_in_tag(affiliation, "ce:textfn"))
            affiliations[aff_id] = text
        implicit_affilations = True
        for author in authors:
            matching_ref = [ref for ref in author.get("cross_ref", []) if ref in affiliations]
            if matching_ref:
                implicit_affilations = False
                author["affiliation"] = []
                for i in xrange(0, len(matching_ref)):
                    author["affiliation"].append(affiliations[matching_ref[i]])
        if implicit_affilations and len(affiliations) > 1:
            print >> sys.stderr, "Implicit affiliations are used, but there's more than one affiliation: %s" % affiliations
        if implicit_affilations and len(affiliations) >= 1:
            for author in authors:
                author["affiliation"] = []
                for aff in affiliations.values():
                    author["affiliation"].append(aff)
        return authors

    def get_publication_information(self, xml):
        if self.CONSYN:
            jid = get_value_in_tag(xml, "ja:jid")
            publicationName = get_value_in_tag(xml,"prism:publicationName")
            journal = publicationName.split(",")[0]
            try:
                journal = journal_mappings[journal]
            except:
                pass
            issn = get_value_in_tag(xml, "prism:issn")
            issue = ""#get_value_in_tag(xml, "iss-first")
            volume = publicationName.split(",")[1].lstrip()
            first_page = get_value_in_tag(xml, "prism:startingPage")
            last_page = get_value_in_tag(xml, "prism:endingPage")
            doi = get_value_in_tag(xml,"prism:doi")
            if volume == "Section B":
                volume = "B"
            vol = get_value_in_tag(xml, "prism:volume")
            if vol is "":
                #if volume is not present try to harvest it from elsevier website
                try:
                    session = requests.session()
                    r = session.get("http://dx.doi.org/"+doi)
                    parsed_html = BeautifulSoup(r.text)                
                    info = parsed_html.body.find('p',attrs={'class':'volIssue'}).text.split()
                    for s in info:
                        if unicode(s).find(u'\xe2')>0:
                            first_page = s.rsplit(u'\xe2')[0]
                            last_page = s.rsplit(u'\x93')[1]
                    vol=info[1][:-1]
                except:
                    pass
            if vol:
                volume = volume + vol
            year = xml.getElementsByTagName('ce:copyright')[0].getAttribute("year")
            start_date = ""
            if len(start_date) is 8:
                start_date = time.strftime('%Y-%m-%d', time.strptime(start_date, '%Y%m%d'))
            elif len(start_date) is 6:
                start_date = time.strftime('%Y-%m', time.strptime(start_date, '%Y%m'))                
            doi = get_value_in_tag(xml, "ce:doi")
            
            return (journal, issn, volume, issue, first_page, last_page, year, start_date,doi)
        else:
            doi = self._get_doi(xml)
            try:
                return self._dois[doi] + (doi, )
            except:
                return ('', '', '', '', '', '', '', '', doi)

    def get_references(self, xml):
        references = []
        for reference in xml.getElementsByTagName("ce:bib-reference"):
            label = get_value_in_tag(reference, "ce:label")
            authors = []
            comment = get_value_in_tag(reference, "sb:comment")
            links = []
            for link in reference.getElementsByTagName("ce:inter-ref"):
                links.append(link.firstChild.data)
            for author in reference.getElementsByTagName("sb:author"):
                given_name = get_value_in_tag(author, "ce:given-name")
                surname = get_value_in_tag(author, "ce:surname")
                if given_name:
                    name = "%s, %s" % (surname, given_name)
                else:
                    name = surname
                authors.append(name)
            doi = get_value_in_tag(reference, "ce:doi")
            issue = get_value_in_tag(reference, "sb:issue")
            page = get_value_in_tag(reference, "sb:first-page")
            title = ""
            if len(reference.getElementsByTagName("sb:contribution")) > 0:
                title_container = reference.getElementsByTagName("sb:contribution")[0]
                try:
                    title = title_container.getElementsByTagName("sb:maintitle")[0].firstChild.data
                except:
                    pass
            volume = get_value_in_tag(reference, "sb:volume-nr")
            tmp_issues = reference.getElementsByTagName('sb:issue')
            if tmp_issues:
                year = get_value_in_tag(tmp_issues[0], "sb:date")[:4]
            else:
                year = None
            textref = get_value_in_tag(reference, "ce:textref")
            ext_link = format_arxiv_id(self.get_ref_link(reference, 'arxiv'))
            journal = len(reference.getElementsByTagName("sb:issue"))>0
            journal_title = ""
            if journal:
                journal_title_container = reference.getElementsByTagName("sb:issue")[0]
                journal_title = get_value_in_tag(journal_title_container, "sb:maintitle")
            book = len(reference.getElementsByTagName("sb:book"))>0
            publisher = ""
            if book:
                if len(reference.getElementsByTagName("sb:book-series"))>0:
                    book_series = reference.getElementsByTagName("sb:book-series")[0]                
                    title = title +", "+ get_value_in_tag(book_series, "sb:maintitle") +", "+ get_value_in_tag(book_series, "sb:volume-nr")
                publisher = get_value_in_tag(reference, "sb:publisher")
            if self.CONSYN:
                references.append((label, authors, doi, issue, page, title, volume, year, textref, ext_link, journal, links, comment, journal_title, publisher))
            else:
                references.append((label, authors, doi, issue, page, title, volume, year, textref, ext_link))
        return references

    def get_article_journal(self, xml):
        if get_value_in_tag(xml, "ja:jid") == "":
            return "Nuclear Physics B"
        else:
            return CFG_ELSEVIER_JID_MAP[get_value_in_tag(xml, "ja:jid")]

    def get_article(self, path):
        if path.endswith('.xml'):
            data_file = path
        else:
            data_file = open(join(path, "resolved_main.xml"))
        return parse(data_file)

    def get_elsevier_version(self, name):
        try:
            ret = name[0:5]
            if ret[4] is "A":
                ret = ret + "B"
            return ret
        except Exception, err:
            raise

    def get_pdfa_record(self, path=None):
        xml = self.get_article(path)
        rec = {}
        journal, issn, volume, issue, first_page, last_page, year, start_date, doi = self.get_publication_information(xml)
        record_add_field(rec, '024', ind1='7', subfields=[('a', doi), ('2', 'DOI')])
        try:
            if exists(join(path, 'main_a-2b.pdf')):
                record_add_field(rec, 'FFT', subfields=[('a', join(path, 'main_a-2b.pdf')), ('n', 'main'), ('f', '.pdf;pdfa')])
                self.logger.debug('Adding PDF/A to record: %s' % (doi,))
            elif exists(join(path, 'main.pdf')):
                record_add_field(rec, 'FFT', subfields=[('a', join(path, 'main.pdf'))])
                self.logger.debug('No PDF/A in VTEX package for record: %s' % (doi,))
            else:
                raise MissingFFTError("Record %s doesn't contain PDF file." % (doi,))
        except MissingFFTError, err:
            register_exception(alert_admin=True, prefix="Elsevier paper: %s is missing PDF." % (doi,))
            self.logger.warning("Record %s doesn't contain PDF file." % (doi,))

        return record_xml_output(rec)

    def get_record(self, path=None, no_pdf=False):
        xml_doc = self.get_article(path)
        rec = {}
        title = self.get_title(xml_doc)
        if title:
            record_add_field(rec, '245', subfields=[('a', title)])
        journal, issn, volume, issue, first_page, last_page, year, start_date, doi = self.get_publication_information(xml_doc)
        if not journal:
            journal = self.get_article_journal(xml_doc)
        if start_date:
            record_add_field(rec, '260', subfields=[('c', start_date)])
        else:
            record_add_field(rec, '260', subfields=[('c', time.strftime('%Y-%m-%d'))])
        if doi:
            record_add_field(rec, '024', ind1='7', subfields=[('a', doi), ('2', 'DOI')])
        self.logger.info("Creating record: %s %s" % (path, doi))
        authors = self.get_authors(xml_doc)
        first_author = True
        for author in authors:
            subfields = [('a', '%s, %s' % (author['surname'], author.get('given_name') or author.get('initials')))]
            if 'orcid' in author:
                subfields.append(('j', author['orcid']))
            if 'affiliation' in author:
                for aff in author["affiliation"]:
                    subfields.append(('v', aff))
            if author.get('email'):
                subfields.append(('m', author['email']))
            if first_author:
                record_add_field(rec, '100', subfields=subfields)
                first_author = False
            else:
                record_add_field(rec, '700', subfields=subfields)
        abstract = self.get_abstract(xml_doc)
        if abstract:
            record_add_field(rec, '520', subfields=[('a', abstract), ('9', 'Elsevier')])
        record_add_field(rec, '540', subfields=[('a', 'CC-BY-3.0'), ('u', 'http://creativecommons.org/licenses/by/3.0/')])
        copyright = self.get_copyright(xml_doc)
        if copyright:
            record_add_field(rec, '542', subfields=[('f', copyright)])
        keywords = self.get_keywords(xml_doc)
        if self.CONSYN:
            if keywords:
                for keyword in keywords:
                    record_add_field(rec, '653', ind1='1', subfields=[('a', keyword), ('9', 'author')])
            if first_page and last_page:
                record_add_field(rec, '773', subfields=[('p', journal), ('v', volume), ('n', ''), ('c', '%s-%s' % (first_page, last_page)), ('y', year)])
            else:
                record_add_field(rec, '773', subfields=[('p', journal), ('v', volume), ('n', ''), ('y', year)])
        else:
            if keywords:
                for keyword in keywords:
                    record_add_field(rec, '653', ind1='1', subfields=[('a', keyword), ('9', 'author')])
            record_add_field(rec, '773', subfields=[('p', journal), ('v', volume), ('n', issue), ('c', '%s-%s' % (first_page, last_page)), ('y', year)])
        references = self.get_references(xml_doc)
        self._add_references(references,rec,doi)
        if not no_pdf:
            from invenio.search_engine import search_pattern
            prev_version = search_pattern(p="024__:%s - 980__:deleted" % (doi,))
            from invenio.bibdocfile import BibRecDocs

            add_new_pdf = True

            if prev_version:
                prev_rec = BibRecDocs(prev_version[0])
                try:
                    pdf_path = prev_rec.get_bibdoc('main').get_file(".pdf;pdfa").fullpath
                    record_add_field(rec, 'FFT', subfields=[('a', pdf_path), ('n', 'main'), ('f', '.pdf;pdfa')])
                    add_new_pdf = False
                    self.logger.info('Leaving previously delivered PDF/A for: %s' % (doi,))
                except:
                    pass

            if add_new_pdf:
                try:
                    if exists(join(path, 'main_a-2b.pdf')):
                        record_add_field(rec, 'FFT', subfields=[('a', join(path, 'main_a-2b.pdf')), ('n', 'main'), ('f', '.pdf;pdfa')])
                        self.logger.debug('Adding PDF/A to record: %s' % (doi,))
                    elif exists(join(path, 'main.pdf')):
                        record_add_field(rec, 'FFT', subfields=[('a', join(path, 'main.pdf'))])
                    else:
                        raise MissingFFTError("Record %s doesn't contain PDF file." % (doi,))
                except MissingFFTError, err:
                    register_exception(alert_admin=True, prefix="Elsevier paper: %s is missing PDF." % (doi,))
                    self.logger.warning("Record %s doesn't contain PDF file." % (doi,))

        if not self.CONSYN:
            record_add_field(rec, '583', subfields=[('l', self.get_elsevier_version(find_package_name(path)))])
            record_add_field(rec, 'FFT', subfields=[('a', join(path, 'main.xml'))])
            record_add_field(rec, '980', subfields=[('a', 'SCOAP3'), ('b', 'Elsevier')])
        else:
            record_add_field(rec, '980', subfields=[('a', 'HEP')])
            record_add_field(rec, '980', subfields=[('a', 'Citeable')])
        return record_xml_output(rec)


    def bibupload_it(self):
        print self.found_articles
        if self.found_articles:
            if [x for x in self.found_articles if "vtex" not in x]:
                self.logger.debug("Preparing bibupload.")
                fd, name = mkstemp(suffix='.xml', prefix='bibupload_scoap3_', dir=CFG_TMPSHAREDDIR)
                out = fdopen(fd, 'w')
                print >> out, "<collection>"
                for i, path in enumerate(self.found_articles):
                    if "vtex" not in path:
                        print >> out, self.get_record(path)
                        print path, i + 1, "out of", len(self.found_articles)
                print >> out, "</collection>"
                out.close()
                task_low_level_submission("bibupload", "admin", "-N", "Elsevier", "-i", "-r", name)

            if [x for x in self.found_articles if "vtex" in x]:
            # for VTEX files with PDF/A
                fd_vtex, name_vtex = mkstemp(suffix='.xml', prefix='bibupload_scoap3_', dir=CFG_TMPSHAREDDIR)
                out = fdopen(fd_vtex, 'w')
                print >> out, "<collection>"
                # enumerate remember progres of prevoius one
                for i, path in enumerate(self.found_articles):
                    if "vtex" in path:
                        print >> out, self.get_pdfa_record(path)
                        print path, i + 1, "out of", len(self.found_articles)
                print >> out, "</collection>"
                out.close()
                task_low_level_submission("bibupload", "admin", "-N", "Elsevier:VTEX", "-a", name_vtex)


def main():
    try:
        if len(sys.argv) == 2:
            path_or_package = sys.argv[1]
            if path_or_package.endswith((".tar", ".zip")):
                els = ElsevierPackage(package_name=path_or_package)
            else:
                els = ElsevierPackage(path=path_or_package)
        else:
            els = ElsevierPackage()
        els.bibupload_it()
    except Exception, err:
        register_exception()
        print >> sys.stderr, "ERROR: Exception captured: %s" % err
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

if __name__ == "__main__":
    main()
