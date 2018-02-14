# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2015, 2016, 2018 CERN.
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
""" BibFormat element - scans through all fields likely to create urls
(856, 773, etc) and creates and displays a list of those links.  Currently
does not include arXiv.
"""

from invenio.bibdocfile import bibdocfile_url_to_bibdoc
from invenio.config import CFG_SITE_URL
from invenio.messages import gettext_set_language

try:
    from invenio.config import CFG_BASE_URL
except ImportError:
    CFG_BASE_URL = CFG_SITE_URL


ADSABS = 'http://adsabs.harvard.edu/abs/'
CDS = 'http://cds.cern.ch/record/'
EUCLID = 'http://projecteuclid.org/'
HAL = 'https://hal.archives-ouvertes.fr/'
INIS = 'https://inis.iaea.org/search/search.aspx?orig_q='
KEK = 'https://lib-extopc.kek.jp/preprints/PDF'
MSNET = 'http://www.ams.org/mathscinet-getitem?mr='
OSTI = 'http://www.osti.gov/scitech/biblio/'
ZBLATT = 'http://www.zentralblatt-math.org/zmath/en/search/?an='


def format_element(bfo, default='', separator='; ', style='',
                   show_icons='no', prefix='', suffix=''):
    """ Creates html of links based on metadata
    @param separator (separates instances of links)
    @param prefix
    @param suffix
    @param show_icons default = no
    @param style options CSS style for link
    """
    _ = gettext_set_language(bfo.lang)
    if style != "":
        style = ' class="' + style + '"'

    links = []

    # ADS/CDS/KEKSCAN/INIS/HAL links
    # external identifiers in tag 035__a along with service label in 035__9
    identifiers = bfo.fields('035__')
    adslinked = False
    for ident in identifiers:
        provenance = ident.get('9', None)
        extid = ident.get('a', None)
        if provenance is None or extid is None:
            continue

        if provenance == 'KEKSCAN':
            extid = extid.replace("-", "")
            if len(extid) == 7 and not extid.startswith('19') and not extid.startswith('20'):
                year = '19' + extid[:2]
            elif len(extid) == 9:
                year = extid[:4]
                extid = extid[2:]
            else:
                # likely bad id
                continue
            yymm = extid[:4]
            links.append('<a%s href="%s/%s/%s/%s.pdf"> KEK scanned document</a>' %
                         (style, KEK, year, yymm, extid))
        elif provenance == 'CDS':
            links.append('<a%s href="%s%s"> CERN Document Server</a>' %
                         (style, CDS, extid))
        elif provenance == 'ADS':
            extid = extid.replace('&', '%26')  # A&A etc.
            links.append('<a%s href="%s%s"> ADS Abstract Service</a>' %
                         (style, ADSABS, extid))
            adslinked = True
        elif provenance == 'INIS':
            links.append('<a%s href="%s%s"> INIS Repository</a>' %
                         (style, INIS, extid))
        elif provenance == 'HAL':
            from invenio.webuser import isUserAdmin
            if isUserAdmin(bfo.user_info):
                links.append('<a %s href="%s%s"> HAL Archives Ouvertes</a>' %
                             (style, HAL, extid))

    # fallback ADS link via arXiv:e-print
    if not adslinked:
        identifiers = bfo.fields('037__')
        eprints = set()  # avoid duplicate links
        for ident in identifiers:
            if ident.get('9', '') == 'arXiv' \
               and ident.get('a', None) is not None:
                eprints.add(ident.get('a', ''))
        if eprints:
            adslinked = True
            for eprint in eprints:
                links.append('<a href="%s%s"> ADS Abstract Service</a>'
                             % (ADSABS, eprint))

    # external identifiers in tag 035__a along with service label in 035__9
    urls = bfo.fields('035__')
    for url in urls:
        provenance = url.get('9', None)
        extid = url.get('a', None)
        if provenance is None or extid is None:
            continue

        provenance = provenance.lower()
        if provenance == "msnet":
            links.append('<a%s href="%s%s"> AMS MathSciNet</a>' %
                         (style, MSNET, extid))
        elif provenance == "zblatt":
            links.append('<a%s href="%s%s"> zbMATH</a>' %
                         (style, ZBLATT, extid))
        elif provenance == "euclid":
            links.append('<a%s href="%s%s"> Project Euclid</a>' %
                         (style, EUCLID, extid))
        elif provenance == "osti":
            links.append('<a%s href="%s%s"> OSTI.gov Server</a>' %
                         (style, OSTI, extid))

    # now look for explicit URLs
    # might want to check that we aren't repeating things from above...
    # Note: excluding self-links
    urls = bfo.fields('8564_')
    allowed_doctypes = ["INSPIRE-PUBLIC", "SCOAP3", "PoS"]
    for url in urls:
        if url.get("y", "").lower() not in \
           ("adsabs", "euclid", "msnet", "osti", "zblatt"):
            if '.png' not in url.get('u', '') and not (
                    url.get('y', '').lower().startswith("fermilab") and
                    bfo.field("710__g").lower() in
                    ('atlas collaboration', 'cms collaboration')):
                if url.get('y', '').upper() != "DURHAM":
                    if url.get("u", '') and \
                       url.get('y', 'Fulltext').upper() != "DOI" and not \
                       url.get('u', '').startswith(CFG_SITE_URL):
                        links.append('<a %s href="%s">%s</a>' %
                                     (style, url.get("u", ''),
                                      _lookup_url_name(bfo, url.get(
                                          'y', 'Fulltext'))))
                    elif url.get("u", '').startswith(CFG_SITE_URL) and \
                        (url.get("u", '').lower().endswith(".pdf") or
                         url.get("u", '').lower().endswith(
                             '.pdf?subformat=pdfa')) and \
                            bibdocfile_url_to_bibdoc(url.get('u')).doctype in \
                            allowed_doctypes:
                        links.append('<a %s href="%s">%s</a>' %
                                     (style, url.get("u", ''),
                                      _lookup_url_name(bfo, url.get(
                                          'y', 'Fulltext'))))

    # put it all together
    if links:
        if show_icons.lower() == 'yes':
            img = '<img style="border:none" \
            src="%s/img/file-icon-text-12x16.gif" alt="%s"/>' \
            % (CFG_BASE_URL, _("Download fulltext"))
            links = [img + '<small>' + link + '</small>' for link in links]
        return prefix + separator.join(links) + suffix
    else:
        return default


def _lookup_url_name(bfo, abbrev=''):
    """ Finds the display name for the url, based on an
    abbrev in record.
    Input:  bfo, abbrev  (abbrev is PHRVA-D, etc)
    Output: display string  (Phys Rev D Server)
    """
    if abbrev is None:
        abbrev = ''
    return bfo.kb('WEBLINKS', abbrev, 'Link to ' + abbrev)


# we know the argument is unused, thanks
# pylint: disable=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable=W0613
