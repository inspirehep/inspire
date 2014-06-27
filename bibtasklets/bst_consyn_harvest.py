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
import traceback
from xml.dom.minidom import (parse,
                             parseString)
from os import (remove,
                walk,
                rmdir)
from datetime import datetime
from os.path import (join,
                     exists,
                     dirname)
from zipfile import (ZipFile,
                     BadZipfile)
from invenio.filedownloadutils import (download_url,
                                       InvenioFileDownloadError)
from harvestingkit.elsevier_package import ElsevierPackage
from invenio.search_engine import perform_request_search
from invenio.apsharvest_utils import (submit_records_via_ftp,
                                      locate,
                                      submit_records_via_mail,
                                      create_work_folder)
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

    if not exists(CFG_CONSYN_OUT_DIRECTORY):
        rmdir(create_work_folder(CFG_CONSYN_OUT_DIRECTORY))
    out_folder = CFG_CONSYN_OUT_DIRECTORY

    if not package and not package_list:
        download_feed(feed, batch_size, delete_zip, new_sources, out_folder)
    else:
        xml_files = []
        if package:
            xml_files = extract_package(package, batch_size, delete_zip, out_folder)
        elif package_list:
            xml_files = extract_multiple_packages(
                package_list, batch_size,
                delete_zip, new_sources,
                out_folder
            )
        # Remove the files to re-convert and add to bundle
        for xml_file in xml_files:
            file_to_look_for = join(dirname(xml_file), "upload.xml")
            if exists(file_to_look_for):
                remove(file_to_look_for)

    task_sleep_now_if_required(can_stop_too=True)
    consyn_files = join(out_folder, "consyn-files")
    consyn_files = consyn_files.lstrip()
    els = ElsevierPackage(CONSYN=True)
    task_update_progress("Converting files 2/2...")
    fetch_xml_files(consyn_files, els, new_files)
    task_sleep_now_if_required(can_stop_too=False)
    create_collection(batch_size, new_files, new_sources, out_folder, upload_FTP)


def extractAll(zipName, delete_zip, directory):
    """Unzip a zip file"""
    write_message("Unzipping: " + zipName + "\n")
    z = ZipFile(zipName)
    xml_files_extracted = []
    for f in z.namelist():
        if f.endswith(".xml"):
            xml_files_extracted.append(f)
        extract_fld = join(directory, "consyn-files")
        extract_fld = extract_fld.lstrip()
        if not exists(join(extract_fld, f)):
            z.extract(f, extract_fld)
    if delete_zip:
        #delete the zip file after the extraction
        write_message("Deleting zip file: " + zipName + "\n")
        remove(zipName)
    return xml_files_extracted


def fetch_xml_files(folder, els, new_files):
    """Recursively gets the downloaded xml files
    converts them to marc xml format and stores them
    in the same directory with the name "upload.xml"."""
    for path, folders, files in walk(folder):
        for fl in files:
            if fl != 'upload.xml':
                file_loc = join(path, 'upload.xml')
                if not exists(file_loc):
                    record_path = join(path, fl)
                    dom_xml = parse(record_path)
                    doi = els.get_publication_information(dom_xml)[-1]
                    res = None
                    if doi:
                        write_message("DOI in record: %s" % (doi,))
                        res = perform_request_search(p="doi:%s" % (doi,),
                                                     of="id")
                    if not res:
                        write_message("DOI not found in record: \n%s" % (join(path, fl),))
                        doctype = els.get_doctype(dom_xml).lower()
                        #ignore index pages
                        if doctype in INTERESTING_DOCTYPES:
                            marcfile = open(file_loc, 'w')
                            marcfile.write(els.get_record(record_path))
                            marcfile.close()
                            new_files.append(file_loc)
                            task_sleep_now_if_required(can_stop_too=False)
                        else:
                            write_message("DOI found: %s" % (res,))


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

    dom = parseString(xmlString)
    entries = dom.getElementsByTagName("entry")

    # Loop through entries
    for entry in entries:
        # Get URL and filename
        fileUrl = entry.getElementsByTagName("link")[0].getAttribute("href")
        fileName = entry.getElementsByTagName("title")[0].firstChild.data

        # Output location is directory + filename
        outFilename = join(directory, fileName)
        outFilename = outFilename.lstrip()

        # Check if file has already been fetched
        existing_files = list(locate(fileName, root=CFG_CONSYN_OUT_DIRECTORY))

        if len(existing_files) == 1:
            write_message("Not downloading %s, already found %s in %s\n" %
                          (fileUrl, existing_files[0], outFilename))
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
            try:
                extractAll(outFilename, delete_zip, directory)
            except BadZipfile:
                write_message("Error BadZipfile %s", (outFilename,))
                task_update_status("CERROR")
                remove(outFilename)


def extract_package(package, batch_size, delete_zip, directory):
    try:
        return extractAll(package, delete_zip, directory)
    except BadZipfile:
        write_message("Error BadZipfile %s", (package,))
        task_update_status("CERROR")
        remove(package)


def extract_multiple_packages(package_list, batch_size,
                              delete_zip, new_sources,
                              directory):

    xml_files_extracted = []
    with open(package_list, 'r') as package_file:
        for line in package_file:
            line = line.strip()
            if line:
                xml_files_extracted.extend(extract_package(
                    line, batch_size, delete_zip, directory)
                )
                new_sources.append(line)
    return xml_files_extracted


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
                    filepath = join(directory, filepath).lstrip()
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
        if submit_records_via_mail(subject, body, CFG_CONSYNHARVEST_EMAIL):
            write_message("Mail sent to %r" % (CFG_CONSYNHARVEST_EMAIL,))
        else:
            write_message("ERROR: Cannot send mail.")
    else:
        write_message(subject)
        write_message("No new files")


if __name__ == "__main__":
    bst_consyn_harvest()
