#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import codecs

def coll_split(value):
    """ split at 'and' and ',' """
    colls = []
    # split at 'and' and ','
    for val in value.split(' and '):
        colls += val.split(', ')
    return colls

def coll_cleanforthe(coll):
    """ Cleanup collaboration, try to find author """
    import re
    author = None
    re_for_the = re.compile(r'(?:^| )+(?:for the|on behalf of the|on behalf of|representing the|representing)(?: |$)+', re.IGNORECASE)
    re_start = re.compile(r'^ *(group|team|consortium) +(.*) *$', re.IGNORECASE)
    re_the = re.compile(r'^ *the +', re.IGNORECASE)
    re_for = re.compile(r'^ *for +', re.IGNORECASE)
    re_coll = re.compile(r'(?:^| |\/|-)+collaborations?\.?(?=\W|$)', re.IGNORECASE)
    re_group = re.compile(r'(?:^| |\/|-)+group(?=\W|$)', re.IGNORECASE)
    re_wgroup = re.compile(r'(?:^| |\/|-)+working group(?=\W|$)', re.IGNORECASE)
    re_team = re.compile(r'(?:^| |\/|-)+team(?=\W|$)', re.IGNORECASE)
    re_consortium = re.compile(r'(?:^| |\/|-)+consortium(?=\W|$)', re.IGNORECASE)
   
   
    #replace trailing brackets only if there are leading brackets
    if re.search('^ *\(.*\) *$', coll):
        coll = coll.strip('.; ()')
    else:
        coll = coll.strip('.; ')
    if re_for_the.search(coll):
        if re.search('ASSOCIATION FOR THE', coll, flags=re.IGNORECASE) or \
            re.search('CENTER FOR THE', coll, flags=re.IGNORECASE) or \
            re.search('INSTITUTE FOR THE', coll, flags=re.IGNORECASE) or\
            re.search('FOR THE DEVELOPMENT', coll, flags=re.IGNORECASE):
            return coll, author
        else:
            # get strings leading and trailing 'for the'
            (l, t) = re_for_the.split(coll, maxsplit=1)
            if re.search(r'\w', l):
                lead = re.split(' ', l)
            else:
                lead = []
            if re.search(r'\w', t):
                tail = re.split(' ', t)
            else:
                tail = []
            if len(tail) == 0:
                if len(lead) == 0:
                    # nothing left over
                    coll = ''
                else:
                    # ATLAS John Doe for the
                    coll = lead[0]
                    if len(lead) > 1:
                        author = ' '.join(lead[1:])
            else:
                coll = ' '.join(tail)
                if re.search(r'collaboration$', coll, flags=re.IGNORECASE) or \
                    re.search(r' team$', coll, flags=re.IGNORECASE):
                    #   John Doe for the ATLAS Collaboration
                    if len(lead) > 0:
                        author = ' '.join(lead)
                else:
                    if len(lead) > 0:
                        if len(lead) > 1:
                            # Collaboration John Doe for the ATLAS
                            # John Doe for ATLAS
                            author = ' '.join(lead)
                            author = re_coll.sub('', author)
                        else:
                            # Collaboration for the ATLAS
                            coll = coll + ' ' + lead[0]
            if author:
                # John Doe -> Doe, John
                author = re.sub(r'^ *([\w.-]+) (.+)$', r'\2, \1', author)

    coll = re_the.sub('', coll)
    coll = re_start.sub(r'\2 \1', coll)
    coll = re_coll.sub('', coll)
    coll = re_for.sub('', coll)
    coll = re_group.sub(' Group', coll)
    coll = re_wgroup.sub(' Working Group', coll)
    coll = re_team.sub(' Team', coll)
    coll = re_consortium.sub(' Consortium', coll)
    return coll, author

