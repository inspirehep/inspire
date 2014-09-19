#!/usr/bin/env python

# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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
import traceback
from xml.dom.minidom import parse
from os import (remove,
                makedirs)
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
                                      submit_records_via_mail)
from invenio.config import (CFG_TMPSHAREDDIR,
                            CFG_SITE_SUPPORT_EMAIL)
try:
    from invenio.config import CFG_CONSYNHARVEST_EMAIL
except ImportError:
    CFG_CONSYNHARVEST_EMAIL = CFG_SITE_SUPPORT_EMAIL
from invenio.bibtask import (task_update_status,
                             write_message,
                             task_update_progress)
try:
    from invenio.config import CFG_CONSYN_OUT_DIRECTORY
except ImportError:
    CFG_CONSYN_OUT_DIRECTORY = join(CFG_TMPSHAREDDIR, "consynharvest")
from invenio.config import CFG_CONSYN_ATOM_KEY
from invenio.refextract_api import (
    extract_references_from_string_xml as refextract
)
from invenio.refextract_kbs import get_kbs

INTERESTING_DOCTYPES = ['fla', 'add', 'chp', 'err', 'rev', 'sco', 'ssu', 'pub']


class StatusCodes(object):

    """Error codes."""

    DOCTYPE_WRONG = "Wrong doctype"
    DOI_FOUND = "DOI found"
    CONVERSION_ERROR = "Error while converting"
    OK = "Record OK"

_errors_detected = []


def bst_consyn_harvest(feed_url=None, package=None, feed_file=None,
                       package_list_file=None, batch_size='500',
                       delete_zip='False', submit='False'):
    """ Task to convert xml files from consyn.elsevier.com to Marc xml files.
    There are four execution modes:
    1. Download from an atom feed url.
    2. Extract and convert a zip package.
    3. Download from an atom feed file.
    4. Extract and convert a list of zip packages.

    The feed is stored to the file system under the folder feeds.
    If no errors occur during the execution of the tasklet the feed
    is deleted. Records may be recovered running the tasklet again with
    the modes 2, 3 or 4.

    :param feed_url: A URL to the atom feed.
    :type feed: string.

    :param package: A path to a zip package.
    :type package: string.

    :param package: A path to an atom feed file.
    :type package: string.

    :param package_list_file: A path to a file with a list of paths
                              to zip packages. The file must contain
                              the path to each package in a different
                              line.
    :type package_list_file: string.

    :param batch_size: The number of records contained in each output file.
    :type batch_size: string representation of an integer.

    :param delete_zip: Flag to indicate if the downloaded zip files
                       should be kept on the disk or not.
    :type delete_zip: string representation of a boolean.

    :param submit: Flag to indicate whether the result files
                       should be submited by email and uploaded
                       to FTP server.
    :type submit: string representation of a boolean.
    """
    if not feed_url:
        feed_url = "https://consyn.elsevier.com/batch/atom?key=%s" % \
                   (CFG_CONSYN_ATOM_KEY,)
    new_files = []
    new_sources = []
    feed_location = ''

    try:
        batch_size = int(batch_size)
    except ValueError:
        batch_size = 500
        write_message('Warning batch_size parameter is not a valid integer\n'
                      'the default value \'500\' has been used!\n')
    if delete_zip.lower() == 'true':
        delete_zip = True
    elif delete_zip.lower() == 'false':
        delete_zip = False
    else:
        delete_zip = False
        write_message('Warning delete_zip parameter is not'
                      ' a valid Boolean (True/False)\n'
                      'the default value \'False\' has been used!\n')
    if submit.lower() == 'true':
        submit = True
    elif submit.lower() == 'false':
        submit = False
    else:
        submit = False
        write_message('Warning upload_FTP parameter is not'
                      ' a valid Boolean (True/False)\n'
                      'the default value \'False\' has been used!\n')

    if not exists(CFG_CONSYN_OUT_DIRECTORY):
        makedirs(CFG_CONSYN_OUT_DIRECTORY)
    out_folder = CFG_CONSYN_OUT_DIRECTORY
    journal_mappings = get_kbs()['journals'][1]
    els = ElsevierPackage(CONSYN=True,
                          journal_mappings=journal_mappings)

    consyn_files = join(out_folder, "consyn-files")
    consyn_files = consyn_files.lstrip()

    if package:
        xml_files = extract_package(package, batch_size, delete_zip,
                                    out_folder, new_sources)
    elif package_list_file:
        package_list = []
        with open(package_list_file, 'r') as package_file:
            for line in package_file:
                line = line.strip()
                if line:
                    package_list.append(line)
        xml_files = extract_multiple_packages(
            package_list, batch_size,
            delete_zip, new_sources,
            out_folder
        )
    elif feed_file:
        entries = parse_feed(feed_file)
        links = map(lambda a: a[0], entries)
        package_list = map(lambda a: a[1], entries)
        package_list = map(lambda a: join(CFG_CONSYN_OUT_DIRECTORY, a),
                           package_list)
        for package in package_list:
            if not exists(package):
                index = package_list.index(package)
                link = links[index]
                try:
                    message = ("Downloading %s to %s\n" % (link,
                                                           package))
                    write_message(message)
                    download_url(link, "zip", package, 5, 60.0)
                    package_list.append(package)
                except InvenioFileDownloadError as err:
                    message = "URL could not be opened: " + link
                    write_message(message)
                    write_message(str(err))
                    write_message(traceback.format_exc()[:-1])
                    task_update_status("CERROR")
                    continue
            xml_files = extract_multiple_packages(
                package_list, batch_size,
                delete_zip, new_sources,
                out_folder
            )
    else:
        feeds_folder = join(CFG_CONSYN_OUT_DIRECTORY, 'feeds')
        if not exists(feeds_folder):
            makedirs(feeds_folder)
        date = datetime.now().strftime("%Y.%m.%d")
        feed_location = "feed-%s.xml" % date
        feed_location = join(feeds_folder, feed_location)
        xml_files = download_feed(feed_url, batch_size, delete_zip,
                                  new_sources, out_folder, feed_location)
    task_update_progress("Converting files 2/3...")
    results = convert_files(xml_files, els, prefix=consyn_files)
    for dummy, (status_code, result) in results.iteritems():
        if status_code == StatusCodes.OK:
            new_files.append(result)
    task_update_progress("Compiling output 3/3...")
    create_collection(batch_size, new_files, new_sources,
                      out_folder, submit)
    if feed_location and not _errors_detected:
        remove(feed_location)
    for error in _errors_detected:
        write_message(str(error))


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


