#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import codecs
import datetime

from collclean_lib import coll_cleanforthe
from collclean_lib import coll_clean710
from collclean_lib import coll_split

#this should come from a KB
expcoll = []
 
def coll_check(colls, logtext):
    global expcoll 
    for coll in colls:
        # misspelled collaboration?
        if re.search('coll', coll.lower()) or re.search('borati', coll.lower()):
            if re.search('collider', coll.lower()) or re.search('college', coll.lower()):
                pass
            else:
                logtext += 'COLL?? %s ' % coll
    
    # for splitted colls: is this string listed in EXP 710__g?    
    if len(colls) > 1:
        unknown = False
        for coll in colls:
            if not coll in expcoll:
                unknown = True
        if unknown:
            colls = None
            logtext += '          Dont dare to change\n' 
    return colls, logtext
   
def coll_splitandclean(recid, value, logtext):
    newcolls = []
    for original in coll_split(value):    
        (coll, author) = coll_cleanforthe(original)
        coll = coll_clean710(coll)
        newcolls.append(coll)
        if author:
            logtext += '%09i found author: %s\n' % (recid,author)
            logtext += '           in: %s\n' % original
    (newcolls, logtext) = coll_check(newcolls, logtext)
    return newcolls, logtext
    
def writexml(recid, mark, changed):
    ind1 = mark[1]
    ind2 = mark[2]
    extracolls = []
    logtext = ''
    xmltext = ''
    curator = False
    for field in mark[0]:
        if field[0] == '9' and field[1].upper().strip() == 'CURATOR':
            curator = True
    if curator:
        logtext += '%09i Skipping %s\n' % (recid, mark)
            
    xmltext += '  <datafield tag="710" ind1="%s" ind2="%s">\n' % (ind1, ind2)
    for field in mark[0]:
        subf = field[0]
        value = field[1]
        if ind1 == ' ' and ind2 == ' ' and subf == 'g' and not curator:
            logtext += '%09i %s\n' % (recid, value)
            (colls, logtext) = coll_splitandclean(recid, value, logtext)
            if colls:
                if not colls[0] == value.strip():
                    changed = True
                    for coll in colls:
                        logtext += '          %s\n' % coll 
                value = colls[0]
                extracolls = colls[1:]
                
        xmltext += '    <subfield code="%s">%s</subfield>\n' % (subf, value)
    xmltext += '  </datafield>\n' 
    if extracolls:
        for value in extracolls:
            xmltext += '  <datafield tag="710" ind1="%s" ind2="%s">\n' % (ind1, ind2)
            xmltext += '    <subfield code="%s">%s</subfield>\n' % (subf, value)
            xmltext += '  </datafield>\n' 
    return(xmltext, logtext, changed)
    

def main():
    from invenio.search_engine import get_collection_reclist
    from invenio.search_engine import search_pattern
    from invenio.search_engine import get_record
    from invenio.search_engine import get_fieldvalues
    global expcoll 
    now = datetime.datetime.now()
    stopdate = now
    startdate = stopdate + datetime.timedelta(days=-10)
    filedate = '%4d%02d%02d' % (stopdate.year, stopdate.month, stopdate.day)
    stampofstopdate = '%4d-%02d-%02d' % (stopdate.year, stopdate.month, stopdate.day)
    stampofstartdate = '%4d-%02d-%02d' % (startdate.year, startdate.month, startdate.day)
    
    exp = get_collection_reclist("Experiments")
    hep = get_collection_reclist("HEP")
    
    recall = search_pattern(p="710__g:/^./")
    recexp = recall.intersection(exp)
    for rec in recexp:
        expcoll += get_fieldvalues(rec, '710__g')

    reccoll = search_pattern(p="710__g:'collaboration'")
    recids = search_pattern(p="dadd:%s->%s" % (stampofstartdate,stampofstopdate))
    recids = recids.intersection(recall)
    recids = recids.union(reccoll)
    recids = recids.intersection(hep)
    logtext =  ''
    xmlpath = "/afs/desy.de/user/l/library/dok/inspire/correct/"
    filename = '%scoll_%s.correct' % (xmlpath,filedate)
    try:
        filexml = codecs.EncodedFile(codecs.open(filename, 'w'), 'utf8')
    except IOError:
        logtext += 'Cant open file %s\n' % filename
        return
#    filelog = open('coll_%s.log' % filedate, 'w')
    xmlall = '<collection>\n'
    mail_subject = 'CollClean %s' % filedate
    logtext += 'Processing coll_%s\n' % filedate
    for rec in recids:
        changed = False
        xmltext = '<record>\n  <controlfield tag="001">%i</controlfield>\n' % rec
        m710 = get_record(rec).get('710')
        for mark in m710:
            (thisxml, thislog, thischange) = writexml(rec, mark, changed)
            logtext += thislog
            if thischange:
                changed = True
                xmltext += thisxml
        if changed:
            xmltext += '</record>\n'
            xmlall += xmltext 
        else:
            logtext += '          unchanged\n'
    xmlall += '</collection>\n'
    filexml.write(xmlall)
    filexml.close()
    
    os.system('echo "%s" | mail -s "%s" %s ' % (logtext,mail_subject,'kirsten.sachs@desy.de'))
#    filelog.write(logtext)
#    filelog.close()
            

if __name__ == "__main__":
        main()
