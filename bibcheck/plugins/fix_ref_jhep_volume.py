#!/usr/bin/python
# -*- coding: utf-8 -*-

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

For PTEP the article-ID (12D123) is often split and only the first part is kept.

Sometimes a random 'Physics' is recognized as journal MDPI Physics.

This plugin tries to correct the PubNote based on additional info in the reference:
DOI
reportnumber
raw pubnote in the raw-reference
ambigous INSPIRE search (journal, year, artid) + confirmation by author or title

Clear cases will be corrected automatically, others flagged.
"""

import re
from invenio.search_engine import (get_fieldvalues, get_record,
                                   perform_request_search)


def parse_ref(markfield):
    """
    Read subfields of a markfield representing a reference 999C5
    Return a dict with text line, curator-tag,
    $$0, $$r, $$s mark tags, DOI the rest is lumped in text field
    """

    reference_dict = {'subfield_0': '', 'doi': '', 'repno': '',
                      'subfield_pbn': '', 'subfields_text': '',
                      'position_pbn': -1, 'year': '',
                      'mark_line': '', 'curator': ''}

    if markfield[1] == 'C' and markfield[2] == '5':
        for subfield_position, (code, value) in enumerate(markfield[0]):
            reference_dict['mark_line'] += '$$%s%s' % (code, value)
            if code == '0':
                reference_dict['subfield_0'] = value
            elif code == 'a':
                if value.startswith('doi:'):
                    reference_dict['doi'] = value[4:]
            elif code == '9':
                if value == 'CURATOR':
                    reference_dict['curator'] = 'C'
            elif code == 'r':
                reference_dict['repno'] = value.split(' ')[0]
            elif code == 's':
                # in case of more than one $$s subfield, pick one that is interesting
                if not reference_dict['subfield_pbn'].split(',')[0] in \
                    ['JCAP', 'JHEP', 'J.Stat.Mech.', 'PTEP']:
                    reference_dict['position_pbn'] = subfield_position
                    reference_dict['subfield_pbn'] = value
            elif code == 'y':
                reference_dict['year'] = value
            else:
                reference_dict['subfields_text'] = '%s $$%s%s' % (reference_dict['subfields_text'], code, value)

    return reference_dict


def parse_pbn(reference):
    """
    split $$s subfield in journal, volume and artid
    include year in return pbn
    """
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

    return {'p':journal, 'v':volume, 'c':artid, 'y':reference['year']}


def derive_year_from_YYMM(volume):
    """ volume should be YYMM """
    try:
        year = volume[:2]
        if int(year) < 50:  # I hope this is not necessary after 2050, no JHEP articles before 1950
            year = '20%s' % year
        else:
            year = '19%s' % year
    except ValueError:
        year = volume
    return year


def wrong_pubnote(pbn, source, fuzzy=False):
    """
    For JHEP etc.:
    Volume should be YYMM; true if
    month (MM) > 12 or
    YYYY is more likely, i.e. 2016
    In fuzzy mode potentially wrong volumes YY==MM will be checked.
    WARNING: from year 2020 on this will flag correct YYMM unless year is given
    In references the year might be derived from wrong volume and is useless.

    For PTEP:
    article-id contains a letter in the middle. 1st 2 digits are month.
    """
    bug_type = ''
    rendered_pbn = 'x' in pbn # comes most likely from arxiv - don't trust it

    if pbn['p'].upper() in ['JCAP', 'JHEP', 'J.STAT.MECH.']:
        try:
            wrong_volume = int(pbn['v'][-2:]) > 12
        except (KeyError, ValueError):
            wrong_volume = True
        if len(pbn['v']) != 4:
            wrong_volume = True
        if fuzzy and source == 'reference':
            if pbn['v'][-2:] == pbn['v'][:2]:
                wrong_volume = True
        if source == 'pubnote' and pbn['y']:
            volume_is_year = pbn['v'] == pbn['y']
        else:
            volume_is_year = pbn['v'].startswith('20')
        wrong_pbn = wrong_volume or volume_is_year
        if wrong_pbn:
            bug_type = 'JHEP'
    elif pbn['p'] == 'PTEP':
        if re.search(r'^\d{2,3}[A-Z]\d{2,3}$', pbn['c']):
            wrong_pbn = False
        else:
            wrong_pbn = True
            bug_type = 'PTEP'
    elif pbn['p'] == 'Physics':
        if source == 'reference' or rendered_pbn:
            # mostly wrong
            wrong_pbn = True
            bug_type = 'Physics'

    return bug_type


def confirm_by_collaboration(text, candidate):
    """
    Confirmed if all collaborations are in text
    Return reason - result of confirmation analysis
    """
    ok = 0
    confirmation_reason = ''

    collaborations = get_fieldvalues(candidate, '710__g')
    for collaboration in collaborations:
        if collaboration.lower() in text:
            ok += 1

    if collaborations and ok == len(collaborations):
        confirmation_reason = 'C %s/%s' % (ok, len(collaborations))
    return confirmation_reason


def confirm_by_authors(text, candidate):
    """
    Confirmed if more than 60% of the first 4 authors last-names are in text
    Return reason - result of confirmation analysis
    If the cited record has more than 8 authors
    most likely only the first is given in the reference (et.al.)
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
                    # this is robust, but 'Li, Chiang' matches 'Lindner, Alex',
                    # so restrict it to longer names
                    ok += 1
            else:
                if re.search(r'(?i)(?<!\w)%s(?!\w)' % lastname, text):
                    ok += 1
        if total and ok / float(total) > 0.6:
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
        if len(candidates) == 1:
            recid_citation = candidates[0]
        elif not candidates:
            # check for trailing ';' or ')'
            if doi[-1] in [';', ','] or (doi[-1] == ')' and doi.find('(') < 0):
                candidates = perform_request_search(p='doi:%s' % doi[:-1])
                if len(candidates) == 1:
                    recid_citation = candidates[0]
    return recid_citation