def convert_files(xml_files, els, prefix=""):
    """Convert the list of publisher XML to MARCXML using given instance."""
    results = {}
    for xml_file in xml_files:
        full_xml_filepath = join(prefix, xml_file)
        dom_xml = parse(full_xml_filepath)
        doi = els.get_publication_information(dom_xml)[-1]
        res = None
        if doi:
            write_message("DOI in record: {0}".format(doi))
            res = perform_request_search(p="doi:{0}".format(doi),
                                         of="id")
        else:
            write_message('DOI not found in record:'
                          ' \n{0}'.format(full_xml_filepath))
        if res:
            write_message("DOI found in: {0}".format(res))
            results[full_xml_filepath] = (StatusCodes.DOI_FOUND, res)
        else:
            doctype = els.get_doctype(dom_xml).lower()
            if doctype in INTERESTING_DOCTYPES:
                new_full_xml_filepath = join(dirname(full_xml_filepath),
                                             "upload.xml")
                try:
                    converted_xml = els.get_record(
                        full_xml_filepath, refextract_callback=refextract)
                except Exception as e:
                    _errors_detected.append(e)
                    error_trace = traceback.format_exc()
                    # Some error happened, lets gracefully quit
                    results[full_xml_filepath] = (StatusCodes.CONVERSION_ERROR,
                                                  error_trace)
                    write_message('Error converting:'
                                  ' \n {0}'.format(error_trace))
                    continue
                if not exists(new_full_xml_filepath):
                    with open(new_full_xml_filepath, "w") as marcfile:
                        marcfile.write(converted_xml)
                results[full_xml_filepath] = (StatusCodes.OK,
                                              new_full_xml_filepath)
            else:
                results[full_xml_filepath] = (StatusCodes.DOCTYPE_WRONG,
                                              doctype)
                write_message("Doctype not interesting: {0}".format(doctype))
    return results


def parse_feed(feed_file):
    """ Parses the atom feed and returns a list
    of tuples with link and the package name. """
    dom = parse(feed_file)
    entries = dom.getElementsByTagName("entry")
    files = []
    # Loop through entries
    for entry in entries:
        # Get URL and filename
        fileUrl = entry.getElementsByTagName("link")[0].getAttribute("href")
        fileName = entry.getElementsByTagName("title")[0].firstChild.data
        files.append((fileUrl, fileName))
    return files


