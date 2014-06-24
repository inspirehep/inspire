#!/usr/bin/env python

# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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
import xml.dom.minidom
import traceback

from os import (remove,
                listdir,
                mkdir)
from datetime import datetime
from os.path import (join,
                     exists,
                     isfile,
                     getsize)
from zipfile import (ZipFile,
                     BadZipfile)
from MySQLdb import ProgrammingError

from invenio.dbquery import run_sql
from invenio.mailutils import send_email
from invenio.filedownloadutils import (download_url,
                                       InvenioFileDownloadError)
from harvestingkit.elsevier_package import ElsevierPackage
from invenio.search_engine import perform_request_search
from invenio.apsharvest_utils import (create_work_folder,
                                      submit_records_via_ftp)
from invenio.config import (CFG_TMPSHAREDDIR,
                            CFG_SITE_SUPPORT_EMAIL)
try:
    from invenio.config import CFG_CONSYNHARVEST_EMAIL
except ImportError:
    CFG_CONSYNHARVEST_EMAIL = CFG_SITE_SUPPORT_EMAIL
from invenio.bibtask import (task_update_status,
                             write_message,
                             task_update_progress,
                             task_sleep_now_if_required)
try:
    from invenio.config import CFG_CONSYN_OUT_DIRECTORY
except ImportError:
    CFG_CONSYN_OUT_DIRECTORY = join(CFG_TMPSHAREDDIR, "consynharvest")
from invenio.config import CFG_CONSYN_ATOM_KEY

INTERESTING_DOCTYPES = ['fla', 'add', 'chp', 'err', 'rev', 'sco', 'ssu', 'pub']


def bst_consyn_harvest(feed=None, package=None, package_list=None,
                       batch_size='500', delete_zip='False', upload_FTP='True'):
    """ Task to convert xml files from consyn.elsevier.com to Marc xml files.
    There are three execution modes:
    1. Download from an atom feed.
    2. Extract a zip package.
    3. Extract a list of zip packages.

    :param feed: The URL of the atom feed to download.
    :type feed: string

    :param package: A path to a zip package
    :type package: string

    :param package_list: A path to a file with a list of paths to zip packages
    :type package_list: string

    :param batch_size: The number of records contained in each output file
    :type batch_size: string representation of an integer

    :param delete_zip: Flag to indicate if the downloaded zip files
                       should be kept on the disk or not
    :type delete_zip: string representation of a boolean

    :param upload_FTP: Flag to indicate whether the result files
                       should be uploaded to the FTP server
    :type upload_FTP: string representation of a boolean
    """
    if not feed:
        feed = "https://consyn.elsevier.com/batch/atom?key=%s" % \
               (CFG_CONSYN_ATOM_KEY,)
    new_files = []
    new_sources = []

    try:
        batch_size = int(batch_size)
    except ValueError:
        batch_size = 500
        write_message('Warning batch_size parameter is not a valid integer\n' +
                      'the default value \'500\' has been used!\n')
    if delete_zip.lower() == 'true':
        delete_zip = True
    elif delete_zip.lower() == 'false':
        delete_zip = False
    else:
        delete_zip = False
        write_message('Warning delete_zip parameter is not a valid Boolean (True/False)\n' +
                      'the default value \'False\' has been used!\n')
    if upload_FTP.lower() == 'true':
        upload_FTP = True
    elif upload_FTP.lower() == 'false':
        upload_FTP = False
    else:
        upload_FTP = True
        write_message('Warning upload_FTP parameter is not a valid Boolean (True/False)\n' +
                      'the default value \'True\' has been used!\n')

    out_folder = create_work_folder(CFG_CONSYN_OUT_DIRECTORY)

    try:
        run_sql("SELECT filename FROM CONSYNHARVEST")
    except ProgrammingError:
        # Table missing, create it.
        run_sql("CREATE TABLE CONSYNHARVEST ("
                "filename VARCHAR(100) NOT NULL PRIMARY KEY,"
                "date VARCHAR(50),"
                "size VARCHAR(30) );")

    if not package and not package_list:
        download_feed(feed, batch_size, delete_zip, new_sources, out_folder)
    elif package:
        extract_package(package, batch_size, delete_zip, out_folder)
    elif package_list:
        extract_multiple_packages(package_list, batch_size,
                                  delete_zip, new_sources,
                                  out_folder)

    task_sleep_now_if_required(can_stop_too=True)
    consyn_files = join(out_folder, "consyn-files")
    consyn_files = consyn_files.lstrip()
    els = ElsevierPackage(path="whatever", CONSYN=True)
    task_update_progress("Converting files 2/2...")
    fetch_xml_files(consyn_files, els, new_files)
    task_sleep_now_if_required(can_stop_too=False)
    create_collection(batch_size, new_files, new_sources, out_folder, upload_FTP)


