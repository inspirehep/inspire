# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2015 CERN.
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
"""BibFormat element - Prints INSPIRE jobs contact name HEPNAMES search
"""


def format_element(bfo, style="", separator=''):
    """
    This is the default format for formatting the contact person
    link in the Jobs format. This link will point to a direct search
    in the HepNames database.

    @param style: CSS class of the link
    @type style: str

    @param separator: the separator between names.
    @type separator: str
    """

    out = []
    fulladdress = bfo.fields("111__")
    sday = ''
    smonth = ''
    syear = ''
    fday = ''
    fmonth = ''
    fyear = ''
    printaddress = ''

    for printaddress in fulladdress:
        if printaddress.has_key('d'):
            out.append(printaddress['d'])
            break
        else:
            if printaddress.has_key('x'):
                sdate = printaddress['x']
                sday = sdate[-2:]
                smonth = sdate[5:7]
                syear = sdate[:4]
            if printaddress.has_key('y'):
                fdate = printaddress['y']
                fday = fdate[-2:]
                fmonth = fdate[5:7]
                fyear = fdate[:4]

    if smonth == '01':
        smonth = smonth.replace('01', 'Jan')
    elif smonth == '02':
        smonth = smonth.replace('02', 'Feb')
    elif smonth == '03':
        smonth = smonth.replace('03', 'Mar')
    elif smonth == '04':
        smonth = smonth.replace('04', 'Apr')
    elif smonth == '05':
        smonth = smonth.replace('05', 'May')
    elif smonth == '06':
        smonth = smonth.replace('06', 'Jun')
    elif smonth == '07':
        smonth = smonth.replace('07', 'Jul')
    elif smonth == '08':
        smonth = smonth.replace('08', 'Aug')
    elif smonth == '09':
        smonth = smonth.replace('09', 'Sep')
    elif smonth == '10':
        smonth = smonth.replace('10', 'Oct')
    elif smonth == '11':
        smonth = smonth.replace('11', 'Nov')
    elif smonth == '12':
        smonth = smonth.replace('12', 'Dec')

    if fmonth == '01':
        fmonth = fmonth.replace('01', 'Jan')
    elif fmonth == '02':
        fmonth = fmonth.replace('02', 'Feb')
    elif fmonth == '03':
        fmonth = fmonth.replace('03', 'Mar')
    elif fmonth == '04':
        fmonth = fmonth.replace('04', 'Apr')
    elif fmonth == '05':
        fmonth = fmonth.replace('05', 'May')
    elif fmonth == '06':
        fmonth = fmonth.replace('06', 'Jun')
    elif fmonth == '07':
        fmonth = fmonth.replace('07', 'Jul')
    elif fmonth == '08':
        fmonth = fmonth.replace('08', 'Aug')
    elif fmonth == '09':
        fmonth = fmonth.replace('09', 'Sep')
    elif fmonth == '10':
        fmonth = fmonth.replace('10', 'Oct')
    elif fmonth == '11':
        fmonth = fmonth.replace('11', 'Nov')
    elif fmonth == '12':
        fmonth = fmonth.replace('12', 'Dec')

    if printaddress in fulladdress:
        if not printaddress.has_key('d'):
            if syear == fyear:
                if smonth == fmonth:
                    ##year matches. month matches
                    out.append(sday+'-'+fday+' '+fmonth+' '+fyear)
                else:
                    ##year matches. month doesnt
                    out.append(sday+' '+smonth+' - '+fday+' '+fmonth+' '+fyear)
            if not syear == fyear and not smonth == fmonth:
                ##year doesnt match. dont test month
                out.append(sday+' '+smonth+' '+syear+' - '+fday+' '+fmonth+' '+fyear)
    return separator.join(out)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