def get_citation_from_repno(repno):
    """ search for report number, return recid if exactly one result"""
    recid_citation = None
    if repno:
        candidates = perform_request_search(p='reportnumber:%s' % repno)
        if len(candidates) == 1:
            recid_citation = candidates[0]
    return recid_citation


def get_citation_for_PTEP(ref_pbn, text, debug):
    '''
    look for typical references:
    PTEP 2016, no. 9, 093B05
    PTEP 2016 (2016) 12C101
    PTEP, 2017(5):053B03
    '''
    recid_citation = None
    pubnote = ''
    journal = ref_pbn['p']
    volume = ref_pbn['v']
    ref_year = ref_pbn['y']

    text = text.replace('.', ' ').upper()
    text = text.replace(' NO ', ' ')
    text = text.replace(' P ', ' ')
    text = text.replace(r' +', ' ')
    text = text.replace('PROGRESS OF THEORETICAL AND EXPERIMENTAL PHYSICS', 'PTEP')
    text = text.replace('PROG THEOR EXP PHYS', 'PTEP')

    if volume.isdigit() and 2000 < int(volume) < 2030:
        year = volume
    elif ref_year:
        year = ref_year
    else:
        year = ''

    search_string = r'PTEP[^A-Za-z]*%s[^A-Za-z]*[,: ](\d{2,3}[A-Z]\d{2,3})' % year
    search_res = re.search(search_string, text)
    if search_res:
        true_artid = search_res.group(1)
        pubnote = '%s,%s,%s' % (journal, year, true_artid)
        pattern = '773__p:"%s" and 773__c:"%s" and 773__v:"%s"' % (journal, true_artid, year)
        candidates = perform_request_search(p=pattern)
        if debug:
            print '    found %s candidates for pbn %s' % (len(candidates), pattern)
        if len(candidates) == 1:
            recid_citation = candidates[0]
    else:
        if debug:
            print 'Can not find %s in %s' % (search_string, text)
    return recid_citation, pubnote


def get_citation_for_JHEP(ref_pbn, text, debug):
    '''
    looking for 4 groups of digits:
    first is the year (== volume), another is the year
    from the two others, the first is the month ( <=12 , the other the article-id)
    '''
    recid_citation = None
    pubnote = ''
    journal = ref_pbn['p']
    volume = ref_pbn['v']

    if volume:
        year = derive_year_from_YYMM(volume)
        search_res = re.search(r'%s[():, ]+(\d+)[():, ]+(\d+)[():, ]+(\d+)' % volume, text)
        if search_res:
            month = ''
            true_artid = ''
            for i in [1, 2, 3]:
                digit_group = search_res.group(i)
                if digit_group == volume:
                    year = digit_group
                elif month:
                    true_artid = digit_group  # fill artid last
                elif int(digit_group) < 13:
                    month = digit_group
            if year and month and true_artid:
                # make sure there are leading 0's
                month = '%02i' % int(month)
                true_artid = '%03i' % int(true_artid)
                pubnote = '%s,%s%s,%s' % (journal, year[-2:], month, true_artid)
                pattern = '773__p:"%s" and 773__c:"%s" and 773__v:"%s%s"' % (journal, true_artid, year[-2:], month)
                candidates = perform_request_search(p=pattern)
                if debug:
                    print '    found %s candidates for pbn %s' % (len(candidates), pattern)
                if len(candidates) == 1:
                    recid_citation = candidates[0]
    return recid_citation, pubnote