def extractAll(zipName, delete_zip, directory):
    """Unzip a zip file"""
    write_message("Unziping: " + zipName + "\n")
    z = ZipFile(zipName)
    for f in z.namelist():
        extract_fld = join(directory, "consyn-files")
        extract_fld = extract_fld.lstrip()
        if not exists(join(extract_fld, f)):
            z.extract(f, extract_fld)
    if delete_zip:
        #delete the zip file after the extraction
        write_message("Deleting zip file: " + zipName + "\n")
        remove(zipName)


def fetch_xml_files(folder, els, new_files):
    """Recursively gets the downloaded xml files
    converts them to marc xml format and stores them
    in the same directory with the name "upload.xml"."""
    if exists(folder):
        for subfolder in listdir(folder):
            subfolder = join(folder, subfolder).lstrip()
            if isfile(subfolder):
                if not subfolder.endswith('upload.xml'):
                    folders = subfolder.split('/')
                    folders[-1] = 'upload.xml'
                    file_loc = "/".join(folders)
                    if not exists(file_loc):
                        xmlFile = open(subfolder, "r")
                        xmlString = xmlFile.read()
                        xmlFile.close()
                        dom_xml = xml.dom.minidom.parseString(xmlString)
                        doi = els.get_publication_information(dom_xml)[-1]
                        write_message("DOI in record: %s" % (doi,))
                        res = perform_request_search(p="doi:%s" % (doi,),
                                                     of="id")
                        if not res:
                            write_message("DOI not found")
                            doctype = els.get_doctype(dom_xml).lower()
                            #ignore index pages
                            if doctype in INTERESTING_DOCTYPES:
                                marcfile = open(file_loc, 'w')
                                marcfile.write(els.get_record(subfolder))
                                marcfile.close()
                                new_files.append(file_loc)
                                task_sleep_now_if_required(can_stop_too=False)
                        else:
                            write_message("DOI found: %s" % (res,))
            else:
                fetch_xml_files(subfolder, els, new_files)


def download_feed(feed, batch_size, delete_zip, new_sources,
                  directory):
    """ Get list of entries from XML document """
    xmlString = ""
    try:
        task_update_progress("Downloading and extracting files 1/2...")
        result_path = download_url(url=feed,
                                   retry_count=5,
                                   timeout=60.0)
        try:
            result_file = open(result_path, 'r')
            xmlString = result_file.read()
        finally:
            result_file.close()
            remove(result_path)
    except InvenioFileDownloadError as err:
        write_message("URL could not be opened: %s" % (feed,))
        write_message(str(err))
        write_message(traceback.format_exc()[:-1])
        task_update_status("CERROR")
        return

    dom = xml.dom.minidom.parseString(xmlString)
    entries = dom.getElementsByTagName("entry")
    downloaded_files = []
    for tup in run_sql("SELECT filename FROM CONSYNHARVEST"):
        downloaded_files.append(tup[0])

    # Loop through entries
    for entry in entries:
        # Get URL and filename
        fileUrl = entry.getElementsByTagName("link")[0].getAttribute("href")
        fileName = entry.getElementsByTagName("title")[0].firstChild.data
        updated = entry.getElementsByTagName("updated")[0].firstChild.data
        # Output location is directory + filename
        outFilename = join(directory, fileName)
        outFilename = outFilename.lstrip()

        #file has already been fetched
        if outFilename in downloaded_files:
            write_message("Not downloading %s, already found %s\n" %
                          (fileUrl, outFilename))
        else:
            try:
                write_message("Downloading %s to %s\n" % (fileUrl, outFilename))
                download_url(fileUrl, "zip", outFilename, 5, 60.0)
                new_sources.append(outFilename)
            except InvenioFileDownloadError as err:
                write_message("URL could not be opened: %s" % (fileUrl,))
                write_message(str(err))
                write_message(traceback.format_exc()[:-1])
                task_update_status("CERROR")
                continue
            size = getsize(outFilename)
            run_sql("INSERT INTO CONSYNHARVEST"
                    "(filename,date,size)"
                    "VALUES (%s,%s,%s)",
                    (outFilename, updated, size))
            try:
                extractAll(outFilename, delete_zip, directory)
            except BadZipfile:
                write_message("Error BadZipfile %s", (outFilename,))
                task_update_status("CERROR")
                remove(outFilename)
                run_sql("DELETE FROM CONSYNHARVEST"
                        "WHERE filename =%s",
                        (outFilename,))


