#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
For JCAP, JHEP and J.Stat.Mech. the volume counting is repeated per year.
For a unique PubNote both year and volume are needed.
Sometimes these two numbers are called volume and issue.
Since SPIRES could handle only one number we made up an artifical volume YYMM.

There are several problems with metadata we receive and how they are parsed.
As a result we have in references stuff like
JHEP,2016,123
JHEP,1616,123
neither contains the necessary volume information.
In addition some references contain artid-artid:
JHEP,2016,123-123

This plugin tries to correct the PubNote based on additional info in the reference:
DOI
reportnumber
raw pubnote in the raw-reference
ambigous INSPIRE search (journal, year, artid) + confirmation by author or title

Clear cases will be corrected automatically, others flagged.
"""

import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_record
from invenio.search_engine import get_fieldvalues

JOURNALS = ['JCAP', 'JHEP', 'J.Stat.Mech.']

def parse_ref(markfield):
    """
    Read subfields of a markfield representing a reference 999C5
    Return a dict with text line, curator-tag, $$0, $$r, $$s mark tags, DOI and text fields hmxt
    """

    reference_dict = {'subfield_0': '', 'doi': '', 'repno': '', 'subfield_pbn': '',
        'subfields_text': '', 'position_pbn': -1, 'mark_line': '', 'curator': ''}

    if markfield[1] == 'C' and markfield[2] == '5':
        for subfield_position, (code, value) in enumerate(markfield[0]):
            reference_dict['mark_line'] += '$$%s%s' % (code, value)
            if code == '0':
                reference_dict['subfield_0'] = value
            elif code in ['h', 'm', 'x', 't']:
                reference_dict['subfields_text'] = '%s $$%s%s' % (reference_dict['subfields_text'], code, value)
            elif code == 'a' and value.startswith('doi:'):
                reference_dict['doi'] = value[4:]
            elif code == '9' and value == 'CURATOR':
                reference_dict['curator'] = 'C'
            elif code == 'r':
                reference_dict['repno'] = value.split(' ')[0]
            elif code == 's':
                # in case of more than one $$s subfield, pick one that is interesting
                if not reference_dict['subfield_pbn'].split(',')[0] in JOURNALS:
                    reference_dict['position_pbn'] = subfield_position
                    reference_dict['subfield_pbn'] = value

    return reference_dict

def parse_pbn(reference):
    """ split $$s subfield in journal, volume and artid """
    try:
        (journal, volume, artid) = reference['subfield_pbn'].split(',')
    except (KeyError, ValueError):
        journal = ''
        volume = ''
        artid = ''

    # fix artid
    page_range = artid.split('-')
    if len(page_range) == 2:
        if page_range[0] == '1':
            # this looks like number of pages, not page-numbers
            artid = ''
        if page_range[0] == page_range[1]:
            # this looks like artid-artid
            artid = page_range[0]
    if 0 < len(artid) < 3:
        # add leading 0s
        try:
            artid = '%03i' % int(artid)
        except ValueError:
            pass
    return journal, volume, artid

def derive_year_from_volume(volume):
    """ volume should be YYMM """
    try:
        year = volume[:2]
        if int(year) < 50: # I hope this is not necessary after 2050, no JHEP articles before 1950
            year = '20%s' % year
        else:
            year = '19%s' % year
    except (KeyError, ValueError):
        year = volume
    return year

def volume_looks_wrong(volume):
    """
    Volume should be YYMM; true if
    month (MM) > 12 or
    YYYY is more likely, i.e. 2016
    WARNING: from year 2020 on this will flag correct YYMM
    """
    try:
        wrong_yymm = int(volume[-2:]) > 12
    except (KeyError, ValueError):
        wrong_yymm = False
    wrong_yymm = wrong_yymm or volume.startswith('20')
    return wrong_yymm

def confirm_by_collaboration(text, candidate):
    """
    Confirmed if all collaborations are in text
    Return reason - result of confirmation analysis
    """
    ok = 0
    confirmation_reason = ''

    collaborations = get_fieldvalues(candidate, '710__g')
    if len(collaborations) > 1:
        for collaboration in collaborations:
            if collaboration.lower() in text:
                ok += 1
        if ok == len(collaborations):
            confirmation_reason = 'C %s/%s' % (ok, len(collaborations))
    return confirmation_reason

def confirm_by_authors(text, candidate):
    """
    Confirmed if more than 60% of the first 4 authors last-names are in text
    Return reason - result of confirmation analysis
    If the cited record has more than 8 authors most likely only the first is given in the reference (et.al.)
    """
    authors = get_fieldvalues(candidate, '100__a') + get_fieldvalues(candidate, '700__a')
    if len(authors) > 8:
        confirmation_reason = 'Too many authors'
    else:
        total = 0
        ok = 0
        for author in authors[:3]:
            total += 1
            lastname = author.split(',')[0]
            if len(lastname) > 4:
                if lastname.lower() in text:
                    # this is robust, but 'Li, Chiang' matches 'Lindner, Alex', so restrict it to longer names
                    ok += 1
            else:
                if re.search(r'(?i)(?<!\w)%s(?!\w)' % lastname, text):
                    ok += 1
        if total and  ok / float(total) > 0.6:
            confirmation_reason = 'A  %s/%s(%s)  %s' % (ok, total, len(authors), authors[0])
        else:
            confirmation_reason = ''
    return confirmation_reason

def confirm_by_title(text, candidate):
    """
    Confirmed if all good title words are in text, at least 2 good words
    Return reason - result of confirmation analysis
    """
    titles = get_fieldvalues(candidate, '245__a')
    title_words = []
    if titles:
        for word in titles[0].split(' '):
            if len(word) < 4 or re.search(r'\W', word):
                continue
            title_words.append(word.lower())

    ok = 0
    total = len(title_words)
    for word in title_words:
        if word in text:
            ok += 1
    if total == ok and total > 2:
        confirmation_reason = 'T  %s/%s  %s...' % (ok, total, titles[0][:30])
    else:
        confirmation_reason = ''
    return confirmation_reason

def get_citation_from_doi(doi):
    """ search for DOI, return recid if exactly one result"""
    recid_citation = None
    if doi:
        candidates = perform_request_search(p='doi:%s' % doi)
        if len(candidates) == 1: recid_citation = candidates[0]
    return recid_citation

def get_citation_from_repno(repno):
    """ search for report number, return recid if exactly one result"""
    recid_citation = None
    if repno:
        candidates = perform_request_search(p='reportnumber:%s' % repno)
        if len(candidates) == 1: recid_citation = candidates[0]
    return recid_citation

def get_citation_from_pubnote(journal, volume, text, debug=False):
    """
    guess pubnote from text - looking for 4 groups of digits:
      first is the year (== volume)
      another is the year
      from the two others, the first is the month ( <=12 , the other the article-id)
    search for pubnote, return recid if exactly one result
    """

    recid_citation = None
    if volume:
        year = derive_year_from_volume(volume)
        search_res = re.search(r'%s[():, ]+(\d+)[():, ]+(\d+)[():, ]+(\d+)' % volume, text)
        if search_res:
            year = ''
            month = ''
            true_artid = ''
            for i in [1, 2, 3]:
                text = search_res.group(i)
                if text == volume:
                    year = text
                elif month:
                    true_artid = text # fill artid last
                elif int(text) < 13:
                    month = text
            if year and month and true_artid:
                # make sure there are leading 0's
                month = '%02i' % int(month)
                true_artid = '%03i' % int(true_artid)
                pattern = '773__p:"%s" and 773__c:"%s" and 773__v:"%s%s"' % (journal, true_artid, year[-2:], month)
                candidates = perform_request_search(p=pattern)
                if debug:
                    print '    found %s candidates for pbn %s' % (len(candidates), pattern)
                if len(candidates) == 1: recid_citation = candidates[0]
    return recid_citation

def get_candidates_by_journal_year_artid(journal, volume, artid):
    """
    guess year from volume
    return list of candidates
    """
    candidates = []

    if volume and artid:
        if volume[:2] == volume[2:]:
            # this is a known bug - year is repeated as month e.g. 1515
            year = volume[:2]
            if int(year) < 50: # NOTE: I assume this will not run in 2050 anymore
                year = '20%s' % year
            else:
                year = '19%s' % year
        else:
            year = volume
        # maybe it's correct - make it Y2020 complient and add the correct search to candidates
        pattern = '773__p:"%s" and 773__c:"%s" and 773__v:"%s"' % (journal, artid, volume)
        candidates = perform_request_search(p=pattern)
        # ignore the potentially wrong volume, use only the year
        pattern = '773__p:"%s" and 773__c:"%s" and 773__y:"%s"' % (journal, artid, year)
        candidates += perform_request_search(p=pattern)
    return candidates

def guess_citation(journal, volume, artid, text, debug=False):
    """
    return recid and reason for confirmation if exactly one result confirmed,
    return list of candidates
    """
    recid_citation = None
    confirmation_reason = ''
    multiple_results = False
    candidates = get_candidates_by_journal_year_artid(journal, volume, artid)

    if debug:
        print '    found %s candidates for %s %s %s' % (len(candidates), journal, volume, artid)

    if candidates:
        text = re.sub(r'\$\$([a-z])', r'$$\1 ', text.lower()) # search is easier with \W in front of the author
        for candidate in candidates:
            confirmation_result = confirm_by_authors(text, candidate)
            if confirmation_result == 'Too many authors':
                confirmation_result = confirm_by_collaboration(text, candidate)
                if not confirmation_result:
                    confirmation_result = confirm_by_title(text, candidate)

            if debug:
                print '    %s  :  %s' % (candidate, confirmation_result)
            if confirmation_result:
                if recid_citation:
                    multiple_results = True
                else:
                    recid_citation = candidate
                    confirmation_reason = confirmation_result

    if multiple_results:
        recid_citation = None
        confirmation_reason = ''

    return recid_citation, confirmation_reason, candidates

def wrong_pubnote(pbn):
    """ Dont add obviously wrong PubNotes """
    try:
        wrong_pbn = int(pbn['v'][-2:]) > 12
    except (KeyError, ValueError):
        wrong_pbn = True
    wrong_pbn = wrong_pbn or pbn['v'] == pbn['y']
    return wrong_pbn

def get_pubnote_from_inspire(journal, artid, recid, debug=False):
    """
    get publication note of a record
    in case of several 773 fields get the one corresponding to journal and article-id
    Dont use PBNs with volume == year - print warning
    """
    pubnote = ''
    if not recid:
        return pubnote

    record = get_record(recid)

    # render the mark-fields to a list of dicts
    pbns = []
    pubnotes = record.get('773', [])
    if debug and not pubnotes:
        print 'No pubnote for %s - %s %s' % (recid, journal, artid)

    for subfield in pubnotes:
        pbn = {'y':''}
        for code, value in subfield[0]:
            if code in ['p', 'v', 'c', 'y']:
                pbn[code] = value
        if len(pbn) == 4:
            pbns.append(pbn)

    if len(pbns) == 1:
        pbn = pbns[0]
        if wrong_pubnote(pbn):
            if debug:
                print 'Wrong pubnote in %s: %s %s (%s) %s' % (recid, pbn['p'], pbn['v'], pbn['y'], pbn['c'])
        else:
            pubnote = '%s,%s,%s' % (pbn['p'], pbn['v'], pbn['c'])
            if debug:
                print '    single pbn', pubnote
    else:
        for pbn in pbns:
            if pbn['p'].lower() == journal.lower() and pbn['c'].lower() == artid.lower():
                if wrong_pubnote(pbn):
                    if debug:
                        print 'Wrong pubnote in %s: %s %s (%s) %s' % (recid, pbn['p'], pbn['v'], pbn['y'], pbn['c'])
                else:
                    pubnote = '%s,%s,%s' % (pbn['p'], pbn['v'], pbn['c'])
                    if debug:
                        print '    selected pbn', pubnote

    return pubnote

def check_record(record, no_tickets=False):
    """ same as analyse_refs as BibCheck plugin """
    for m999 in record.get('999', []):
        reference = parse_ref(m999)
        journal, volume, artid = parse_pbn(reference)

        if journal in JOURNALS and volume_looks_wrong(volume):
            recid_citation = get_citation_from_doi(reference['doi'])
            confirmation_reason = 'DOI'
            if not recid_citation:
                recid_citation = get_citation_from_repno(reference['repno'])
                confirmation_reason = 'RepNo'
            if not recid_citation:
                recid_citation = get_citation_from_pubnote(journal, volume, reference['subfields_text'])
                confirmation_reason = 'PubNote'
            if recid_citation:
                candidates = [recid_citation, ]
            else:
                recid_citation, confirmation_reason, candidates = \
                    guess_citation(journal, volume, artid, reference['subfields_text'])

            inspire_pubnote = get_pubnote_from_inspire(journal, artid, recid_citation)

            if inspire_pubnote:
                if not m999[0][reference['position_pbn']] == ('s', inspire_pubnote):
                    m999[0][reference['position_pbn']] = ('s', inspire_pubnote)
                    record.set_amended('R %s: %s %s  <-  %s' %
                        (confirmation_reason, reference['curator'], inspire_pubnote, reference['mark_line']))
                if reference['subfield_0'] and not \
                    (reference['subfield_0'].isdigit() and int(reference['subfield_0']) == recid_citation):
                    m999[0].remove(('0', reference['subfield_0']))
                    record.set_amended('    deleting $$0%s' % reference['subfield_0'])
            else:
                url = 'http://inspirehep.net/search?p=773__p%%3A%%22%s%%22+773__y%%3A%%22%s%%22+773__c%%3A%%22%s%%22' % (journal, volume, artid)
                # url = 'http://inspirehep.net/search?p= + '+or+'.join('recid%%3A%s' % recid for recid in candidates) # alternative link
                if no_tickets:
                    record.warn('Ambigous reference: %s' % reference['mark_line'])
                else:
                    record.set_invalid('Ambigous reference: %s  %s' % (url, re.sub(r'\$\$', '\n                        $$', reference['mark_line'])))

def analyse_refs(recid, debug):
    """
    for references to JOURNALS:
    * check if the volume can be YYMM
    * if not try to find the correct record in INSPIRE
    * replace the journal pubnote in reference
    * delete wrong $$0 in reference
    * return xml of corrected record for BatchUpload in correct mode
    """
    from invenio.bibrecord import record_xml_output

    record = get_record(recid)
    update_refs = False

    for m999 in record.get('999', []):
        reference = parse_ref(m999)
        journal, volume, artid = parse_pbn(reference)

        nice_line = '%s  999C5  %s' % (recid, reference['mark_line'])
        if journal in JOURNALS and volume_looks_wrong(volume):
            if debug:
                print '----------', nice_line

            recid_citation = get_citation_from_doi(reference['doi'])
            confirmation_reason = 'DOI'
            if not recid_citation:
                recid_citation = get_citation_from_repno(reference['repno'])
                confirmation_reason = 'RepNo'
            if not recid_citation:
                recid_citation = get_citation_from_pubnote(journal, volume, reference['subfields_text'], debug)
                confirmation_reason = 'PubNote'
            if recid_citation:
                candidates = [recid_citation, ]
            else:
                recid_citation, confirmation_reason, candidates = \
                    guess_citation(journal, volume, artid, reference['subfields_text'], debug)

            inspire_pubnote = get_pubnote_from_inspire(journal, artid, recid_citation, debug)

            if inspire_pubnote:
                if not m999[0][reference['position_pbn']] == ('s', inspire_pubnote):
                    m999[0][reference['position_pbn']] = ('s', inspire_pubnote)
                    update_refs = True
                    print 'R %s: %s %s   <-%s  %s' % (confirmation_reason, reference['curator'], inspire_pubnote, recid, reference['mark_line'])
                if reference['subfield_0'] and not \
                    (reference['subfield_0'].isdigit() and int(reference['subfield_0']) == recid_citation):
                    m999[0].remove(('0', reference['subfield_0']))
                    update_refs = True
                    print '    %s deleting $$0%s' % (recid, reference['subfield_0'])
            else:
                print '? %s    %s' % (candidates, nice_line)

    if update_refs:
        text = record_xml_output(record, ['001', '005', '999'])
    else:
        text = ''
    return text

def get_recids_2016(journal):
    """ looking for volumes which are years (e.g. 2016) """
    pattern = '999C5s:"%s,20*"' % journal
    recids = perform_request_search(p=pattern)
    return recids

def get_recids_1616(journal):
    """ looking for volumes with repeated 2-digit year (e.g. 1616) """
    recids = []
    for year in range(13, 21):
        pattern = '999C5s:"%s,%02i%02i,"' % (journal, year, year)
        recids += perform_request_search(p=pattern)
    recids = set(recids)
    return recids

def main():
    import codecs
    journal = 'JCAP'
    # journal = 'JHEP'
    # journal = 'J.Stat.Mech.'
    debug = False

    xmlfile = codecs.EncodedFile(codecs.open('fix_ref.%s.xml' % journal, mode='wb'), 'utf8')
    xmlfile.write('<?xml version="1.0" encoding="UTF-8"?>\n<collection>\n')

    recids = get_recids_2016(journal)
    # recids = get_recids_1616(journal)

    # recids = ['1312698', '1744693', '1745959', '1725570']
    # recids = ['1732258']

    print 'Analysing %s records' % len(recids)

    for recid in recids:
        text = analyse_refs(recid, debug)
        if text:
            xmlfile.write(text+'\n')

    xmlfile.write('</collection>\n')
    xmlfile.close()

if __name__ == '__main__':
    main()
