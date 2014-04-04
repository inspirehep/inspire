#! /usr/bin/env python
"""
    name:           bibfilter_oaipos2inspire
    decription:     Program to filter and analyse MARCXML records
                    from PoS oaiharvest, download the fulltexs,
                    and create the xml files for bibupload.

                    Based on bibfilter_oaicds2inspire
"""
import sys
import requests
import urllib
from os import mkdir
from os.path import join, \
    exists
from shutil import copy
from bs4 import BeautifulSoup
from datetime import datetime
from xml.dom.minidom import parse
from invenio.bibrecord import record_add_field, \
    record_xml_output
from invenio.filedownloadutils import download_url, \
    InvenioFileDownloadError
from invenio.bibtask import write_message
from invenio.config import CFG_TMPSHAREDDIR, CFG_SITE_SUPPORT_EMAIL
from invenio.search_engine import perform_request_search
from invenio.mailutils import send_email
from harvestingkit.pos_package import PosPackage
try:
    from invenio.config import CFG_POSHARVEST_EMAIL
except ImportError:
    CFG_POSHARVEST_EMAIL = CFG_SITE_SUPPORT_EMAIL
try:
    from invenio.config import CFG_POS_OUT_DIRECTORY
except ImportError:
    CFG_POS_OUT_DIRECTORY = join(CFG_TMPSHAREDDIR, 'fulltexts')

base_url = "http://pos.sissa.it/contribution?id="


# ==============================| Main |==============================
def main(args):
    if len(args) != 1:
        write_message("usage: python bibfilter_oaipos2inspire.py input_filename")
        raise Exception("Wrong usage!!")
    input_file = args[0]

    #create folders if they dont exist
    create_folders(CFG_POS_OUT_DIRECTORY)

    run = 1
    date = datetime.now().strftime("%Y.%m.%d")
    out_folder = join(CFG_POS_OUT_DIRECTORY, date + "-" + str(run))
    while(exists(out_folder)):
        run += 1
        out_folder = join(CFG_POS_OUT_DIRECTORY, date + "-" + str(run))

    mkdir(out_folder)

    insert = []
    append = []
    not_found = []

    pos = PosPackage()
    xml_doc = parse(input_file)
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
        write_message("Querying with: %s" % (query,))
        results = perform_request_search(p=query, of="id")

        #harvest fulltext
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
                if results:
                    rec = {}
                filename = join(out_folder, identifier + ".pdf")
                record_add_field(rec, '856', ind1='4', subfields=[('u', url)])
                record_add_field(rec, 'FFT', subfields=[('a', filename),
                                                        ('t', 'PoS'),
                                                        ('o', 'INSPIRE-PUBLIC'),
                                                        ('d', 'Fulltext')])
                try:
                    write_message('downloading ' + url)
                    download_url(url, "pdf", filename, 5, 60.0)
                    if results:
                        recid = results[0]["001__"][0]
                        record_add_field(rec, '001', controlfield_value=recid)
                        append.append(record_xml_output(rec))
                    else:
                        insert.append(record_xml_output(rec))
                except InvenioFileDownloadError:
                    write_message("Download of %s failed" % (url,))
                break
        if not found:
            not_found.append(record_xml_output(rec))

    try:
        #allready existing records
        append_file = open(input_file + '.append.xml', 'w')
        #non existing records
        insert_file = open(input_file + '.insert.xml', 'w')
        #fulltext not found
        not_found_file = open(input_file + '.not_found.xml', 'w')
        append_file.write("<collection>\n" + "\n".join(append) + "\n</collection>")
        insert_file.write("<collection>\n" + "\n".join(insert) + "\n</collection>")
        not_found_file.write("<collection>\n" + "\n".join(not_found) + "\n</collection>")
    finally:
        not_found_file.close()
        insert_file.close()
        append_file.close()

    #keep a copy of the files on AFS
    copy(input_file + '.append.xml', out_folder)
    copy(input_file + '.insert.xml', out_folder)
    copy(input_file + '.not_found.xml', out_folder)

    total_records = len(append) + len(insert) + len(not_found)
    subject = "PoS Harvest results: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = """Total of %d records processed: \n
              %d new records,\n
              %d records already existing in the system,\n
              %d records that failed to retrieve the fulltext""" %\
           (total_records, len(insert), len(append), len(not_found))
    write_message(body)
    send_email(CFG_SITE_SUPPORT_EMAIL,
               CFG_POSHARVEST_EMAIL,
               subject,
               body)


def create_folders(new_folder):
    #create folders if they dont exist
    if not exists(new_folder):
        folders = new_folder.split("/")
        folder = "/"
        for i in range(1, len(folders)):
            folder = join(folder, folders[i]).strip()
            if not exists(folder):
                mkdir(folder)


if __name__ == '__main__':
    main(sys.argv[1:])
