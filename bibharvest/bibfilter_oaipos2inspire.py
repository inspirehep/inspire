#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
    name:           bibfilter_oaipos2inspire
    description:    Program to filter and analyse MARCXML records
                    from PoS oaiharvest, download the fulltexs,
                    and create the xml files for bibupload.

                    Based on bibfilter_oaicds2inspire
"""
from __future__ import print_function

import sys
import requests
import urllib

from tempfile import mkdtemp
from os import remove
from os.path import (join,
                     basename)
from shutil import copy
from bs4 import BeautifulSoup
from datetime import datetime
from xml.dom.minidom import parse
from harvestingkit.bibrecord import (record_add_field,
                                     record_xml_output)
from invenio.filedownloadutils import (download_url,
                                       InvenioFileDownloadError)
from invenio.config import (CFG_TMPSHAREDDIR,
                            CFG_SITE_SUPPORT_EMAIL)
from invenio.search_engine import perform_request_search
from invenio.mailutils import send_email
from invenio.bibtask import write_message
try:
    from invenio.config import CFG_POSHARVEST_EMAIL
except ImportError:
    CFG_POSHARVEST_EMAIL = CFG_SITE_SUPPORT_EMAIL
try:
    from invenio.config import CFG_POS_OUT_DIRECTORY
except ImportError:
    CFG_POS_OUT_DIRECTORY = join(CFG_TMPSHAREDDIR, 'fulltexts')
try:
    from invenio.config import CFG_POS_DEBUG
except ImportError:
    CFG_POS_DEBUG = False

from harvestingkit.pos_package import PosPackage
from invenio.apsharvest_utils import (create_work_folder,
                                      submit_records_via_ftp)

base_url = "http://pos.sissa.it/contribution?id="


def main(args):
    """Run the filtering."""
    if len(args) != 1:
        print("Usage: python bibfilter_oaipos2inspire.py input_filename")
        sys.exit(1)
    input_filename = args[0]

    out_folder = create_work_folder(CFG_POS_OUT_DIRECTORY)

    insert_records = []
    append_records = []
    error_records = []
    files_uploaded = []

    pos = PosPackage()
    xml_doc = parse(input_filename)
    for record in xml_doc.getElementsByTagName('record'):
        rec = pos.get_record(record)
        identifier = pos.get_identifier()
        conference = identifier.split(':')[2]
        conference = conference.split('/')[0]
        contribution = identifier.split(':')[2]
        contribution = contribution.split('/')[1]
        identifier = "PoS(%s)%s" % (conference, contribution)
        query = "773__p:pos 773__v:%s 773__c:%s" % \
                (conference.replace(' ', ''), contribution)
        print("Querying with: %s" % (query,))
        results = perform_request_search(p=query, of="id")

        url = base_url + identifier
        session = requests.session()
        r = session.get(url)
        parsed_html = BeautifulSoup(r.text)
        links = parsed_html.body.findAll('a')
        found = False

        for link in links:
            url = urllib.quote(link['href'], safe=":/")
            if url.endswith('.pdf'):
                found = True
                filename = join(out_folder, identifier + ".pdf")
                record_add_field(rec, '856', ind1='4', subfields=[
                    ('u', url),
                    ('y', 'PoS server')
                ])
                record_add_field(rec, 'FFT', subfields=[('a', filename),
                                                        ('t', 'PoS'),
                                                        ('d', 'Fulltext')])
                try:
                    print('Downloading ' + url)
                    download_url(url, "pdf", filename, 5, 60.0)
                    if results:
                        recid = results[0]
                        record_add_field(rec, '001', controlfield_value=recid)
                        append_records.append(rec)
                    else:
                        insert_records.append(rec)
                except InvenioFileDownloadError:
                    print("Download of %s failed" % (url,))
                break
        if not found:
            error_records.append(rec)

        # upload to FTP
        if not CFG_POS_DEBUG:
            tempfile_path = join(mkdtemp(), "{0}.xml".format(contribution))
            with open(tempfile_path, 'w') as tempfile:
                tempfile.write(record_xml_output(rec))
            submit_records_via_ftp(tempfile_path, conference)
            files_uploaded.append('%s/%s.xml' % (conference, contribution))
            remove(tempfile_path)

    insert_filename = "%s.insert.xml" % (input_filename,)
    append_filename = "%s.append.xml" % (input_filename,)
    errors_filename = "%s.errors.xml" % (input_filename,)

    created_files = []

    if write_record_to_file(insert_filename, insert_records):
        copy(insert_filename, out_folder)
        created_files.append(join(out_folder, basename(insert_filename)))
    if write_record_to_file(append_filename, append_records):
        copy(append_filename, out_folder)
        created_files.append(join(out_folder, basename(append_filename)))
    if write_record_to_file(errors_filename, error_records):
        copy(errors_filename, out_folder)
        created_files.append(join(out_folder, basename(errors_filename)))

    total_records = len(append_records) + len(insert_records) + len(error_records)
    subject = "PoS Harvest results: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = """
    Total of %d records processed:

    %d new records,
    %d records already existing in the system,
    %d records that failed to retrieve the fulltext

    Location of new records:
    %s
    """ % \
           (total_records,
            len(insert_records),
            len(append_records),
            len(error_records),
            "\n".join(created_files))
    if files_uploaded:
        body += "\nFiles uploaded:"
        for fl in files_uploaded:
            body += "\n\t%s file uploaded on the FTP Server\n" % (fl,)
    write_message(subject)
    write_message(body)
    if not send_email(CFG_SITE_SUPPORT_EMAIL,
                      CFG_POSHARVEST_EMAIL,
                      subject,
                      body):
        print("ERROR: Mail not sent")
    else:
        print("Mail sent to %s" % (CFG_POSHARVEST_EMAIL,))


def write_record_to_file(filename, record_list):
    """Write a new MARCXML file to specified path from BibRecord list."""
    if len(record_list) > 0:
        out = []
        out.append("<collection>")
        for record in record_list:
            out.append(record_xml_output(record))
        out.append("</collection>")
        if len(out) > 2:
            file_fd = open(filename, 'w')
            file_fd.write("\n".join(out))
            file_fd.close()
            return True

if __name__ == '__main__':
    main(sys.argv[1:])
