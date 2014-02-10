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

import sys
import xml.dom.minidom
import os
import sys
import traceback

from zipfile import ZipFile, BadZipfile
from invenio.dbquery import run_sql
from invenio.filedownloadutils import download_url, InvenioFileDownloadError
from harvestingkit.minidom_utils import get_value_in_tag
from harvestingkit.elsevier_package import ElsevierPackage
from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibtask import task_update_status, \
    write_message, \
    task_update_progress, \
    task_sleep_now_if_required
try:
    from invenio.config import CFG_CONSYN_OUT_DIRECTORY
except ImportError:
    CFG_CONSYN_OUT_DIRECTORY = os.path.join(CFG_TMPSHAREDDIR, "consynharvest")


NOT_ARTICLE_TITLES = ["editorial board", "author index", "subject index",
"announcement from the publisher", "index"
"papers to appear in forthcoming issues of nuclear physics b[fs]"]


def bst_consyn_harvest(CONSYNATOMURL="https://consyn.elsevier.com/batch/atom?key=QUhvbHRrYW1wOzM0Mjc%253d"):
    """
    Task to download metadata given an ATOM feed from consyn.elsevier.com
    and a folder to store the files.

    @param CONSYNATOMURL: The URL of the atom feed to download.
    """
    if not os.path.exists(CFG_CONSYN_OUT_DIRECTORY):
        folders = CFG_CONSYN_OUT_DIRECTORY.split("/")
        folder = "/"
        for i in range(1, len(folders)):
            folder = os.path.join(folder, folders[i]).strip()
            if not os.path.exists(folder):
                os.mkdir(folder)
            
    try:
        run_sql("SELECT filename FROM CONSYNHARVEST")
    except:
        run_sql("CREATE TABLE CONSYNHARVEST ("
                "filename VARCHAR(100) NOT NULL PRIMARY KEY,"
                "date VARCHAR(50),"
                "size VARCHAR(30) );")
    # Get list of entries from XML document
    xmlString = ""
    try:
        task_update_progress("Downloading and extracting files 1/2...")
        result_file = download_url(url=CONSYNATOMURL,
                                   retry_count=5,
                                   timeout=60.0)
        xmlString = open(result_file, 'r').read()
    except InvenioFileDownloadError, err:
        write_message("URL could not be opened: %s" % (CONSYNATOMURL,))
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
        # Output location is CFG_CONSYN_OUT_DIRECTORY + filename
        outFilename = os.path.join(CFG_CONSYN_OUT_DIRECTORY, fileName)
        outFilename = outFilename.lstrip()

        #file has already been fetched
        if outFilename in downloaded_files:
            write_message("Not downloading %s, already found %s\n" %
                          (fileUrl, outFilename))
        else:
            try:
                write_message("Downloading %s to %s\n" % (fileUrl, outFilename))
                download_url(fileUrl, "zip", outFilename, 5, 60.0)
            except InvenioFileDownloadError, err:
                write_message("URL could not be opened: %s" % (fileUrl,))
                write_message(str(err))
                write_message(traceback.format_exc()[:-1])
                task_update_status("CERROR")
                return
            size = os.path.getsize(outFilename)
            run_sql("INSERT INTO CONSYNHARVEST"
                    "(filename,date,size)"
                    "VALUES (%s,%s,%s)",
                    (outFilename, updated, size))
            downloaded_files.append(outFilename)
            try:
                extractAll(outFilename)
            except BadZipfile:
                write_message("Error BadZipfile %s",(outFilename,))
                task_update_status("CERROR")
                os.remove(outFilename)
                run_sql("DELETE FROM CONSYNHARVEST"
                        "WHERE filename =%s",
                        (outFilename,))
                
    task_sleep_now_if_required(can_stop_too=True)
    consyn_files = os.path.join(CFG_CONSYN_OUT_DIRECTORY, "consyn-files")
    consyn_files = consyn_files.lstrip()
    els = ElsevierPackage(path="whatever", CONSYN=True)
    task_update_progress("Converting files 2/2...")
    fetch_xml_files(consyn_files, els)
    task_sleep_now_if_required(can_stop_too=False)
    create_collection()


def get_title(xmlFile):
    try:
        return get_value_in_tag(xmlFile, "ce:title")
    except Exception:
        print >> sys.stderr, "Can't find title"