def get_citation_from_pubnote(ref_pbn, bug_type, text, debug=False):
    """
    guess pubnote from text
    search for pubnote, return recid if exactly one result
    """

    if bug_type == "PTEP":
        recid_citation, pubnote = get_citation_for_PTEP(ref_pbn, text, debug)
    elif bug_type == 'JHEP':
        recid_citation, pubnote = get_citation_for_JHEP(ref_pbn, text, debug)
    else:
        recid_citation = None
        pubnote = ''
    return recid_citation, pubnote


def get_candidates_ignoring_journal(ref_pbn, debug):
    """
    journal is wrong - use only the rest
    volume might be preceeded by journal letter, artid might be start-page
    return list of candidates
    """
    year = ref_pbn['y']
    volume = ref_pbn['v']
    artid = ref_pbn['c']

    candidates = []
    if volume and artid:
        pattern = '773__v:"*%s" and 773__c:"%s*"' % (volume, artid)
        if year:
            pattern += ' 773__y:%s' % year
        if debug:
            print pattern
        candidates = perform_request_search(p=pattern)
    return candidates


def get_candidates_by_artid_substring(ref_pbn, debug):
    """
    search substring in article-ID
    return list of candidates
    """
    journal = ref_pbn['p']
    volume = ref_pbn['v']
    artid = ref_pbn['c']

    pattern = "773__p:%s and 773__c:'%s' and 773__v:%s" % (journal, artid, volume)
    if debug:
        print pattern
    candidates = perform_request_search(p=pattern)
    return candidates


def get_candidates_by_journal_year_artid(ref_pbn):
    """
    guess year from volume
    return list of candidates
    """
    journal = ref_pbn['p']
    volume = ref_pbn['v']
    artid = ref_pbn['c']

    candidates = []
    if volume and artid:
        if volume[:2] == volume[2:]:
            # this is a known bug - year is repeated as month e.g. 1515
            year = derive_year_from_YYMM(volume)
        else:
            year = volume
        # maybe it's correct - make it Y2020 complient and add the correct search to candidates
        pattern = '773__p:"%s" and 773__c:"%s" and 773__v:"%s"' % (journal, artid, volume)
        candidates = perform_request_search(p=pattern)
        # maybe it's mixed up - switch volume and artid
        pattern = '773__p:"%s" and 773__c:"%s" and 773__v:"%s"' % (journal, volume, artid)
        candidates += perform_request_search(p=pattern)
        # ignore the potentially wrong volume, use only the year
        pattern = '773__p:"%s" and 773__c:"%s" and 773__y:"%s"' % (journal, artid, year)
        candidates += perform_request_search(p=pattern)
    return candidates


def guess_citation(ref_pbn, bug_type, text, debug=False):
    """
    return recid and reason for confirmation if exactly one result confirmed,
    return list of candidates
    """
    recid_citation = None
    confirmation_reason = ''
    multiple_results = False

    if bug_type == 'JHEP':
        candidates = get_candidates_by_journal_year_artid(ref_pbn)
    elif bug_type == 'PTEP':
        candidates = get_candidates_by_artid_substring(ref_pbn, debug)
    elif bug_type == 'Physics':
        candidates = get_candidates_ignoring_journal(ref_pbn, debug)
    else:
        confirmation_reason = 'ERROR: unknown bug_type: %s' % bug_type
        return recid_citation, confirmation_reason

    if debug:
        print '    found %s candidates for %s' % (len(candidates), ref_pbn)

    if len(candidates) > 25:
        confirmation_reason = 'ERROR: %s - too many candidates: %s' % \
                              (bug_type, len(candidates))
    elif candidates:
        # search is easier with \W in front of the author
        text = re.sub(r'\$\$([a-z])', r'$$\1 ', text.lower())
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

    return recid_citation, confirmation_reason


