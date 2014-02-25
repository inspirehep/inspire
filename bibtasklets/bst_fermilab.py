# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2013, 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import os
import re
import datetime
import time
import pytz
from cgi import escape
from invenio.search_engine import perform_request_search
from invenio.search_engine_utils import get_fieldvalues
from invenio.bibtask import write_message

chicago_timezone = pytz.timezone('America/Chicago')

SERIES1 = ['thesis', 'misc', 'tm', 'fn', 'proposal', 'workbook', 'bachelors', 'masters', 'design', 'loi', 'pbar', 'nal', 'annual', 'upc', 'ap', 'en', 'exp', 'lu', 'habil', 'vlhcpub']
SERIES2 = ['PUB', 'CONF']
#serieses = ['thesis']
SERIES1.sort()

CFG_FERMILAB_PATH = "/afs/cern.ch/project/inspire/public/fermilab"

def bst_fermilab():
    write_message('cd /afs/fnal.gov/files/expwww/bss/html/techpubs')

    for series in SERIES1 :
        reports = []
        authorId = False
        search = "find r fermilab-" + series + "-*"
        #search = "find recid 1261432"
        #print search
        result = perform_request_search(p=search, cc='HEP')
        for recid in result :
            #print recid
            reportValues = get_fieldvalues(recid, '037__a')
            author = get_fieldvalues(recid, '100__a')
            authorId = get_fieldvalues(recid, '100__i')
            authorAff = get_fieldvalues(recid, '100__u')
            title = get_fieldvalues(recid, '245__a')
            experiment = get_fieldvalues(recid, '693__e')

            if author :
                author = author[0]
            else :
                author = ''
            if title :
                title = '<i>' + title[0][:100] + '</i>'
            else :
                title = ''
            if experiment :
                experiment = experiment[0]
            else :
                experiment = ''
            if authorAff :
                authorAff = authorAff[0]
            else :
                authorAff = ''
            #print "author = ", author
            #print "title = ", title
            #print "authorId = ", authorId
            #print "experiment = ", experiment
            if authorId :
                authorId = authorId[0]
            for report in reportValues :
                if re.match('FERMILAB-' + series, report, re.IGNORECASE):
                    y = [report, str(recid), author, title, authorId, experiment, authorAff]
                    #print "y = ", y
                    reports.append(y)
        reports.sort(reverse=True)

        filename = os.path.join(CFG_FERMILAB_PATH, 'fermilab-reports-' + series + '.html')
        output = open(filename, 'w')
        output.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n')
        output.write('          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        output.write('<html xmlns="http://www.w3.org/1999/xhtml">\n')
        output.write('<head>\n')
        output.write('<title>Fermilab Technical Publications: ')
        output.write(escape(series))
        output.write('</title>\n')
        output.write('<meta http-equiv="content-type" content="text/html;charset=utf-8" />\n')
        output.write('</head>\n')
        output.write('<body>\n')
        output.write('<a href="http://bss.fnal.gov/techpubs/fermilab_spires.html">Fermilab Technical Publications</a>\n')
        output.write('<br /><br />')
        dateTimeStamp = '<i>Updated ' + chicago_timezone.fromutc(datetime.datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S') + '</i>\n'
        output.write(dateTimeStamp)
        output.write('<br />\n<table>\n')
        for report in reports :
            #print "report =", report
            if report[4]:
                search2 = '035__a:' + report[4]
                #print "search2 =", search2
                result = perform_request_search(p=search2, cc='HepNames')
                #print report[4], result
                report[2] = '<a href="http://inspirehep.net/record/' + str(result[0]) + '">'+report[2]+'</a>'
            line = '<tr><td><a href="http://inspirehep.net/record/'+report[1]+'">'+report[0]+'</a></td>\
                    <td>'+report[2]+'</td><td>'+report[3]+'</td></tr>\n'
            if re.search(r'THESIS', report[0]):
                if report[5]:
                    search2 = '119__a:' + report[5]
                    result = perform_request_search(p=search2, cc='Experiments')
                    if result: result = result[0]
                    collaboration = get_fieldvalues(result, '710__g')
                    if collaboration:
                        collaboration = collaboration[0]
                        collaboration = collaboration.replace(' Collaboration', '')
                        report[5] = report[5] + ' (' + collaboration + ')'
                    if result:
                        report[5] = '<a href="http://inspirehep.net/record/' + str(result) + '">'+report[5]+'</a>'
                line = '<tr><td><a href="http://inspirehep.net/record/'+report[1]+'">'+report[0]+'</a></td>\
                        <td>'+report[2]+'</td><td>'+report[5]+'</td><td>'+report[6]+'</td><td>'+report[3]+'</td></tr>\n'
            output.write(line)
        output.write('</table>\n')
        output.write('</body>\n')
        output.write('</html>\n')
        output.close()
        write_message('\\rm fermilab-reports-' + series + '.html')
        write_message('cp %s .' % filename)

    reports = []
    currentyear = time.strftime('%Y')
    for series in SERIES2 :
        #print series
        for year in range(1970, time.localtime()[0]+1) :
            #print year
            dd = str(year)
            dd = re.sub(r"19", "", dd)
            dd = re.sub(r"20", "", dd)
            search = "find r fermilab-" + series + "-" + dd + "*"
            #print search
            result = perform_request_search(p=search, cc='HEP')
            for recid in result :
                reportValues = get_fieldvalues(recid, '037__a')
                author = get_fieldvalues(recid, '100__a')
                title = get_fieldvalues(recid, '245__a')
                if author :
                    author = author[0]
                else :
                    author = ''
                if title :
                    title = title[0][:100]
                else :
                    title = ''
                for report in reportValues :
                    #print 'report = ' + report
                    #print 'FERMILAB-' + series
                    if re.match('FERMILAB-' + series, report, re.IGNORECASE) :
                        number = re.sub("FERMILAB-" + series + "-", "", report)
                        y = [year, number, report, str(recid), author, title]
                        #print 'y = ' , y
                        reports.append(y)
    reports.sort(reverse=True)
    #print reports

    filename = os.path.join(CFG_FERMILAB_PATH, 'fermilab-reports-preprints.html')
    output = open(filename, 'w')
    output.write('<html>\n')
    output.write('<header>\n')
    output.write('<title>Fermilab Technical Publications: ')
    output.write('preprints')
    output.write('</title>\n')
    output.write('</header>\n')
    output.write('<body>\n')
    output.write('<a href="http://bss.fnal.gov/techpubs/fermilab_spires.html">Fermilab Technical Publications</a>\n')
    output.write('<br /><br />')
    dateTimeStamp = '<i>Updated ' + chicago_timezone.fromutc(datetime.datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S') + '</i>\n'
    output.write(dateTimeStamp)
    output.write('<br />\n<table>\n')
    for report in reports :
        line = '<tr><td><a href="http://inspirehep.net/record/' + report[3] + '">' + report[2] + '</a></td><td>'+report[4]+'</td><td>'+report[5]+'</td></tr>\n'
        output.write(line)
    output.write('</table>\n')
    output.write('</body>\n')
    output.write('</html>\n')
    output.close()
    write_message('cd /afs/fnal.gov/files/expwww/bss/html/techpubs')
    write_message('\\rm fermilab-reports-preprints.html')
    write_message('cp %s .' % filename)


if __name__ == "__main__":
    bst_fermilab()