def extractAll(zipName):
    """Unzip a zip file"""
    write_message("Unziping: " + zipName + "\n")
    z = ZipFile(zipName)
    for f in z.namelist():
        extract_fld = os.path.join(CFG_CONSYN_OUT_DIRECTORY, "consyn-files")
        extract_fld = extract_fld.lstrip()
        if not os.path.exists(os.path.join(extract_fld, f)):
            z.extract(f, extract_fld)
    #delete the zip file after the extraction
    write_message("Deleting zip file: " + zipName + "\n")
    os.remove(zipName)


def fetch_xml_files(folder, els):
    """Recursively gets the downloaded xml files
    converts them to marc xml format and stores them
    in the "marc_files" folder."""
    if os.path.exists(folder):
        for subfolder in os.listdir(folder):
            subfolder = os.path.join(folder, subfolder).lstrip()
            if os.path.isfile(subfolder):
                xmlFile = open(subfolder, "r")
                xmlString = xmlFile.read()
                xmlFile.close()
                dom_xml = xml.dom.minidom.parseString(xmlString)
                title = get_title(dom_xml).lower()
                #print subfolder
                #print dom_xml.getElementsByTagName("prism:doi")[0].firstChild.data
                #ignore index pages
                if not title.startswith("cumulative author index") and \
                not title in NOT_ARTICLE_TITLES:
                    marc_fld = os.path.join(CFG_CONSYN_OUT_DIRECTORY, "marc_files")
                    marc_fld = marc_fld.lstrip()
                    if not os.path.exists(marc_fld):
                        os.mkdir(marc_fld)
                    #Errata must be linked to the referencing paper
                    #so we store them in separate folder
                    if title.startswith("errat"):
                        errata_folder = os.path.join(marc_fld, "errata")
                        errata_folder = errata_folder.lstrip()
                        extract_fld = os.path.join(CFG_CONSYN_OUT_DIRECTORY, "consyn-files")
                        extract_fld = extract_fld.lstrip()
                        if not os.path.exists(errata_folder):
                            os.mkdir(errata_folder)
                        outfolder = subfolder[len(extract_fld)+1:]
                        #create folders
                        folders = outfolder.split('/')
                        for i in range(len(folders)):
                            folder = errata_folder
                            for f in range(i):
                                folder = os.path.join(folder, folders[f])
                                if not os.path.exists(folder):
                                    os.mkdir(folder)
                        file_loc = os.path.join(errata_folder, outfolder)
                        file_loc = file_loc.lstrip()
                        if not os.path.exists(file_loc):
                            marcfile = open(file_loc, 'w')
                            marcfile.write(els.get_record(subfolder, True))
                            marcfile.close()
                            task_sleep_now_if_required(can_stop_too=False)
                    else:
                        extract_fld = os.path.join(CFG_CONSYN_OUT_DIRECTORY, "consyn-files")
                        extract_fld = extract_fld.lstrip()
                        outfolder = subfolder[len(extract_fld) + 1:]
                        #create folders
                        folders = outfolder.split('/')
                        for i in range(len(folders)):
                            folder = marc_fld
                            for f in range(i):
                                folder = os.path.join(folder, folders[f])
                                if not os.path.exists(folder):
                                    os.mkdir(folder)
                        file_loc = os.path.join(marc_fld, outfolder)
                        file_loc = file_loc.lstrip()
                        if not os.path.exists(file_loc):
                            marcfile = open(file_loc, 'w')
                            marcfile.write(els.get_record(subfolder, True))
                            marcfile.close()
                            task_sleep_now_if_required(can_stop_too=False)
            else:
                fetch_xml_files(subfolder, els)


def create_collection():
    """Create a single xml file "collection.xml" 
    that contains all the records."""
    folder = os.path.join(CFG_CONSYN_OUT_DIRECTORY, "marc_files").lstrip()
    collection = open(os.path.join(CFG_CONSYN_OUT_DIRECTORY, "collection.xml"). lstrip(), 'w')
    collection.write("<collection>\n")
    parse_files(folder, collection)
    collection.write("\n</collection>")
    collection.close()


def parse_files(folder, collection):
    """Reads all the xml files contained in a folders
    and appends them in the file "collection"."""
    if os.path.exists(folder):
        for subfolder in os.listdir(folder):
            subfolder = os.path.join(folder, subfolder).lstrip()
            if os.path.isfile(subfolder):
                xmlFile = open(subfolder, 'r')
                xmlString = xmlFile.read()
                xmlFile.close()
                collection.write(xmlString+'\n')
            else:
                parse_files(subfolder, collection)


if __name__ == "__main__":
    bst_consyn_harvest()