def pubnotes_from_recid(recid, debug=False):
    """
    return journal pubnotes as list of dicts
    if there are at least p,v,c
    """
    record = get_record(recid)
    pbns = []
    pubnotes = record.get('773', [])
    if debug and not pubnotes:
        print 'No pubnote for %s' % (recid)

    for subfield in pubnotes:
        pbn = {'y': ''}
        for code, value in subfield[0]:
            pbn[code] = value
        if 'p' in pbn and 'v' in pbn and 'c' in pbn:
            pbns.append(pbn)
    return pbns


def get_pubnote_from_inspire(ref_pbn, bug_type, recid, debug=False):
    """
    get publication note of a record
    in case of several 773 fields get the one corresponding to journal and article-id
    Dont use PBNs with wrong pubnote - print warning
    """
    journal = ref_pbn['p']
    artid = ref_pbn['c']
    pubnote = ''
    if not recid:
        return pubnote

    pbn_candidates = {}
    for pbn in pubnotes_from_recid(recid, debug):
        if pbn['p'] == journal or bug_type == 'Physics':
            if wrong_pubnote(pbn, 'pubnote'):
                if debug:
                    print 'Wrong pubnote in %s: %s %s (%s) %s' % (recid, pbn['p'], pbn['v'], pbn['y'], pbn['c'])
            else:
                first_page = pbn['c'].split('-')[0]
                pbn_candidates[first_page] = '%s,%s,%s' % (pbn['p'], pbn['v'], first_page)
    if artid in pbn_candidates.keys():
        pubnote = pbn_candidates[artid]
    elif pbn_candidates:
        pubnote = pbn_candidates.values()[-1]

    return pubnote


def check_record(record, tickets=True, fuzzy=False):
    """
    same as analyse_refs as BibCheck plugin
    tickes=False: instead of RT tickets, a WARN to log-file
    """
    recid = record['001'][0][3]
    for m999 in record.get('999', []):
        reference = parse_ref(m999)
        ref_pbn = parse_pbn(reference)

        bug_type = wrong_pubnote(ref_pbn, 'reference', fuzzy)
        if bug_type:
            pubnote_from_rawref = ''
            recid_citation = get_citation_from_doi(reference['doi'])
            confirmation_reason = 'DOI'
            if not recid_citation:
                recid_citation = get_citation_from_repno(reference['repno'])
                confirmation_reason = 'RepNo'
            if not recid_citation:
                recid_citation, pubnote_from_rawref = \
                    get_citation_from_pubnote(ref_pbn, bug_type, reference['subfields_text'])
                confirmation_reason = 'PubNote'
            if not recid_citation:
                recid_citation, confirmation_reason = \
                    guess_citation(ref_pbn, bug_type, reference['subfields_text'])
                if confirmation_reason.startswith('ERROR'):
                    record.warn(confirmation_reason)

            inspire_pubnote = get_pubnote_from_inspire(ref_pbn, bug_type, recid_citation)

            if inspire_pubnote:
                if m999[0][reference['position_pbn']] == ('s', inspire_pubnote):
                    # Add unchanged references to the logs for statistics
                    record.warn('= %s: %s == %s' % \
                    (confirmation_reason, inspire_pubnote, reference['mark_line']))
                else:
                    m999[0][reference['position_pbn']] = ('s', inspire_pubnote)
                    record.set_amended('R %s: %s %s  <-  %s' %
                                       (confirmation_reason, reference['curator'],
                                        inspire_pubnote, reference['mark_line']))
                if reference['subfield_0'] and not \
                   (reference['subfield_0'].isdigit() and int(reference['subfield_0']) == recid_citation):
                    m999[0].remove(('0', reference['subfield_0']))
                    record.set_amended('    deleting $$0%s' % reference['subfield_0'])
            else:
                if tickets:
                    record.set_invalid('?  %s -- %s -- %s' % \
                        (recid, pubnote_from_rawref, reference['mark_line']))
                else:
                    record.warn('?  %s -- %s -- %s' % \
                        (recid, pubnote_from_rawref, reference['mark_line']))


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
    log_text = ''

    for m999 in record.get('999', []):
        reference = parse_ref(m999)
        ref_pbn = parse_pbn(reference)

        nice_line = '%s  999C5  %s' % (recid, reference['mark_line'])

        bug_type = wrong_pubnote(ref_pbn, 'reference')
        if bug_type:
            if debug:
                print '---------- %s ----- %s'% (bug_type, nice_line)

            pubnote_from_rawref = ''
            recid_citation = get_citation_from_doi(reference['doi'])
            confirmation_reason = 'DOI'
            if not recid_citation:
                recid_citation = get_citation_from_repno(reference['repno'])
                confirmation_reason = 'RepNo'
            if not recid_citation:
                recid_citation, pubnote_from_rawref = \
                    get_citation_from_pubnote(ref_pbn, bug_type, reference['subfields_text'], debug)
                confirmation_reason = 'PubNote'
            if not recid_citation:
                recid_citation, confirmation_reason = \
                    guess_citation(ref_pbn, bug_type, reference['subfields_text'], debug)
                if confirmation_reason.startswith('ERROR'):
                    log_text += '%s/n' % confirmation_reason

            inspire_pubnote = get_pubnote_from_inspire(ref_pbn, bug_type, recid_citation, debug)

            if inspire_pubnote:
                if m999[0][reference['position_pbn']] == ('s', inspire_pubnote):
                    # Add unchanged references to the logs for statistics
                    log_text += '= %s: %s ==%s  %s\n' % \
                    (confirmation_reason,  \
                    inspire_pubnote, recid, reference['mark_line'])
                else:
                    m999[0][reference['position_pbn']] = ('s', inspire_pubnote)
                    update_refs = True
                    log_text += 'R %s: %s %s   <-%s  %s\n' % \
                    (confirmation_reason, reference['curator'], \
                    inspire_pubnote, recid, reference['mark_line'])
                if reference['subfield_0'] and not \
                   (reference['subfield_0'].isdigit() and int(reference['subfield_0']) == recid_citation):
                    m999[0].remove(('0', reference['subfield_0']))
                    update_refs = True
                    log_text += '    %s deleting $$0%s\n' % (recid, reference['subfield_0'])
            else:
                log_text += '?  %s  %s %s\n' % (confirmation_reason, pubnote_from_rawref, nice_line)

    if update_refs:
        text = record_xml_output(record, ['001', '005', '999'])
    else:
        text = ''
    return text, log_text


