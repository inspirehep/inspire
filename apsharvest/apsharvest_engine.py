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

"""
APSharvest engine module containing all the objects
used when harvesting.
"""

import os
import sys
import datetime
import shutil
import time
import traceback

from invenio.bibtask import (write_message,
                             task_sleep_now_if_required,
                             task_update_progress,
                             )
from invenio.filedownloadutils import (download_url,
                                       InvenioFileDownloadError)

from invenio.apsharvest_utils import (create_records_from_file,
                                      create_records_from_string,
                                      create_work_folder,
                                      create_folders,
                                      get_record_from_doi,
                                      get_doi_from_record,
                                      generate_xml_for_records,
                                      submit_records_via_ftp,
                                      submit_records_via_mail,
                                      submit_bibupload_for_records,
                                      is_beyond_threshold_date,
                                      unzip,
                                      get_file_modified_date,
                                      find_and_validate_md5_checksums,
                                      convert_xml_using_saxon,
                                      compare_datetime_to_iso8601_date,
                                      remove_dtd_information
                                      )
from invenio.apsharvest_config import (CFG_APSHARVEST_FFT_DOCTYPE,
                                       CFG_APSHARVEST_REQUEST_TIMEOUT,
                                       CFG_APSHARVEST_FULLTEXT_URL,
                                       CFG_APSHARVEST_MD5_FILE)
from invenio.apsharvest_dblayer import (store_last_updated,
                                        can_launch_bibupload)
from invenio.apsharvest_errors import (APSHarvesterSearchError,
                                       APSHarvesterSubmissionError,
                                       APSHarvesterFileExits,
                                       APSHarvesterConversionError,
                                       APSFileChecksumError,
                                       )
from invenio.docextract_record import (BibRecord,
                                       BibRecordControlField)


try:
    from invenio.config import CFG_APSHARVEST_XSLT
except ImportError:
    CFG_APSHARVEST_XSLT = "/afs/cern.ch/project/inspire/xslt/aps.xsl"

try:
    from invenio.config import CFG_APSHARVEST_EMAIL
except ImportError:
    CFG_APSHARVEST_EMAIL = "desydoc@desy.de"


class APSRecordList(list):
    """
    Class representing the list of records to harvest.
    """
    def __init__(self):
        super(APSRecordList, self).__init__()
        self.recids = []

    def append(self, record):
        """
        Append a APSRecord to the list if it is not already there.
        """
        if record.recid not in self.recids:
            super(APSRecordList, self).append(record)
            self.recids.append(record.recid)


