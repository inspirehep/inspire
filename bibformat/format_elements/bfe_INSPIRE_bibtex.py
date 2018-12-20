# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2011, 2015, 2018 CERN.
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
BibFormat element - Prints BibTeX meta-data

"""


import cgi
import re

from invenio.bibformat_elements import bfe_report_numbers as bfe_repno
from invenio.config import CFG_SITE_LANG
from invenio.search_engine import get_fieldvalues, search_pattern


def format_element(bfo, width="50", show_abstract=False):
    """
    Prints a full BibTeX record.

    'width' must be >= 30.
    This format element is an example of a large element, which does
    all the formatting by itself

    @param width the width (in number of characters) of the record
    """

    # Values of the note field which should not be displayed.
    # These are typically added programmatically, so stupid string matching is
    # ok. If this assumption changes, turn this into a list of regexps to apply
    # for a match test.
    # note_values_skip = ["* Temporary entry *", "* Brief entry *"]

    width = int(width)
    if width < 30:
        width = 30
    name_width = 21
    value_width = width-name_width
    recID = bfo.control_field('001')

    # Initialize user output
    out = "@"
    erratum_note = ''
    displaycnt = 0

    def texified(name, value):
        """Closure of format_bibtex_field so we don't keep passing static data

        Saves a little bit of boilerplate.
        """
        return format_bibtex_field(name, value, name_width, value_width)

    # map INSPIRE collection types to bibtex entry_type labels

    entry_type = 'article'

    collections = [c.lower() for c in bfo.fields("980__a")]
    if "conferencepaper" in collections:
        entry_type = 'inproceedings'
    elif 'thesis' in collections:
        # Master thesis has to be identified
        if bfo.field("502__b") == 'Master':
            entry_type = 'mastersthesis'
        else:
            entry_type = 'phdthesis'
    elif 'proceedings' in collections:
        entry_type = 'proceedings'
    elif 'book' in collections:
        entry_type = 'book'
    elif 'bookchapter' in collections:
        entry_type = 'incollection'
    elif 'arxiv' in collections:
        entry_type = 'article'

    # exclude certain collections:
    if set(['hepnames', 'journals', 'experiment',
            'jobs', 'conferences', 'institution']) & set(collections):
        nullentry = '@misc{'
        nullentry += texified('key', recID)
        nullentry += texified('note',
                              'not a cited reference in the BibTeX sense')
        nullentry += texified('howpublished', bfo.field('909COo'))
        nullentry = nullentry.rstrip(',') + '\n}'
        return nullentry

    # Irrespective of type, check for complete journal info -> @article
    origentry = entry_type
    for j in bfo.fields("773__"):
        if j.get('p', '') and j.get('v', '') \
           and j.get('c', '') and j.get('y', ''):
            entry_type = 'article'

    out += entry_type + "{"

    # BibTeX key
    import invenio.bibformat_elements.bfe_texkey as bfe_texkey
    key = bfe_texkey.format_element(bfo, harvmac=False)
    out += key + ','

    # KEY
    # if no texkey is found, print a key element with recID
    if not key:
        out += texified("key", recID)

    # Thesis type - special for habilitation
    if entry_type == 'phdthesis':
        thesistype = bfo.field("502__b")
        if thesistype.lower() == "habilitation":
            out += texified("type", "habilitation")

    # Authors
    import invenio.bibformat_elements.bfe_INSPIRE_authors as bfe_authors
    authors = bfe_authors.format_element(bfo=bfo,
                                         limit="10",
                                         separator=" and ",
                                         extension=" and others",
                                         collaboration="no",
                                         print_links="no",
                                         name_last_first="yes",
                                         markup="bibtex")

    # Editors
    import invenio.bibformat_elements.bfe_editors as bfe_editors
    editors = bfe_editors.format_element(bfo=bfo, limit="10",
                                         separator=" and ",
                                         extension=" and others ",
                                         print_links="no")

    spacinginitials = re.compile(r'([A-Z][a-z]{0,1}[}]?\.)(\b|[-\{])')
    if authors:
        # bibtex requires spaces after initials in names (authors/editors)
        # FIXME: use posix [[:upper:]][[:lower:]]{0,1} and re.UNICODE
        # FIXME: do we want A.-B. => A. -B. ?
        authors = spacinginitials.sub(r'\1 \2', authors)
        out += texified("author", authors)

    if editors:
        editors = spacinginitials.sub(r'\1 \2', editors)
        if entry_type == 'article' and not authors:
            # satisfy @article required fields
            out += texified("author", editors)
        else:
            out += texified("editor", editors)

    # Title
    import invenio.bibformat_elements.bfe_INSPIRE_title_brief as bfe_title
    title = bfe_title.format_element(bfo=bfo, brief="yes")
    if title:
        # don't escape "$", assume it's a math delimiter
        title = re.sub(r'(?<!\\)([#&%])', r'\\\1', title)
        title = '{' + title + '}'
        out += texified("title", title)

    # BookTitle
    # ConferencePaper retrieve parent proceeding's title information
    booktitle = ''
    if entry_type == 'inproceedings' or origentry == 'inproceedings':
        import bfe_INSPIRE_inproc_booktitle
        booktitle = bfe_INSPIRE_inproc_booktitle.format_element(bfo)

        if booktitle:
            # $ in booktitle is often a monetary dollar
            bt = re.sub(r'(?<!\\)([#_&%$])', r'\\\1', booktitle)
            out += texified("booktitle", '{' + bt + '}')
    # bookchapter, retrieve book's title and editor info
    if entry_type in ('incollection',):
        # 1) recid:[773__0]  (245 $$a: $$b + editors)
        bookid = bfo.field("773__0")
        # 2) reportnumber:[773__r]  (245 $$a: $$b + editors)
        if not bookid:
            rn = bfo.field("773__r")
            if rn:
                bookids = search_pattern(p='reportnumber:' + rn)
                if bookids:
                    bookid = bookids[0]
        # 3) isbn:[773__z]  (245 $$a: $$b + editors)
        if not bookid:
            isbn = bfo.field("773__z")
            if isbn:
                bookids = search_pattern(p='isbn:' + isbn)
                if bookids:
                    bookid = bookids[0]
        if bookid:
            if not isinstance(bookid, int):
                bookid = int(bookid)
            maintitle = get_fieldvalues(bookid, '245__a')
            if maintitle:
                booktitle = maintitle[0]
                subtitle = get_fieldvalues(bookid, '245__b')
                if subtitle:
                    booktitle += ': ' + subtitle[0]
            # editors
            from invenio.bibformat_engine import BibFormatObject
            bfb = BibFormatObject(bookid)
            editors = bfe_editors.format_element(bfo=bfb,
                                                 limit="10",
                                                 separator=" and ",
                                                 extension=" and others ",
                                                 print_links="no")
            if editors:
                out += texified('editor', editors)
        # 4) [773__x]
        if not booktitle:
            booktitle = bfo.field("773__x")
        if booktitle:
            out += texified("booktitle", booktitle)

    # Institution
    if entry_type == "techreport":
        publication_name = bfo.field("269__b")
        out += texified("institution", publication_name)

    # Organization
    if entry_type in ['inproceedings', 'proceedings']:
        organization = []
        organization_1 = bfo.field("260__b")
        if organization_1:
            organization.append(organization_1)
        organization_2 = bfo.field("269__b")
        if organization_2:
            organization.append(organization_2)
        out += texified("organization", ". ".join(organization))

    # Publisher
    if entry_type in ['incollection', 'book', 'inproceedings', 'proceedings']:
        publishers = []
        import invenio.bibformat_elements.bfe_publisher as bfe_publisher
        publisher = bfe_publisher.format_element(bfo=bfo)
        if publisher:
            publishers.append(publisher)
        publication_name = bfo.field("269__b")
        if publication_name:
            publishers.append(publication_name)
        imprint_publisher_name = bfo.field("933__b")
        if imprint_publisher_name:
            publishers.append(imprint_publisher_name)
        imprint_e_journal__publisher_name = bfo.field("934__b")
        if imprint_e_journal__publisher_name:
            publishers.append(imprint_e_journal__publisher_name)

        out += texified("publisher", ". ".join(publishers))

    # Collaboration
    unique_collabs = []
    for coll in [re.sub(r'(.+)?\s+[Cc]ollaboration', r'\1', c) for c in bfo.fields("710__g")]:
        if coll not in unique_collabs:
            unique_collabs.append(coll)
    out += texified("collaboration", ", ".join(unique_collabs))

    yearset = False
    # School
    if entry_type in ['phdthesis', 'mastersthesis']:
        university = bfo.field("100__u")

        out += texified("school", university)

        thesisyear = bfo.field("502__d")
        if thesisyear:
            yearset = True
            out += texified("year", thesisyear)

    # Address
    if entry_type in ['incollection', 'book', 'inproceedings', 'proceedings',
                      'phdthesis', 'mastersthesis', 'techreport']:
        addresses = []
        publication_place = bfo.field("260__a")
        if publication_place:
            addresses.append(publication_place)
        publication_place_2 = bfo.field("269__a")
        if publication_place_2:
            addresses.append(publication_place_2)
        imprint_publisher_place = bfo.field("933__a")
        if imprint_publisher_place:
            addresses.append(imprint_publisher_place)
        imprint_e_journal__publisher_place = bfo.field("934__a")
        if imprint_e_journal__publisher_place:
            addresses.append(imprint_e_journal__publisher_place)

        out += texified("address", ". ".join(addresses))

        # Pubyear
        if not yearset:
            pubyear = get_year(bfo.field("260__c"))
            if pubyear:
                yearset = True
                out += texified("year", pubyear)

        # URL
        urls = bfo.fields("8564_u")
        # FIXME: use bibdocfile doctype not PLOT or INSPIRE-PUBLIC
        for url in urls:
            if url.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.gif', '.eps')):
                continue
            if url.startswith(('http://inspirehep.net/', 'https://inspirehep.net/')):
                continue

            out += texified("url", url)
            break

    # Journal
    pagesset = False
    if entry_type in ['article', 'inproceedings']:
        journal_infos = bfo.fields("773__")
        for journal_info in journal_infos:
            journal_source = cgi.escape(journal_info.get('p', ''))
            volume = cgi.escape(journal_info.get('v', ''))
            number = cgi.escape(journal_info.get('n', ''))
            pages = cgi.escape(journal_info.get('c', ''))
            erratum = cgi.escape(journal_info.get('m', ''))

            year = cgi.escape(journal_info.get('y', ''))
            if not year:
                year = get_year(bfo.field("269__c"))
                if not year:
                    year = get_year(bfo.field("260__c"))
                    if not year:
                        year = get_year(bfo.field("502__d"))

            str773 = ''
            if journal_source:
                jsub = re.sub(r'\.([A-Z])', r'. \1', journal_source)
                if not (volume or number or pages
                        or bfo.field("0247_2") == 'DOI'):
                    str773 += 'Submitted to: ' + jsub
                else:
                    str773 += jsub
                if displaycnt == 0:
                    out += texified("journal", str773)
            if volume:
                if str773.find("JHEP") > -1:
                    volume = re.sub(r'\d\d(\d\d)', r'\1', volume)
                if displaycnt == 0:
                    out += texified("volume", volume)
                else:
                    str773 += volume
            if year:
                if displaycnt == 0 and not yearset:
                    yearset = True
                    out += texified("year", year)
                else:
                    year = '(' + year + ')'
            if number:
                if displaycnt == 0:
                    out += texified("number", number)
                else:
                    str773 += ',no.' + number
            if pages:
                if displaycnt == 0:
                    pagesset = True
                    out += texified("pages", pages)
                else:
                    str773 += ',' + pages.split('-', 1)[0]

            if str773:
                str773 += year

    # N.B. In cases where there is more than one journal in journals iteration
    # the second pass is usually a cite for a translation or something else to
    # appear in a note. Therefore erratum_note is set to display this data
    # later on.

            displaycnt += 1
            if displaycnt > 1 and str773:
                if erratum.lower() in \
                   ('erratum', 'addendum', 'corrigendum', 'reprint'):
                    str773 = '[%s: %s]' % (erratum, str773,)
                else:
                    str773 = '[' + str773 + ']'
                erratum_note = texified("note", str773)

    # Publication/Journal Name for non-article types
    if entry_type in ['book', 'incollection', 'proceedings']:
        pname = bfo.field("773__p")
        if pname:
            jsub = re.sub(r'\.([A-Z])', r'. \1', pname)
            out += texified("journal", jsub)
        else:
            xstring = bfo.field("773__x")
            if xstring:
                out += texified("journal", xstring)

    # Number
    if entry_type in ['book', 'incollection', 'proceedings', 'techreport']:
        number = bfo.field("773__n")
        if number:
            out += texified("number", number)

    # Volume
    if entry_type in ['book', 'incollection', 'proceedings']:
        volumes = []
        host_volume = bfo.field("773__v")
        if host_volume:
            volumes.append(host_volume)
        volume = bfo.field("490__v")
        if volume:
            volumes.append(volume)

        out += texified("volume", ". ".join(volumes))

    # Series
    if entry_type in ['book', 'incollection', 'proceedings']:
        series = bfo.field("490__a")
        out += texified("series", series)

    # Pages
    if entry_type in ['incollection', 'inproceedings', 'proceedings'] \
       and not pagesset:
        pages = bfo.field("773__c")
        if pages:
            pagesset = True
            out += texified("pages", pages)

    # DOI
    if bfo.field("0247_2") == 'DOI':
        dois = bfo.fields("0247_a") + bfo.fields("773__a")
        out += texified("doi", ", ".join(set(dois)))
    elif bfo.field("0247_2") == 'HDL':
        handles = bfo.fields("0247_a") + bfo.fields("773__a")
        out += texified("handle", ", ".join(set(handles)))

    # Year
    # if there was journal info, we already printed the year
    if not yearset:
        year = bfo.field("773__y")
        if not year:
            year = get_year(bfo.field("269__c"))
            if not year:
                year = get_year(bfo.field("260__c"))
                if not year:
                    year = get_year(bfo.field("502__d"))
        if year:
            yearset = True
            out += texified("year", year)

    # Erratum note stuff here
    out += erratum_note

    # Eprint (aka arxiv number)
    import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv
    eprints = bfe_arxiv.get_arxiv(bfo, category="no")
    cats = bfe_arxiv.get_cats(bfo)
    if eprints:
        eprint = eprints[0]
        if eprint.upper().startswith('ARXIV:'):
            eprint = eprint[6:]

        out += texified("eprint", eprint)
        out += texified("archivePrefix", "arXiv")
        if cats:
            out += texified("primaryClass", cats[0])
    else:
        # No eprints, but we don't want refs to eprints[0] to error out below
        # This makes everything work nicely without a lot of extra gating
        eprints = [None]

    # Other report numbers
    out += texified("reportNumber",
                    bfe_repno.get_report_numbers_formatted(
                        bfo,
                        separator=', ',
                        limit='1000',
                        skip=eprints[0]))

#    if entry_type == "inproceedings" and :
#        pubnote = bfo.field("500__a")
#        out += texified("note", pubnote)

    # ISBN
    if entry_type in ['book', 'proceedings']:
        isbn = bfo.fields("020__a")
        # Inspire frequently has multiple ISBN for different types, e.g.
        # 001242544 020__ $$a9781927763124$$bebook
        # 001242544 020__ $$a9781927763117$$bsoftcover
        # FIXME: normalize ISBN to hyphenated form, see
        #        https://pypi.python.org/pypi/isbnlib/3.5.5

        out += texified('ISBN', ', '.join(isbn))

    # Add %%CITATION line
    import invenio.bibformat_elements.bfe_INSPIRE_publi_info_latex as bfe_pil
    import invenio.bibformat_elements.bfe_INSPIRE_publi_coden as bfe_coden
    cite_as = bfe_pil.get_cite_line(
        arxiv=eprints[0],
        pubnote=bfe_coden.get_coden_formatted(bfo, ','),
        repno=bfe_repno.get_report_numbers_formatted(
            bfo, separator='', limit='1', extension=''),
        bfo=bfo)

    out += texified("SLACcitation", cite_as)

    # optionally display abstract
    # FIXME: abstract requires escaping/quoting
    if show_abstract == "True":
        abstract = bfo.field("520__a")
        if len(abstract) > 1000:
            abstract = abstract[:1000] + '...'
        if abstract:
            out += texified("abstract", '{' + abstract + '}')

    # remove trailing comma and close @entry
    out = out.rstrip(',') + '\n}'

    highbitwarning = r'''
%%% contains utf-8, see: http://inspirehep.net/info/faq/general#utf8
%%% add \usepackage[utf8]{inputenc} to your latex preamble

'''
    # FIXME: transcribe chars above \u007F to TeX sequence ?
    # if re.search(ur'[\u0080-\uFFFF]', out, re.UNICODE):
    #     out = highbitwarning + out
    try:
        out.decode('ascii')
    except UnicodeDecodeError:
        out = highbitwarning + out

    return out


def format_bibtex_field(name, value, name_width=20, value_width=40):
    """
    Formats a name and value to display as BibTeX field.

    'name_width' is the width of the name of the field
    (everything before " = " on first line)
    'value_width' is the width of everything after " = ".

    6 empty chars are printed before the name, then the name and then
    it is filled with spaces to meet the required width. Therefore
    name_width must be > 6 + len(name)

    Then " = " is printed (notice spaces).

    So the total width will be name_width + value_width + len(" = ")
                                                               (3)

    if value is empty string, then return empty string.

    For example:
    format_bibtex_field('author', 'a long value for this record', 13, 15)
    will return :
    >>
    >>      name    = "a long value
    >>                 for this record",
    """
    if name_width < 6 + len(name):
        name_width = 6 + len(name)
    if value_width < 2:
        value_width = 2
    if value is None or value == "":
        return ""

    # format name
    name = "\n      " + name
    name = name.ljust(name_width)

    # format value
    value = '"'+value+'"'  # Add quotes to value
    value_lines = []
    last_cut = 0
    cursor = value_width - 1  # First line is smaller because of quote
    increase = False
    while cursor < len(value):
        if cursor == last_cut:  # Case where word is bigger than the max
                                # number of chars per line
            increase = True
            cursor = last_cut + value_width - 1

        if value[cursor] != " " and not increase:
            cursor -= 1
        elif value[cursor] != " " and increase:
            cursor += 1
        else:
            value_lines.append(value[last_cut:cursor])
            last_cut = cursor
            cursor += value_width
            increase = False
    # Take rest of string
    last_line = value[last_cut:]
    if last_line:
        value_lines.append(last_line)

    tabs = "".ljust(name_width + 2)
    value = ("\n"+tabs).join(value_lines)

    return name + ' = ' + value + ","


def get_name(string):
    """
    Tries to return the last name contained in a string.

    In fact returns the text before any comma in 'string', whith
    spaces removed. If comma not found, get longest word in 'string'

    Behaviour inherited from old GET_NAME function defined as UFD in
    old BibFormat. We need to return the same value, to keep back
    compatibility with already generated BibTeX records.

    Eg: get_name("سtlund, عvind B") returns "سtlund".
    """
    names = string.split(',')

    if len(names) == 1:
        # Comma not found.
        # Split around any space
        longest_name = ""
        words = string.split()
        for word in words:
            if len(word) > len(longest_name):
                longest_name = word
        return longest_name
    else:
        return names[0].replace(" ", "")


def get_year(date, default=""):
    """
    Returns the year from a textual date retrieved from a record

    The returned value is a 4 digits string.
    If year cannot be found, returns 'default'
    Returns first value found.

    @param date the textual date to retrieve the year from
    @param default a default value to return if year not fount
    """
    year_pattern = re.compile(r'\d\d\d\d')
    result = year_pattern.search(date)
    if result is not None:
        return result.group()

    return default


def get_month(date, ln=CFG_SITE_LANG, default=""):
    """
    Returns the year from a textual date retrieved from a record

    The returned value is the 3 letters short month name in language 'ln'
    If year cannot be found, returns 'default'

    @param date the textual date to retrieve the year from
    @param default a default value to return if year not fount
    """
    from invenio.dateutils import get_i18n_month_name
    from invenio.messages import language_list_long

    # Look for textual month like "Jan" or "sep" or "November" or "novem"
    # Limit to CFG_SITE_LANG as language first (most probable date)
    # Look for short months. Also matches for long months
    short_months = [get_i18n_month_name(month).lower()
                    for month in range(1, 13)]  # ["jan","feb","mar",...]
    short_months_pattern = re.compile(r'('+r'|'.join(short_months)+r')',
                                      re.IGNORECASE)  # (jan|feb|mar|...)
    result = short_months_pattern.search(date)
    if result is not None:
        try:
            month_nb = short_months.index(result.group().lower()) + 1
            return get_i18n_month_name(month_nb, "short", ln)
        except:
            pass

    # Look for month specified as number in the form 2004/03/08 or 17 02 2004
    # (always take second group of 2 or 1 digits separated by spaces or - etc.)
    month_pattern = re.compile(r'\d([\s]|[-/.,])\
    +(?P<month>(\d){1,2})([\s]|[-/.,])')
    result = month_pattern.search(date)
    if result is not None:
        try:
            month_nb = int(result.group("month"))
            return get_i18n_month_name(month_nb, "short", ln)
        except:
            pass

    # Look for textual month like "Jan" or "sep" or "November" or "novem"
    # Look for the month in each language

    # Retrieve ['en', 'fr', 'de', ...]
    language_list_short = [x[0]
                           for x in language_list_long()]
    for lang in language_list_short:  # For each language
        # Look for short months. Also matches for long months
        short_months = [get_i18n_month_name(month, "short", lang).lower()
                        for month in range(1, 13)]  # ["jan","feb","mar",...]
        short_months_pattern = re.compile(r'('+r'|'.join(short_months)+r')',
                                          re.IGNORECASE)  # (jan|feb|mar|...)
        result = short_months_pattern.search(date)
        if result is not None:
            try:
                month_nb = short_months.index(result.group().lower()) + 1
                return get_i18n_month_name(month_nb, "short", ln)
            except:
                pass

    return default
