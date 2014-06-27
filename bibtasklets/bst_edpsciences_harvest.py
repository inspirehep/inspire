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
import tarfile
from os import (makedirs,
                listdir)
from datetime import datetime
from os.path import (join,
                     dirname,
                     exists)
from invenio.config import (CFG_EDPSCIENCE_SERVER,
                            CFG_EDPSCIENCE_USERNAME,
                            CFG_EDPSCIENCE_PASSWORD,
                            CFG_EDPSCIENCE_OUT_FOLDER,
                            CFG_SITE_SUPPORT_EMAIL)
from invenio.bibtask import (task_update_progress,
                             task_sleep_now_if_required)
from harvestingkit.ftp_utils import FtpHandler
from harvestingkit.edpsciences_package import EDPSciencesPackage
from invenio.apsharvest_utils import (write_message,
                                      submit_records_via_ftp,
                                      submit_records_via_mail)


def bst_edpsciences_harvest(from_date="", to_date=""):
    """ Task to download and convert xml files from EDP Sciences
    FTP servers to Marc xml files.
    """
    source_folder = join(CFG_EDPSCIENCE_OUT_FOLDER, 'sources')
    if not exists(source_folder):
        makedirs(source_folder)
    marc_folder = join(CFG_EDPSCIENCE_OUT_FOLDER, 'marc')
    if not exists(marc_folder):
        makedirs(marc_folder)
    new_files = download_files(from_date, to_date)
    files_to_convert = []
    if new_files:
        task_sleep_now_if_required()
        files_to_convert = extract_files(new_files, source_folder)
        task_sleep_now_if_required(can_stop_too=True)
        converted_files = convert_files(files_to_convert, source_folder,
                                        marc_folder, from_date, to_date)
        if converted_files:
            create_collection(converted_files, new_files)
    else:
        write_message("No new files to download!")


def is_younger(filename, from_date, ftp):
    """ Check if a file was uploaded after a certain date"""
    if from_date:
        datestamp = ftp.get_datestamp(filename)
        return datestamp >= from_date
    else:
        return True


def download_files(from_date, to_date):
    """Downloads the new files from the EDP Sciences
    FTP server."""
    download_folder = join(CFG_EDPSCIENCE_OUT_FOLDER, 'packages')
    old_files = listdir(download_folder)
    ftp = FtpHandler(CFG_EDPSCIENCE_SERVER,
                     CFG_EDPSCIENCE_USERNAME,
                     CFG_EDPSCIENCE_PASSWORD)
    ftp.cd('incoming')
    new_files = ftp.ls()[0]
    new_files = filter(lambda a: is_younger(a,
                                            from_date,
                                            ftp),
                       new_files)
    files_to_download = filter(lambda a: a not in old_files,
                               new_files)
    counter = 1
    for filename in files_to_download:
        task_update_progress('Downloading files 1/3 \t%s of %s'
                             % (counter, len(new_files)))
        write_message('Downloading file %s' % (filename,))
        ftp.download(filename, download_folder)
        filename = join(download_folder, filename)
        counter += 1
    ftp.close()
    return map(lambda a: join(download_folder, a), new_files)


def extract_files(new_files, source_folder):
    """Extracts the tar files to the source_folder"""
    counter = 1
    extracted_files = []
    for filename in new_files:
        task_update_progress('Extracting files 2/3 \t%s of %s' %
                             (counter, len(new_files)))
        write_message('Extracting file %s' % (filename,))
        tar = tarfile.open(filename)
        files = [a.name for a in tar.getmembers()]
        tar.extractall(source_folder)
        extracted_files.extend(files)
        tar.close()
        counter += 1
    return [join(source_folder, a) for a in extracted_files]


def convert_files(files_to_convert, source_folder, marc_folder,
                  from_date, to_date):
    """Converts the xml source files to marc xml files"""
    converted_files = []
    edp = EDPSciencesPackage()
    counter = 1
    for filename in files_to_convert:
        task_update_progress('Converting files 3/3 \t%s of %s' %
                             (counter, len(files_to_convert)))
        target_file = filename.split('/')[-1]
        target_file = join(marc_folder, target_file)
        target_folder = dirname(target_file)
        if not exists(target_folder):
            makedirs(target_folder)
        record = ""
        datestamp = edp.get_date(filename)
        if exists(target_file):
            if from_date and to_date:
                if datestamp >= from_date and\
                        datestamp <= to_date:
                    converted_files.append(target_file)
                elif from_date:
                    if datestamp >= from_date:
                        converted_files.append(target_file)
                elif to_date:
                    if datestamp <= to_date:
                        converted_files.append(target_file)
                else:
                    converted_files.append(target_file)
        else:
            if 'xml_rich' in filename:
                record = edp.get_record_rich(filename)
            else:
                if from_date and to_date:
                    if datestamp >= from_date and\
                            datestamp <= to_date:
                        record = edp.get_record(filename)
                elif from_date:
                    if datestamp >= from_date:
                        record = edp.get_record(filename)
                elif to_date:
                    if datestamp <= to_date:
                        record = edp.get_record(filename)
                else:
                    record = edp.get_record(filename)
            if record:
                write_message("Converted file: %s" % (filename,))
                with open(target_file, 'w') as out:
                    out.write(record)
                    converted_files.append(target_file)
        counter += 1
    return converted_files


def create_collection(converted_files, new_files):
    """Creates the record collection file
    uploads it to the FTP server and sends
    an email to inform about the harvest"""
    target_file = "edpsciences.%s.xml" % \
                  (datetime.now().strftime("%Y-%m-%d"),)
    target_file = join(CFG_EDPSCIENCE_OUT_FOLDER, target_file)
    write_message("Creating collection file: %s" % (target_file,))
    with open(target_file, 'w') as collection:
        collection.write('<collection>\n')
        for fl in converted_files:
            recordfile = open(fl)
            collection.write(recordfile.read())
            recordfile.close()
        collection.write('\n</collection>')
    submit_records_via_ftp(target_file)
    body = ['From %s sources, found and converted %s records'
            % (len(new_files), len(converted_files)),
            '\t%s records ready to upload:\n'
            % (len(converted_files),),
            '\t%s uploaded to server:'
            % (target_file,)]
    body = '\n'.join(body)
    subject = "EDP Sciences harvest results: %s" % \
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    write_message(body)
    if submit_records_via_mail(subject, body, CFG_SITE_SUPPORT_EMAIL):
        write_message("Mail sent to %r" % (CFG_SITE_SUPPORT_EMAIL,))
    else:
        write_message("ERROR: Cannot send mail.")


if __name__ == '__main__':
    bst_edpsciences_harvest(from_date="2014-07-01")