class APSHarvestJob(object):
    """Represents a harvesting job"""
    def __init__(self, directory):
        self.records_harvested = []
        self.records_to_insert = []
        self.records_to_update = []
        self.records_failed = []
        self.zip_folder = create_folders(os.path.join(directory, "zips"))
        self.out_folder = create_work_folder(directory)
        self.date_started = datetime.datetime.now()
        self.mail_subject = "APS harvest results: %s" % \
                            (self.date_started.strftime("%Y-%m-%d %H:%M:%S"),)
        from invenio.refextract_kbs import get_kbs
        journal_mappings = get_kbs()
        if journal_mappings and "journals" in journal_mappings:
            journal_mappings = journal_mappings['journals'][1]
        else:
            journal_mappings = {}
        self.journal_mappings = journal_mappings

    def check_records(self):
        """
        Checks if given records exists on the system and then returns
        a tuple of records that is new and records that exists:

        @return: a tuple of (new_records, existing_records)
        @rtype: tuple
        """
        # We check if any records already exists
        new_records = []
        existing_records = []
        for record in self.records_harvested:
            # Do we already have the record id perhaps?
            if not record.recid:
                try:
                    record.recid = get_record_from_doi(record.doi)
                except APSHarvesterSearchError, e:
                    write_message("Error while getting recid from %s: %s" %
                                  (record.doi, str(e)))

                    # Problem detected, send mail immediately:
                    problem_rec = generate_xml_for_records(records=[record],
                                                           directory=self.out_folder,
                                                           suffix="problem.xml")
                    subject = "APS harvest problem: %s" % \
                              (self.date_started.strftime("%Y-%m-%d %H:%M:%S"),)
                    body = "There was a problem harvesting %s. \n %s \n Path: \n%s" % \
                           (record.doi, str(e), problem_rec)
                    submit_records_via_mail(subject, body, CFG_APSHARVEST_EMAIL)
                    continue

            # What about now?
            if record.recid:
                existing_records.append(record)
            else:
                new_records.append(record)
        return new_records, existing_records

    def reset_bunch(self):
        """Reset the record lists. Used when bunching."""
        self.records_harvested = []

    def get_file_prefix(self, parameters={}):
        """Return a nicely formatted filename prefix."""
        date_list = []
        if parameters.get("from_date"):
            date_list.append(parameters.get("from_date"))
            if parameters.get("until_date"):
                date_list.append(parameters.get("until_date"))
        else:
            date_list.append(self.date_started.strftime("%Y-%m-%d"))
        return "aps_%s_" % ("_".join(date_list), )

    def check_for_records(self):
        """Any records left to submit?"""
        return self.records_harvested or self.records_to_update or self.records_to_insert

    def perform_fulltext_harvest(self, record_list, parameters):
        """
        For every record in given list APSRecord(record ID, DOI, date last
        updated), yield a APSRecord with added FFT dictionary containing URL to
        fulltext/metadata XML downloaded locally.

        If a download is unsuccessful, an error message is given.

        @return: tuple of (APSRecord, error_message)
        """
        count = 0
        request_end = None
        request_start = None
        for record in record_list:
            task_sleep_now_if_required(can_stop_too=False)
            # Unless this is the first request, lets sleep a bit
            if request_end and request_start:
                request_dt = request_end-request_start
                write_message("Checking request time (%d)"
                              % (request_dt,), verbose=3)
                if count and request_dt > 0 and request_dt < CFG_APSHARVEST_REQUEST_TIMEOUT:
                    write_message("Initiating sleep for %.1f seconds"
                                  % (request_dt,), verbose=3)
                    time.sleep(request_dt)

            count += 1
            task_update_progress("Harvesting record (%d/%d)" % (count,
                                                                len(record_list)))

            if not record.doi:
                msg = "No DOI found for record %d" % (record.recid or "",)
                write_message("Error: %s" % (msg,), stream=sys.stderr)
                yield record, msg
                continue

            url = CFG_APSHARVEST_FULLTEXT_URL % {'doi': record.doi}
            result_file = os.path.join(self.zip_folder,
                                       "%s.zip" % (record.doi.replace('/', '_')))
            try:
                request_start = time.time()
                if os.path.exists(result_file):
                    # File already downloaded recently, lets see if it is the same
                    file_last_modified = get_file_modified_date(result_file)
                    if not compare_datetime_to_iso8601_date(file_last_modified, record.last_modified):
                        # File is not older than APS version, we should not download.
                        raise APSHarvesterFileExits

                write_message("Trying to save to %s" % (result_file,), verbose=5)

                result_file = download_url(url=url,
                                           download_to_file=result_file,
                                           content_type="zip",
                                           retry_count=5,
                                           timeout=60.0)
                write_message("Downloaded %s to %s" % (url, result_file), verbose=2)
            except InvenioFileDownloadError, e:
                msg = "URL could not be opened: %s" % (url,)
                write_message("Error: %s" % (msg,),
                              stream=sys.stderr)
                yield record, msg
                continue

            except APSHarvesterFileExits:
                write_message("File exists at %s" % (result_file,), verbose=2)

            except StandardError, e:
                if 'urlopen' in str(e) or 'URL could not be opened' in str(e):
                    msg = "URL could not be opened: %s" % (url,)
                    write_message("Error: %s" % (msg,),
                                  stream=sys.stderr)
                    write_message("No fulltext found for %s" %
                                 (record.recid or record.doi,))
                    yield record, msg
                    continue
                raise
            finally:
                request_end = time.time()

            # Unzip the compressed file
            unzipped_folder = unzip(result_file, base_directory=self.out_folder)

            # Validate the checksum of the compressed fulltext file.
            try:
                checksum_validated_files = find_and_validate_md5_checksums(
                    in_folder=unzipped_folder,
                    md5key_filename=CFG_APSHARVEST_MD5_FILE)
            except APSFileChecksumError, e:
                info_msg = "Skipping %s in %s" % \
                           (record.recid or record.doi, unzipped_folder)
                msg = "Error while validating checksum: %s\n%s\n%s" % \
                      (info_msg, str(e), traceback.format_exc()[:-1])
                write_message(msg)
                yield record, msg
                continue
            if not checksum_validated_files:
                write_message("Warning: No files found to perform checksum"
                              " validation on inside %s" % (unzipped_folder,))
            elif len(checksum_validated_files) != 1 or \
                    not 'fulltext.xml' in checksum_validated_files[0]:
                msg = "Warning: No fulltext file found inside %s for %s" % \
                      (unzipped_folder, record.recid or record.doi)
                write_message(msg)
                yield record, msg
                continue

            # We have the fulltext file as fulltext.xml as expected.
            fulltext_file = checksum_validated_files[0]

            write_message("Harvested record %s (%s)" %
                         (record.recid or "new record", count))
            write_message("File: %s" % (fulltext_file,), verbose=2)

            # Check if published date is after threshold:
            if is_beyond_threshold_date(parameters.get("threshold_date"), fulltext_file):
                # The published date is beyond the threshold, we continue
                msg = "Warning: Article published beyond threshold: %s" % \
                      (record.doi,)
                write_message(msg)
                yield record, msg
                continue
            else:
                write_message("OK. Record is below the threshold.", verbose=3)

            if parameters.get("metadata"):
                from harvestingkit.aps_package import (ApsPackage,
                                                       ApsPackageXMLError)
                # Generate Metadata,FFT and yield it
                aps = ApsPackage(self.journal_mappings)
                try:
                    xml = aps.get_record(fulltext_file)
                    record.add_metadata_by_string(xml)
                except ApsPackageXMLError, e:
                    # This must be old-format XML
                    write_message("Warning: old-style metadata detected for %s" %
                                  (fulltext_file))
                    # Remove any DTD info in the file before converting
                    cleaned_fulltext_file = remove_dtd_information(fulltext_file)
                    try:
                        convert_xml_using_saxon(cleaned_fulltext_file,
                                                CFG_APSHARVEST_XSLT)

                        # Conversion is a success. Let's derive location of converted file
                        source_directory = os.path.dirname(cleaned_fulltext_file)
                        path_to_converted = "%s%s%s.xml" % \
                                            (source_directory,
                                             os.sep,
                                             record.doi.replace('/', '_'))
                        write_message("Converted meta-data for %s" %
                                     (record.recid or "new record"), verbose=2)
                        record.add_metadata(path_to_converted)
                    except APSHarvesterConversionError, e:
                        msg = "Metadata conversion failed: %s\n%s" % \
                              (str(e), traceback.format_exc()[:-1])
                        write_message(msg, stream=sys.stderr)
                        yield record, msg

                write_message("Converted metadata for %s" %
                              (record.recid or "new record"), verbose=2)

            if parameters.get("fulltext"):
                record.add_fft(fulltext_file, parameters.get("hidden"))

            if record.date:
                store_last_updated(record.recid, record.date, name="apsharvest")

            yield record, ""

    def process_record_submission(self, parameters):
        """Run the submission process."""
        if parameters.get("match"):
            # We will do a simple match with the database
            new_records, existing_records = self.check_records()
            self.records_to_insert.extend(new_records)
            self.records_to_update.extend(existing_records)
        else:
            # We insert everything
            self.records_to_insert.extend(self.records_harvested)

        if self.records_to_insert:
            # Submit new records
            record_filename = generate_xml_for_records(
                self.records_to_insert,
                self.out_folder,
                prefix=self.get_file_prefix(parameters),
                suffix="_insert.xml"
            )

            if not parameters.get("devmode"):
                taskid = self.submit_records(record_filename,
                                             parameters.get("new_mode"))
                if not taskid:
                    # Something went wrong
                    err_string = "New records (%s)" \
                                 " were not submitted correctly" % \
                                 (record_filename,)
                    raise APSHarvesterSubmissionError(err_string)
            self.records_to_insert = []

        if self.records_to_update:
            # Submit new records
            record_filename = generate_xml_for_records(
                self.records_to_update,
                self.out_folder,
                prefix=self.get_file_prefix(parameters),
                suffix="_update.xml"
            )

            if not parameters.get("devmode"):
                taskid = self.submit_records(record_filename,
                                             parameters.get("update_mode"),
                                             update=True,
                                             silent=parameters.get("records") and True or False,)
                if not taskid:
                    # Something went wrong
                    err_string = "Existing records (%s)" \
                                 " were not submitted correctly" % \
                                 (record_filename,)
                    raise APSHarvesterSubmissionError(err_string)
            self.records_to_update = []

        if self.records_failed:
            body = "\n".join(["%s failed with error: %s"
                              % (rec.doi or rec.recid, msg)
                              for rec, msg in self.records_failed])
            if not parameters.get("devmode"):
                submit_records_via_mail(subject="%s (failed records)" % (self.mail_subject,),
                                        body=body,
                                        toaddr=CFG_APSHARVEST_EMAIL)

    def submit_records(self, records_filename, mode, update=False,
                       taskid=0, silent=False):
        """
        Performs the logic to submit given file (filepath) of records
        either by e-mail or using BibUpload with given mode.

        Taskid is given to indicate if the task submission should wait for any
        previously submitted tasks.

        The submission can also be made "silent" in the sense of not
        updating the modification date of the records.

        @param records_filename: filepath to XML file containing records.
        @type records_filename: string

        @param records_list: list of APSRecord objects for records
        @type records_list: list

        @param mode: which submission mode is it?
        @type mode: string

        @param taskid: bibsched taskid, wait for task to complete before submission
        @type taskid: int

        @param silent: do not update the modification date of the records
        @type silent: bool

        @return: returns the given taskid upon submission, or True/False from email.
        """
        if update:
            records_list = self.records_to_update
        else:
            records_list = self.records_to_insert

        # Check if we should create bibupload or e-mail
        if mode == "email":
            # Lets parse the records and find our IDs.
            list_of_dois = []
            for record in records_list:
                # We strip away the first part of the DOI for readability.
                list_of_dois.append('/'.join(record.doi.split('/')[1:]))
            # We send an e-mail to CFG_APSHARVEST_EMAIL and put file on AFS.
            body = "Harvested new records: %s" % (records_filename,)
            try:
                try:
                    shutil.move(records_filename, self.out_folder)
                    records_filename = os.path.join(self.out_folder,
                                                    os.path.basename(records_filename))
                    body = "Harvested new records on %s. They are located here:\n %s" % \
                           (self.date_started.strftime("%Y-%m-%d %H:%M:%S"), records_filename)
                except IOError, e:
                    # Some IOError
                    body = "Error while harvesting records: \nError saving %s - %s" % \
                           (records_filename, str(e))
                    raise e
            finally:
                submit_records_via_ftp(records_filename)
                body = "%s\nRecords harvested (%s total):\n%s\n" % (body,
                                                                    str(len(list_of_dois)),
                                                                    "\n".join(list_of_dois))

                body = "%s\nUploaded to FTP: %s" % (
                    body,
                    os.path.basename(records_filename)
                )

                res = submit_records_via_mail(self.mail_subject, body, CFG_APSHARVEST_EMAIL)
                write_message("Sent e-mail to %s with path to %s" %
                              (CFG_APSHARVEST_EMAIL, records_filename))
                return res
        else:
            # We submit a BibUpload task and wait for it to finish
            task_update_progress("Waiting for task to finish")

            if taskid != 0:
                write_message("Going to wait for %d to finish" % (taskid,))

            while not can_launch_bibupload(taskid):
                # Lets wait until the previously launched task exits.
                task_sleep_now_if_required(can_stop_too=False)
                time.sleep(5.0)

            taskid = submit_bibupload_for_records(mode, records_filename, silent)
            write_message("Submitted BibUpload task #%s with mode %s" %
                         (str(taskid), mode))
            return taskid