def get_recids_startpbn(bad_references):
    """ looking for references starting with ... """
    recids = []
    for bad_reference in bad_references:
        pattern = '999C5s:"%s*"' % bad_reference
        recids += perform_request_search(p=pattern)
    recids = set(recids)
    return recids


def get_recids_PTEP():
    """ looking for truncated recids """
    pattern = '999C5s:/^PTEP.*,\d\d\d$/'
    recids = perform_request_search(p=pattern)
    return recids


def get_recids_2016(journal):
    """ looking for volumes which are years (e.g. 2016) """
    pattern = '999C5s:"%s,20*"' % journal
#    pattern += ' and datemodified:2020-01-19->2020-01-30'
    recids = perform_request_search(p=pattern)
    return recids


def get_recids_1616(journal):
    """ looking for volumes with repeated 2-digit year (e.g. 1616) """
    recids = []
    for year in range(13, 21):
        pattern = '999C5s:"%s,%02i%02i,*"' % (journal, year, year)
        recids += perform_request_search(p=pattern)
    recids = set(recids)
    return recids


def main():
    import codecs
    # journal = 'JCAP'
    # journal = 'JHEP'
    # journal = 'J.Stat.Mech.'
    journal = 'PTEP'
    # journal = 'MDPI'

    debug = False

    if journal == 'MDPI':
        recids = get_recids_startpbn(['MDPI Physics,', ])
    elif journal in ['JHEP', 'JCAP', 'J.Stat.Mech.']:
        recids = get_recids_2016(journal)
        # recids = get_recids_1616(journal)
    elif journal == 'PTEP':
        recids = get_recids_PTEP()

    # recids = ['1312698', '1744693', '1745959', '1725570']
    recids = ['1242133']

    print 'Analysing %s records' % len(recids)
    # recids = list(recids)[-100:]
    if len(recids) > 500:
        print 'Too many records'
        return

    logfile = codecs.EncodedFile(codecs.open('fix_ref.%s.log' % journal, mode='wb'), 'utf8')
    xmlfile = codecs.EncodedFile(codecs.open('fix_ref.%s.xml' % journal, mode='wb'), 'utf8')
    xmlfile.write('<?xml version="1.0" encoding="UTF-8"?>\n<collection>\n')

    for recid in recids:
        text, log_text = analyse_refs(recid, debug)
        logfile.write(log_text)
        if text:
            xmlfile.write(text+'\n')

    xmlfile.write('</collection>\n')
    xmlfile.close()
    logfile.close()
    return


if __name__ == '__main__':
    main()