def coll_cleansimple(value): 
    ### Unify case, get rid of hypen, bring Coll to front ###
    knowncoll = ['ATLAS', 'CALICE', 'ALICE', 'CMS', 'CDF', 'LHCb', 'LHCf', 'H1',
        'ZEUS', 'CLEO', 'HERMES', 'HERA-B', 'ALEPH', 'DELPHI', 'OPAL', 'L3', 
        'CosmoALEPH', 'SLD', 'AMS', 'BTeV', 'BaBar', 'RHIC', 'NuSTAR', 'PHENIX',
         'STAR', 'BooNE', 'MiniBooNE', 'MicroBooNE', 'SciBooNE', 'CAST', 
        'CELSIUS', 'CERES', 'CMD', 'CTA', 'GERDA', 'K2K', 'T2K', 'MAGIC', 
        'NuTeV', 'Planck', 'PANDA', 'Hyper-Kamiokande', 'Super-Kamiokande', 
        'KLOE', 'KM3NeT', 'NEMO', 'Swift', 'IceCube', 'ARGUS', 'CUORE', 
        'CUORICINO', 'DarkSide', 'Daya Bay', 'Fermi-LAT', 'GLAST', 'KASCADE', 
        'VERITAS', 'VIRGO', 'Pierre Auger', 'Majorana', 'MINERvA', 'MINOS', 
        'Muon g-2', 'XENON', 'Muon Collider', 'Linear Collider', 'European Muon']
    knownsubcoll = {'Belle':'-', 'BES':'', 'CDF':'-', 'Kamiokande':'-', 'CLEO':'-'}
    for kc in knowncoll:
        start = re.compile(r' +%s[ \/-]+' % kc, re.IGNORECASE)
        extent = re.compile(r' +%s[ \/-]*([0-9]?[A-Z0-9]) ' % kc, re.IGNORECASE)
        front = re.compile(r'^ +(.+)[ -]+%s +' % kc, re.IGNORECASE)
        value = front.sub(r' %s \1 ' % kc, value)
        value = start.sub(r' %s ' % kc, value)
        value = extent.sub(r' %s-\1 ' % kc, value)
    for kc in knownsubcoll.keys():
        letter = knownsubcoll[kc]
        # correct spelling(case), get rid of '-'
        start = re.compile(r' +%s[ \/-]+' % kc, re.IGNORECASE)
        # if only one trailing character, use '-'
        extent = re.compile(r' +%s[ \/-]+([A-Z0-9]) ' % kc, re.IGNORECASE)
        # deal with roman numbering
        subco = re.compile(r' +%s[ \/-]*(I+) ' % kc, re.IGNORECASE)
        value = start.sub(r' %s ' % kc, value)
        value = subco.sub(r' %s%s\1' % (kc, letter), value)
        value = extent.sub(r' %s-\1 ' % kc, value)
    return value
        
def coll_clean710(value):
    #to make things easier, add leading and trailing space
    value = ' %s ' % value
    re_dzero = re.compile(r' DZero ', re.IGNORECASE)
    re_do = re.compile(r' (?:DO|DØ) ')
    re_panda = re.compile(r' \W*(?:bar|overline)\W*P\W*ANDA\W* ', re.IGNORECASE)
    re_fermilat = re.compile(r' +Fermi[ \/-](?:LAT|Large[ -]Area[ -]Telescope) ', re.IGNORECASE)
    re_glastlat = re.compile(r' +GLAST[ \/-](?:LAT|Large[ -]Area[ -]Telescope) ', re.IGNORECASE)
    re_dchooz = re.compile(r' Double[ \/-]Chooz ', re.IGNORECASE)
    re_dbay = re.compile(r' Daya[ \/-]Bay ', re.IGNORECASE)
    value = re_do.sub(' D0 ', value)
    value = re_dzero.sub(' D0 ', value)
    value = re_fermilat.sub(r' Fermi-LAT ', value)
    value = re_glastlat.sub(r' GLAST LAT ', value)
    value = re_panda.sub(r' PANDA ', value)
    value = re_dchooz.sub(r' Double Chooz ', value)
    value = re_dbay.sub(r' Daya Bay ', value)
    value = re.sub('\$B\W*small A}B\W*small AR}\$', 'BaBar', value)    
    value = re.sub(r' +LHC[ \/-]*([a-z])[ \/-]+', r' LHC\1 ', value) 
    value = re.sub(r' R.and.D ', ' R&D ', value) 
    value = re.sub(r' H\. ?E\. ?S\. ?S\.? +',' HESS ', value) 
    value = re.sub(r' PROMICE[ \/-]WASA ', ' PROMICE/WASA ', value)
    value = re.sub(r' WASA[ \/-]PROMICE ', ' PROMICE/WASA ', value)
    value = re.sub(r' CELSIUS[ \/-]WASA ', ' CELSIUS/WASA ', value)
    value = re.sub(r' WASA[ \/-]*[aA][tT][\/-]*COSY ', ' WASA-at-COSY ', value)
    value = re.sub(r' CERES[ \/-]NA', ' CERES/NA', value)
    value = re.sub(r' EHS[ \/-]NA', ' EHS/NA', value)
    value = coll_cleansimple(value)
    value = re.sub(r'  +',' ',value)
    value = value.strip()
    # replace & for xml output
    value = re.sub('&',u'\u0026',value)
    return value

