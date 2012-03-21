# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2011 CERN.
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
"""BibFormat element - Prints BibTeX meta-data"""


import re
from invenio.config import CFG_SITE_LANG
from invenio.bibformat_elements import bfe_report_numbers as bfe_repno


def format_element(bfo, width="50"):
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
    note_values_skip = ["* Temporary entry *", "* Brief entry *"]

    width = int(width)
    if width < 30:
        width = 30
    name_width = 21
    value_width = width-name_width
    recID = bfo.control_field('001')

    # Initialize user output
    out = "@"

    def texified(name, value):
        """Closure of format_bibtex_field so we don't keep pasing static data
    
        Saves a little bit of boilerplate.
        """
        return format_bibtex_field(name, value, name_width, value_width)

    #Print entry type
    import invenio.bibformat_elements.bfe_collection as bfe_collection
    collection = bfe_collection.format_element(bfo=bfo, kb="DBCOLLID2BIBTEX")
    if collection == "":
        out += "article"
        collection = "article"
    else:
        out += collection

    out += "{"

    # BibTeX key
    import invenio.bibformat_elements.bfe_texkey as bfe_texkey
    key = bfe_texkey.format_element(bfo, harvmac=False)

#    key = ''
#    for external_keys in bfo.fields("035"):
#        if external_keys['9'] == "SPIRESTeX" and external_keys['z']:
#            key = external_keys['z']
#    if not key:
#        #contruct key in spires like way  need to store an make unique
#        ####FIXME
#        key = bfo.field("100a").split(' ')[0].lower() + ":" + \
#              bfo.field("269c").split('-')[0] + \
#              chr((recID % 26) + 97) + chr(((recID / 26) % 26) + 97)
    out += key + ','

        #If author cannot be found, print a field key=recID
    import invenio.bibformat_elements.bfe_INSPIRE_authors as bfe_authors
    authors = bfe_authors.format_element(bfo=bfo,
                                 limit="5",
                                 separator=" and ",
                                 extension=" and others",
                                 collaboration = "no",
                                 print_links="no",
                                 name_last_first = "yes")
    if authors:

        rx = re.compile('([A-Za-z\,\'\-\s]+?\.)([A-Z][a-z]+)')
        auspace = rx.sub(r'\1 \2', authors, count=0)
        out += texified("author", auspace)

    else:
        out += texified("key", recID)

    # Editors
    import invenio.bibformat_elements.bfe_editors as bfe_editors
    editors = bfe_editors.format_element(bfo=bfo, limit="10",
                                 separator=" and ",
                                 extension="",
                                 print_links="no")
    out += texified("editor", editors)

    # Title
    import invenio.bibformat_elements.bfe_INSPIRE_title_brief as bfe_title
    title = bfe_title.format_element(bfo=bfo, brief="yes")
    out += texified("title", '{' + title + '}')

    # Institution
    if collection ==  "techreport":
        publication_name = bfo.field("269__b")
        out += texified("institution", publication_name)

    # Organization
    if collection == "inproceedings" or collection == "proceedings":
        organization = []
        organization_1 = bfo.field("260__b")
        if organization_1 != "":
            organization.append(organization_1)
        organization_2 = bfo.field("269__b")
        if organization_2 != "":
            organization.append(organization_2)
        out += texified("organization", ". ".join(organization))

    # Publisher
    if collection == "book" or \
           collection == "inproceedings" \
           or collection == "proceedings":
        publishers = []
        import invenio.bibformat_elements.bfe_publisher as bfe_publisher
        publisher = bfe_publisher.format_element(bfo=bfo)
        if publisher != "":
            publishers.append(publisher)
        publication_name = bfo.field("269__b")
        if publication_name != "":
            publishers.append(publication_name)
        imprint_publisher_name = bfo.field("933__b")
        if imprint_publisher_name != "":
            publishers.append(imprint_publisher_name)
        imprint_e_journal__publisher_name = bfo.field("934__b")
        if imprint_e_journal__publisher_name != "":
            publishers.append(imprint_e_journal__publisher_name)

        out += texified("publisher", ". ".join(publishers))

    # Collaboration
    collaborations = []
    for collaboration in bfo.fields("710__g"):
        if collaboration not in collaborations:
            collaborations.append(collaboration)
    out += texified("collaboration", ", ".join(collaborations))

    # School
    if collection == "phdthesis":
        university = bfo.field("502__b")

        out += texified("school", university)

    # Address
    if collection == "book" or \
           collection == "inproceedings" or \
           collection == "proceedings" or \
           collection == "phdthesis" or \
           collection == "techreport":
        addresses = []
        publication_place = bfo.field("260__a")
        if publication_place != "":
            addresses.append(publication_place)
        publication_place_2 = bfo.field("269__a")
        if publication_place_2 != "":
            addresses.append(publication_place_2)
        imprint_publisher_place = bfo.field("933__a")
        if imprint_publisher_place != "":
            addresses.append(imprint_publisher_place)
        imprint_e_journal__publisher_place = bfo.field("934__a")
        if imprint_e_journal__publisher_place != "":
            addresses.append(imprint_e_journal__publisher_place)

        out += texified("address", ". ".join(addresses))

    # Journal
    if collection == "article":
        journals = []
        host_title = bfo.field("773__p")
        if host_title != "":
            journals.append(host_title)
        journal = bfo.field("909C4p")
        if journal != "":
            journals.append(journal)

        out += texified("journal", ". ".join(journals))

    # Number
    if collection == "techreport" or \
           collection == "article":
        numbers = []
        host_number = bfo.field("773__n")
        if host_number != "":
            numbers.append(host_number)
        number = bfo.field("909C4n")
        if number != "":
            numbers.append(number)
        out += texified("number", ". ".join(numbers))

    # Volume
    if collection == "article" or \
           collection == "book":
        volumes = []
        host_volume = bfo.field("773__v")
        if host_volume != "":
            volumes.append(host_volume)
        volume = bfo.field("909C4v")
        if volume != "":
            volumes.append(volume)

        out += texified("volume", ". ".join(volumes))

    # Series
    if collection == "book":
        series = bfo.field("490__a")
        out += texified("series", series)

    # Pages
    if collection == "article" or \
           collection == "inproceedings":
        pages = []
        host_pages = bfo.field("773c")
        if host_pages != "":
            pages.append(host_pages)
            nb_pages = bfo.field("909C4c")
            if nb_pages != "":
                pages.append(nb_pages)
                phys_pagination = bfo.field("300__a")
                if phys_pagination != "":
                    pages.append(phys_pagination)

        out += texified("pages", ". ".join(pages))

    # DOI
    if collection == "article":
        dois = bfo.fields("773__a")
        out += texified("doi", ", ".join(dois))

    # Year
    year = bfo.field("773__y")
    if year == "":
        year = get_year(bfo.field("269__c"))
        if year == "":
            year = get_year(bfo.field("260__c"))
            if year == "":
                year = get_year(bfo.field("502__c"))
                if year == "":
                    year = get_year(bfo.field("909C0y"))
    out += texified("year", year)

    # Note
    note = bfo.field("500__a")
    if note and note not in note_values_skip:
        out += texified("note", note)

    # Eprint (aka arxiv number)
    import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv
    eprints = bfe_arxiv.get_arxiv(bfo, category = "no")
    cats    = bfe_arxiv.get_cats(bfo)
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
        eprints=['']


    # Other report numbers
    out += texified("reportNumber", 
                    bfe_repno.get_report_numbers_formatted(bfo, 
                                                           separator=', ', 
                                                           limit='1000', 
                                                           skip=eprints[0]))

    # Add %%CITATION line
    import invenio.bibformat_elements.bfe_INSPIRE_publi_info_latex as bfe_pil
    import invenio.bibformat_elements.bfe_INSPIRE_publi_coden as bfe_coden
    cite_as = bfe_pil.get_cite_line(arxiv=eprints[0], 
                                    pubnote=bfe_coden.get_coden_formatted(bfo, ','),
                                    repno=bfe_repno.get_report_numbers_formatted(bfo, '', '1'),
                                    bfo=bfo)
    out += texified("SLACcitation", cite_as)

    out +="\n}"
    return out