def extract_package(package, batch_size, delete_zip, directory):
    try:
        extractAll(package, delete_zip, directory)
    except BadZipfile:
        write_message("Error BadZipfile %s", (package,))
        task_update_status("CERROR")
        remove(package)


def extract_multiple_packages(package_list, batch_size,
                              delete_zip, new_sources,
                              directory):
    packages_file = open(package_list, 'r')
    for line in packages_file:
        if line:
            extract_package(line, batch_size, delete_zip, directory)
            new_sources.append(line)


def create_collection(batch_size, new_files, new_sources,
                      directory, upload_FTP):
    """Create a single xml file "collection.xml"
    that contains all the records."""
    subject = "Consyn harvest results: %s" % \
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    if new_files:
        batch = 1
        counter = 0
        date = datetime.now().strftime("%Y.%m.%d")
        filepath = "elsevier-%s-%s.xml" % (date, batch)
        filepath = join(directory, filepath)
        filepath = filepath.lstrip()
        files_to_upload = []
        with open(filepath, 'w') as collection:
            collection.write("<collection>\n")
            for f in new_files:
                if counter == batch_size:
                    counter = 0
                    batch += 1
                    collection.write("</collection>")
                    collection.close()
                    files_to_upload.append(filepath)
                    filepath = "elsevier-%s-%s.xml" % (date, batch)
                    filepath = join(directory, filepath)
                    filepath = filepath.lstrip()
                    collection = open(filepath, 'w')
                    collection.write("<collection>\n")
                xmlFile = open(f, 'r')
                xmlString = xmlFile.read()
                xmlFile.close()
                collection.write(xmlString + '\n')
                counter += 1
            collection.write("</collection>")
            files_to_upload.append(filepath)
        body = ['From %s sources, found and converted %s records' % (len(new_sources), len(new_files)),
                '\t%s records ready to upload:\n' % ((batch - 1) * 500 + counter,)]
        if upload_FTP:
            body += ['\tFiles uploaded to Server:']
        else:
            body += ['\tFiles ready for upload:']
        for filepath in files_to_upload:
            try:
                submit_records_via_ftp(filepath)
                filename = filepath.split('/')[-1]
                body.append("\t%s (%s records)" % (filename, batch_size))
            except:
                write_message("Failed to upload %s to FTP server" % filepath)
        if len(body) > 3:
            #update the last line of the message
            body[-1] = "\t%s (%s records)" % (filename, counter)
            body = '\n'.join(body)

        write_message(subject)
        write_message(body)
        report_records_via_mail(subject, body)
    else:
        write_message(subject)
        write_message("No new files")


def report_records_via_mail(subject, body, toaddr=CFG_CONSYNHARVEST_EMAIL):
    """
    Performs the call to mailutils.send_email and reports the new
    records via e-mail to the desired recipient (CFG_CONSYNHARVEST_EMAIL).

    :param subject: email subject.
    :type subject: string

    :param body: email contents.
    :type body: string
    """
    if send_email(fromaddr=CFG_SITE_SUPPORT_EMAIL,
                  toaddr=toaddr,
                  subject=subject,
                  content=body):
        write_message("Mail sent to %r" % (toaddr,))
    else:
        write_message("ERROR: Cannot send mail.")


def create_folders(new_folder):
    """Create folders if they don't exist"""
    if not exists(new_folder):
        folders = new_folder.split("/")
        folder = "/"
        for i in range(1, len(folders)):
            folder = join(folder, folders[i]).strip()
            if not exists(folder):
                mkdir(folder)


if __name__ == "__main__":
    bst_consyn_harvest()