def download_feed(feed_url, batch_size, delete_zip, new_sources,
                  directory, feed_location):
    """ Get list of entries from XML document """
    try:
        task_update_progress("Downloading and extracting files 1/2...")
        result_path = download_url(url=feed_url,
                                   content_type="xml",
                                   download_to_file=feed_location,
                                   retry_count=5,
                                   timeout=60.0)
    except InvenioFileDownloadError as err:
        _errors_detected.append(err)
        write_message("URL could not be opened: %s" % (feed_url,))
        write_message(str(err))
        write_message(traceback.format_exc()[:-1])
        task_update_status("CERROR")
        return
    xml_files = []
    entries = parse_feed(result_path)
    for fileUrl, fileName in entries:
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
                write_message("Downloading %s to %s\n" % (fileUrl,
                                                          outFilename))
                download_url(fileUrl, "zip", outFilename, 5, 60.0)
                new_sources.append(outFilename)
            except InvenioFileDownloadError as err:
                _errors_detected.append(err)
                write_message("URL could not be opened: %s" + fileUrl)
                write_message(str(err))
                write_message(traceback.format_exc()[:-1])
                task_update_status("CERROR")
                continue
            try:
                xml_files.extend(extractAll(outFilename,
                                            delete_zip,
                                            directory))
            except BadZipfile:
                _errors_detected.append(err)
                write_message("Error BadZipfile %s", (outFilename,))
                task_update_status("CERROR")
                remove(outFilename)
    return xml_files


def extract_package(package, batch_size, delete_zip,
                    directory, new_sources):
    try:
        new_sources.append(package)
        return extractAll(package, delete_zip, directory)
    except BadZipfile as err:
        _errors_detected.append(err)
        write_message("Error BadZipfile %s", (package,))
        task_update_status("CERROR")
        remove(package)


def extract_multiple_packages(package_list, batch_size,
                              delete_zip, new_sources,
                              directory):
    xml_files_extracted = []
    for package in package_list:
        xml_files_extracted.extend(extract_package(
            package, batch_size, delete_zip, directory, new_sources)
        )
    return xml_files_extracted


def create_collection(batch_size, new_files, new_sources,
                      directory, submit):
    """Create a single xml file "collection.xml"
    that contains all the records."""
    subject = "Consyn harvest results: %s" % \
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    batch = 1
    counter = 1
    date = datetime.now().strftime("%Y.%m.%d")
    files_to_upload = []
    collection = None
    for filename in new_files:
        if counter == 1:
            filepath = "elsevier-%s-%s.xml" % (date, batch)
            filepath = join(directory, filepath)
            filepath = filepath.lstrip()
            collection = open(filepath, 'w')
            collection.write("<collection>\n")
        with open(filename) as f:
            collection.write(f.read() + '\n')
            counter += 1
        if counter == batch_size:
            collection.write("</collection>")
            collection.close()
            files_to_upload.append(filepath)
            counter = 1
            batch += 1
    if counter < batch_size and collection:
        collection.write("</collection>")
        collection.close()
        files_to_upload.append(filepath)
    body = ['From %s sources, found and converted %s records' %
            (len(new_sources), len(new_files)),
            '\t%s records ready to upload:\n' %
            ((batch - 1) * 500 + counter,)]
    if submit:
        body += ['\tFiles uploaded to Server:']
        for filepath in files_to_upload:
            try:
                submit_records_via_ftp(filepath)
                filename = filepath.split('/')[-1]
                body.append("\t%s (%s records)" % (filename, batch_size))
            except:
                _errors_detected.append(Exception(
                    "Failed to upload %s to FTP server" % filepath)
                )
                write_message("Failed to upload %s to FTP server" % filepath)
    else:
        body += ['\tFiles ready for upload:']
        for filename in files_to_upload:
            body.append("\t%s (%s records)" % (filename, batch_size))
    if len(body) > 3:
        #update the last line of the message
        body[-1] = "\t%s (%s records)" % (filename, counter)
        body = '\n'.join(body)
        write_message(subject)
        write_message(body)
    else:
        write_message(subject)
        write_message("No new files!")
    if submit:
        if submit_records_via_mail(subject, body, CFG_CONSYNHARVEST_EMAIL):
            write_message("Mail sent to %r" % (CFG_CONSYNHARVEST_EMAIL,))
        else:
            write_message("ERROR: Cannot send mail.")


if __name__ == "__main__":
    bst_consyn_harvest()
