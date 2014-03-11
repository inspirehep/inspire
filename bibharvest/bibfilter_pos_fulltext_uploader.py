#! /usr/bin/env python
"""
    name:           bibfilter_pos_fulltext_uploader
    decription:     Program to filter and analyse MARCXML records
                    from PoS oaiharvest, download the fulltexs,
                    and create the xml files for bibupload.

                    Based on bibfilter_oaicds2inspire
"""
import sys
import xml.dom.minidom
import requests
import urllib

from os import mkdir
from os.path import join, exists
from bs4 import BeautifulSoup
from xml.dom.minidom import Document
from datetime import datetime
from invenio.filedownloadutils import download_url, \
    InvenioFileDownloadError
from invenio.invenio_connector import InvenioConnector
from invenio.bibtask import write_message
from invenio.config import CFG_TMPSHAREDDIR, CFG_SITE_URL
try:
    from invenio.config import CFG_FULLTEXT_DOWNLOAD_DIR
except ImportError:
    CFG_FULLTEXT_DOWNLOAD_DIR = join(CFG_TMPSHAREDDIR, 'fulltexts')

base_url = "http://pos.sissa.it/contribution?id="


# ==============================| Main |==============================
def main(args):
    if len(args) != 1:
        write_message("usage: python bibfilter_pos_fulltext_uploader.py input_filename:")
        raise Exception("Wrong usage!!")
    input_filename = args[0]

    #create folders if they dont exist
    create_folders(CFG_FULLTEXT_DOWNLOAD_DIR)

    run = 1
    date = datetime.now().strftime("%Y.%m.%d")
    out_folder = join(CFG_FULLTEXT_DOWNLOAD_DIR, date + "-" + str(run))
    while(exists(out_folder)):
        run += 1
        out_folder = join(CFG_FULLTEXT_DOWNLOAD_DIR, date + "-" + str(run))

    mkdir(out_folder)

    # Hack to activate UTF-8
    reload(sys)
    sys.setdefaultencoding("utf8")
    assert sys.getdefaultencoding() == "utf8"

    inspire = InvenioConnector(CFG_SITE_URL)

    records = ''
    input_file = open(input_filename, 'r')
    try:
        dom = xml.dom.minidom.parseString(input_file.read())
        records = dom.getElementsByTagName('record')
    finally:
        input_file.close()

    #allready existing records
    append = open(input_filename + '.append.xml', 'w')
    #non existing records
    insert = open(input_filename + '.insert.xml', 'w')
    #fulltext not found
    not_found = open(input_filename + '.not_found.xml', 'w')

    try:
        insert.write('<collection>')
        not_found.write('<collection>')

        doc = Document()
        collection = doc.createElement('collection')
        for record in records:
            identifier, conference, contribution, date = get_information(record)
            query = "773__p:pos 773__v:%s 773__c:%s" % \
                    (conference.replace(' ', ''), contribution)
            results = inspire.search(p=query)

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
                    filename = join(out_folder, identifier + ".pdf")
                    datafield = doc.createElement("datafield")
                    datafield.setAttribute("ind1", '')
                    datafield.setAttribute("ind2", '')
                    datafield.setAttribute("tag", 'FFT')

                    subfield_a = doc.createElement("subfield")
                    subfield_a.setAttribute("code", 'a')
                    text = doc.createTextNode(filename)
                    subfield_a.appendChild(text)

                    subfield_t = doc.createElement("subfield")
                    subfield_t.setAttribute("code", 't')
                    text = doc.createTextNode("PoS")
                    subfield_t.appendChild(text)

                    subfield_d = doc.createElement("subfield")
                    subfield_d.setAttribute("code", 'd')
                    text = doc.createTextNode("Fulltext")
                    subfield_d.appendChild(text)

                    datafield.appendChild(subfield_a)
                    datafield.appendChild(subfield_t)
                    datafield.appendChild(subfield_d)
                    if results:
                        rec = doc.createElement('record')
                        collection.appendChild(rec)
                        recid = results[0]["001__"][0]

                        controlfield = doc.createElement('controlfield')
                        controlfield.setAttribute('tag', '001')
                        text = doc.createTextNode(recid)
                        controlfield.appendChild(text)
                        rec.appendChild(controlfield)

                        try:
                            write_message('downloading ' + url)
                            download_url(url, "pdf", filename, 5, 60.0)
                        except InvenioFileDownloadError:
                            write_message("Download of %s failed" % (url,))

                        rec.appendChild(datafield)
                    else:
                        record.appendChild(datafield)
                        insert.write(record.toprettyxml())
                    break
            if not found:
                not_found.write(record.toprettyxml())

        append.write(collection.toprettyxml())
        insert.write('</collection>')
        not_found.write('</collection>')
    finally:
        not_found.close()
        insert.close()
        append.close()


def get_information(record):
    identifier = ""
    conference = ""
    contribution = ""
    date = ""
    for child in record.childNodes:
        tag = child.getAttribute('tag')
        if tag == '035':
            for subfield in child.childNodes:
                if subfield.getAttribute('code') == 'a':
                    conference = subfield.firstChild.data.split(':')[2]
                    conference = conference.split('/')[0]
                    contribution = subfield.firstChild.data.split(':')[2]
                    contribution = contribution.split('/')[1]
                    identifier = "PoS(%s)%s" % (conference, contribution)
            record.removeChild(child)
        elif tag == '260':
            for subfield in child.childNodes:
                if subfield.getAttribute('code') == 'c':
                    date = subfield.firstChild.data[:10]
                    subfield.firstChild.data = date
    return identifier, conference, contribution, date


def create_folders(new_folder):
    #create folders if they dont exist
    if not exists(new_folder):
        folders = new_folder.split("/")
        folder = "/"
        for i in range(1, len(folders)):
            folder = join(folder, folders[i]).strip()
            if not exists(folder):
                mkdir(folder)


# ==============================| Init, innit? |==============================
if __name__ == '__main__':
    main(sys.argv[1:])