class APSRecord(object):
    """
    Class representing a record to harvest.
    """
    def __init__(self, recid, doi=None, date=None, last_modified=None):
        self.recid = recid
        self.doi = doi or get_doi_from_record(self.recid)
        self.date = date
        self.record = BibRecord(recid or None)
        self.last_modified = last_modified

    def add_metadata(self, marcxml_file):
        """
        Adds metadata from given file. Removes any DTD definitions
        and translates the metadata to MARCXML using BibConvert.
        """
        if marcxml_file:
            self.record = create_records_from_file(marcxml_file)
            if self.recid:
                self.record['001'] = [BibRecordControlField(str(self.recid))]

    def add_metadata_by_string(self, marcxml_text):
        """
        Adds metadata from given text.
        """
        if marcxml_text:
            self.record = create_records_from_string(marcxml_text)
            if self.recid:
                self.record['001'] = [BibRecordControlField(str(self.recid))]

    def add_fft(self, fulltext_file, hidden=True):
        """
        Adds FFT information as required from given fulltext.
        """
        fft = self.record.add_field("FFT__")
        fft.add_subfield('a', fulltext_file)

        if hidden:
            fft.add_subfield('t', CFG_APSHARVEST_FFT_DOCTYPE)
            fft.add_subfield('o', "HIDDEN")
        else:
            fft.add_subfield('t', "INSPIRE-PUBLIC")

    def to_xml(self):
        return self.record.to_xml()