def format_bibtex_field(name, value, name_width=20, value_width=40):
    """
    Formats a name and value to display as BibTeX field.

    'name_width' is the width of the name of the field (everything before " = " on first line)
    'value_width' is the width of everything after " = ".

    6 empty chars are printed before the name, then the name and then it is filled with spaces to meet
    the required width. Therefore name_width must be > 6 + len(name)

    Then " = " is printed (notice spaces).

    So the total width will be name_width + value_width + len(" = ")
                                                               (3)

    if value is empty string, then return empty string.

    For example format_bibtex_field('author', 'a long value for this record', 13, 15) will
    return :
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

    #format name
    name = "\n      "+name
    name = name.ljust(name_width)

    #format value
    value = '"'+value+'"' #Add quotes to value
    value_lines = []
    last_cut = 0
    cursor = value_width -1 #First line is smaller because of quote
    increase = False
    while cursor < len(value):
        if cursor == last_cut: #Case where word is bigger than the max
                               #number of chars per line
            increase = True
            cursor = last_cut+value_width-1

        if value[cursor] != " " and not increase:
            cursor -= 1
        elif value[cursor] != " " and increase:
            cursor += 1
        else:
            value_lines.append(value[last_cut:cursor])
            last_cut = cursor
            cursor += value_width
            increase = False
    #Take rest of string
    last_line = value[last_cut:]
    if last_line != "":
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
        #Comma not found.
        #Split around any space
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

    #Look for textual month like "Jan" or "sep" or "November" or "novem"
    #Limit to CFG_SITE_LANG as language first (most probable date)
    #Look for short months. Also matches for long months
    short_months = [get_i18n_month_name(month).lower()
                    for month in range(1, 13)] # ["jan","feb","mar",...]
    short_months_pattern = re.compile(r'('+r'|'.join(short_months)+r')',
                                      re.IGNORECASE) # (jan|feb|mar|...)
    result = short_months_pattern.search(date)
    if result is not None:
        try:
            month_nb = short_months.index(result.group().lower()) + 1
            return get_i18n_month_name(month_nb, "short", ln)
        except:
            pass

    #Look for month specified as number in the form 2004/03/08 or 17 02 2004
    #(always take second group of 2 or 1 digits separated by spaces or - etc.)
    month_pattern = re.compile(r'\d([\s]|[-/.,])\
    +(?P<month>(\d){1,2})([\s]|[-/.,])')
    result = month_pattern.search(date)
    if result is not None:
        try:
            month_nb = int(result.group("month"))
            return get_i18n_month_name(month_nb, "short", ln)
        except:
            pass

    #Look for textual month like "Jan" or "sep" or "November" or "novem"
    #Look for the month in each language

    #Retrieve ['en', 'fr', 'de', ...]
    language_list_short = [x[0]
                           for x in language_list_long()]
    for lang in language_list_short: #For each language
        #Look for short months. Also matches for long months
        short_months = [get_i18n_month_name(month, "short", lang).lower()
                        for month in range(1, 13)] # ["jan","feb","mar",...]
        short_months_pattern = re.compile(r'('+r'|'.join(short_months)+r')',
                                          re.IGNORECASE) # (jan|feb|mar|...)
        result = short_months_pattern.search(date)
        if result is not None:
            try:
                month_nb = short_months.index(result.group().lower()) + 1
                return get_i18n_month_name(month_nb, "short", ln)
            except:
                pass

    return default


