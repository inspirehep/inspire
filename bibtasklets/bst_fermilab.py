# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2013, 2014, 2015, 2018, 2019 CERN.
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

import datetime
import os
import re
import time
from cgi import escape

import pytz
from invenio.bibtask import write_message
from invenio.config import CFG_SITE_URL
from invenio.search_engine import perform_request_search
from invenio.search_engine_utils import get_fieldvalues

chicago_timezone = pytz.timezone('America/Chicago')

SERIES1 = ['thesis', 'misc', 'tm', 'fn', 'proposal',
           'workbook', 'bachelors', 'masters', 'design',
           'loi', 'eoi', 'pbar', 'nal', 'annual', 'upc',
           'ap', 'en', 'exp', 'lu', 'habil', 'vlhcpub',
           'slides', 'poster', 'code']
SERIES2 = ['PUB', 'CONF']

SERIES1.sort()

CFG_FERMILAB_PATH = "/afs/cern.ch/project/inspire/public/fermilab"


def bst_fermilab():
    write_message('cd /afs/fnal.gov/files/expwww/bss/html/techpubs')

    for series in SERIES1:
        reports = []
        authorId = False
        search = "find r fermilab-" + series + "-*"
        result = perform_request_search(p=search, cc='Fermilab')
        for recid in result:
            reportValues = get_fieldvalues(recid, '037__a')
            author = get_fieldvalues(recid, '100__a')
            authorId = get_fieldvalues(recid, '100__i')
            authorAff = get_fieldvalues(recid, '100__u')
            title = get_fieldvalues(recid, '245__a')
            experiment = get_fieldvalues(recid, '693__e')

            if author:
                author = author[0]
            else:
                author = ''
            if title:
                title = '<i>' + title[0][:100] + '</i>'
            else:
                title = ''
            if experiment:
                experiment = experiment[0]
            else:
                experiment = ''
            if authorAff:
                authorAff = authorAff[0]
            else:
                authorAff = ''
            if authorId:
                authorId = authorId[0]
            for report in reportValues:
                if re.match('FERMILAB-' + series, report, re.IGNORECASE):
                    y = [report, str(recid), author, title,
                         authorId, experiment, authorAff]
                    reports.append(y)
        reports.sort(reverse=True)

        filename = os.path.join(CFG_FERMILAB_PATH,
                                'fermilab-reports-' + series + '.html')
        output = open(filename, 'w')
        output.write('''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Fermilab Technical Publications: %(series)s</title>
  <meta http-equiv="content-type" content="text/html;charset=utf-8" />
</head>
<body>
  <a href="http://bss.fnal.gov/techpubs/fermilab_spires.html">Fermilab Technical Publications</a>
  <br /><br /><i>Updated %(dateTimeStamp)s</i>
  <br />
  <table>''' % {'series': escape(series),
                'dateTimeStamp': chicago_timezone.fromutc(
                    datetime.datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')})
        for report in reports:
            if report[4]:
                search2 = '035__a:' + report[4]
                result = perform_request_search(p=search2, cc='HepNames')
                report[2] = '<a href="%(site)s/record/%(recid)s">%(rep2)s</a>'\
                            % {'site': CFG_SITE_URL,
                               'recid': str(result[0]),
                               'rep2': report[2]}
            line = '''
    <tr>
      <td><a href="%(site)s/record/%(rep1)s">%(rep0)s</a></td>
      <td>%(rep2)s</td>
      <td>%(rep3)s</td>
    </tr>''' % {'site': CFG_SITE_URL,
                'rep0': report[0],
                'rep1': report[1],
                'rep2': report[2],
                'rep3': report[3]}
            if re.search(r'THESIS|MASTERS|BACHELORS', report[0]):
                if report[5]:
                    search2 = '119__a:' + report[5]
                    result = perform_request_search(p=search2,
                                                    cc='Experiments')
                    if result:
                        result = result[0]
                    collaboration = get_fieldvalues(result, '710__g')
                    if collaboration:
                        collaboration = collaboration[0]
                        collaboration = collaboration.replace(' Collaboration',
                                                              '')
                        report[5] = report[5] + ' (' + collaboration + ')'
                    if result:
                        report[5] = '<a href="%(site)s/record/%(recid)s">%(rep5)s</a>' \
                                    % {'site': CFG_SITE_URL,
                                       'recid': str(result),
                                       'rep5': report[5]}

                line = '''
    <tr>
      <td><a href="%(site)s/record/%(rep1)s">%(rep0)s</a></td>
      <td>%(rep2)s</td>
      <td>%(rep5)s</td>
      <td>%(rep6)s</td>
      <td>%(rep3)s</td>
    </tr>''' % {'site': CFG_SITE_URL,
                'rep0': report[0],
                'rep1': report[1],
                'rep2': report[2],
                'rep3': report[3],
                'rep5': report[5],
                'rep6': report[6]}
            output.write(line)
        output.write('''
  </table>
</body>
</html>
''')
        output.close()
        write_message('\\rm fermilab-reports-' + series + '.html')
        write_message('cp %s .' % filename)

    reports = []
    for series in SERIES2:
        for year in range(1970, time.localtime()[0]+1):
            dd = str(year)
            dd = re.sub(r"19", "", dd)
            dd = re.sub(r"20", "", dd)
            search = "find r fermilab-" + series + "-" + dd + "*"
            result = perform_request_search(p=search, cc='Fermilab')
            for recid in result:
                reportValues = get_fieldvalues(recid, '037__a')
                author = get_fieldvalues(recid, '100__a')
                title = get_fieldvalues(recid, '245__a')
                if author:
                    author = author[0]
                else:
                    author = ''
                if title:
                    title = title[0][:100]
                else:
                    title = ''
                for report in reportValues:
                    if re.match('FERMILAB-' + series, report, re.IGNORECASE):
                        number = re.sub("FERMILAB-" + series + "-", "", report)
                        y = [year, number, report, str(recid), author, title]
                        reports.append(y)
    reports.sort(reverse=True)

    filename = os.path.join(CFG_FERMILAB_PATH, 'fermilab-reports-preprints.html')
    output = open(filename, 'w')
    output.write('''
<html>
<header>
<title>Fermilab Technical Publications: preprints</title>
</header>
<body>
  <a href="http://bss.fnal.gov/techpubs/fermilab_spires.html">Fermilab Technical Publications</a>
  <br /><br /><i>Updated %(dateTimeStamp)s</i>
  <br />
  <table>
''' % {'dateTimeStamp': chicago_timezone.fromutc(datetime.datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')})
    for report in reports:
        line = '''
    <tr>
        <td><a href="%(site)s/record/%(rep3)s">%(rep2)s</a></td>
        <td>%(rep4)s</td><td>%(rep5)s</td>
    </tr>
        ''' % {'site': CFG_SITE_URL,
               'rep2': report[2],
               'rep3': report[3],
               'rep4': report[4],
               'rep5': report[5]}
        output.write(line)
    output.write('''
  </table>
</body>
</html>
''')
    output.close()
    write_message('cd /afs/fnal.gov/files/expwww/bss/html/techpubs')
    write_message('\\rm fermilab-reports-preprints.html')
    write_message('cp %s .' % filename)


if __name__ == "__main__":
    bst_fermilab()
