# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
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

import os
import sys
import traceback
import fnmatch
import zipfile
import codecs
import re
import datetime
import time

from bs4 import BeautifulSoup

from tempfile import mkdtemp, mkstemp
from invenio.config import CFG_SITE_SUPPORT_EMAIL
from invenio.mailutils import send_email
from invenio.search_engine import search_pattern
from invenio.shellutils import run_shell_command
from invenio.bibformat_engine import BibFormatObject
from invenio.bibtask import (task_update_status,
                             write_message,
                             task_low_level_submission,
                             )
from invenio.apsharvest_errors import (APSHarvesterSearchError,
                                       APSFileChecksumError,
                                       APSHarvesterConversionError)
from invenio.apsharvest_config import CFG_APSHARVEST_RECORD_DOI_TAG
from harvestingkit.ftp_utils import FtpHandler


RE_ARTICLE_DTD = re.compile('<!DOCTYPE article PUBLIC "-//American Physical'
                            ' Society//DTD Archival Article [0-9]*?\.[0-9]*?//EN"'
                            ' "article\.dtd">')


def unzip(zipped_file, base_directory=None,
          prefix="apsharvest_unzip_", suffix=""):
    """
    Uncompress a zipped file from given filepath to an (optional) location.
    If no location is given, a temporary folder will be generated inside
    CFG_TMPSHAREDDIR of Invenio.
    """
    if not base_directory:
        from invenio.config import CFG_TMPSHAREDDIR
        base_directory = os.path.join(CFG_TMPSHAREDDIR, 'apsharvest')
    # We create a temporary directory to extract our stuff in
    try:
        output_directory = mkdtemp(suffix=suffix,
                                   prefix=prefix,
                                   dir=base_directory)
    except Exception, e:
        try:
            os.removedirs(output_directory)
        except TypeError:
            pass
        raise e
    return _do_unzip(zipped_file, output_directory)


def _do_unzip(zipped_file, output_directory):
    """
    Performs the actual uncompression.
    """
    z = zipfile.ZipFile(zipped_file)
    for path in z.namelist():
        relative_path = os.path.join(output_directory, path)
        dirname, dummy = os.path.split(relative_path)
        try:
            if relative_path.endswith(os.sep) and not os.path.exists(dirname):
                os.makedirs(relative_path)
            elif not os.path.exists(relative_path):
                dirname = os.path.join(output_directory, os.path.dirname(path))
                if os.path.dirname(path) and not os.path.exists(dirname):
                    os.makedirs(dirname)
                fd = open(relative_path, "w")
                fd.write(z.read(path))
                fd.close()
        except IOError, e:
            raise e
    return output_directory


## {{{ http://code.activestate.com/recipes/499305/ (r3)
def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dummy, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)
## end of http://code.activestate.com/recipes/499305/ }}}


def find_and_validate_md5_checksums(in_folder, md5key_filename):
    """
    Given a root folder to search in and the name of a file containing
    textual info about file checksums to validate, this function will
    return True if the checksum is correct. Otherwise an
    APSFileChecksumError is returned.

    The filename containing the MD5 hashkey is expected to follow this
    structure:

    hashkey filepath
    """
    from invenio.bibdocfile import calculate_md5_external

    validated_files = []
    for filename in locate(md5key_filename, root=in_folder):
        file_fd = open(filename, 'r')
        contents = file_fd.readlines()
        for line in contents:
            split_line = line.split(' ')
            if len(split_line) == 2:
                hashkey, hashkey_target = split_line
                hashkey_target = os.path.join(os.path.dirname(filename),
                                              hashkey_target.strip())
                hashkey = hashkey.strip()
                found_hashkey = calculate_md5_external(hashkey_target).strip()
                if found_hashkey != hashkey:
                    raise APSFileChecksumError("Error matching checksum of %s:"
                                               " %s is not equal to %s" %
                                               (hashkey_target,
                                                found_hashkey,
                                                hashkey))
                validated_files.append(hashkey_target)
    return validated_files


def get_temporary_file(prefix="apsharvest_test_", suffix="", directory=""):
    """
    Using a similar interface as tempfile.mkstemp, this function wraps
    the call to mkstemp and returns a safe and closed filepath.
    """
    try:
        file_fd, filepath = mkstemp(prefix=prefix,
                                    suffix=suffix,
                                    dir=directory)
        os.close(file_fd)
    except IOError, e:
        try:
            os.remove(filepath)
        except Exception:
            pass
        raise e
    return filepath


def remove_dtd_information(fulltext_file):
    """
    Removes any DTD schema validation of "article.dtd" in file.
    """
    # Remove DTD line
    cleaned_lines = []
    for line in codecs.open(fulltext_file, "r", "utf-8"):
        line = RE_ARTICLE_DTD.sub('', line)
        cleaned_lines.append(line)

    # Overwrite file
    new_file = os.path.splitext(fulltext_file)[0] + "_cleaned.xml"
    fulltext_file = codecs.open(new_file, 'w', "utf-8")
    fulltext_file.writelines(cleaned_lines)
    fulltext_file.close()
    return new_file


def convert_xml_using_saxon(source_file, template_file):
    """
    Tries to convert given source file (full path) using XSLT 2.0 Java libraries.

    Looks for given XSLT stylesheet/template file (relative path) in
    CFG_BIBCONVERT_XSL_PATH.

    Path to converted file is derived from DOI in the same directory as source
    as decided inside the template file.

    For example: /path/to/sourcedir/10.1103_PhysRevA.87.052320.xml

    @raise: APSHarvesterConversionError if Java saxon9he-xslt returns error.

    @return: True on success.
    """
    from invenio.bibconvert_xslt_engine import CFG_BIBCONVERT_XSL_PATH
    from invenio.shellutils import run_shell_command

    if not os.path.isabs(template_file):
        template_file = CFG_BIBCONVERT_XSL_PATH + os.sep + template_file
    source_directory = os.path.dirname(source_file)
    command = "cd %s && saxon9he-xslt -s:%s -xsl:%s -dtd:off" % \
              (source_directory, source_file, template_file)
    exit_code, stdout_buffer, stderr_buffer = run_shell_command(cmd=command)
    if exit_code or stdout_buffer or stderr_buffer:
        # Error may have happened
        raise APSHarvesterConversionError("%s: %s\nOut:%s" %
                                          (exit_code,
                                           stderr_buffer,
                                           stdout_buffer))


def create_records_from_file(path_to_file):
    """
    Wrapping function using docextract_record.create_record function to return a
    list of BibRecord structures.
    """
    from invenio.docextract_record import create_record

    fd_xml_file = open(path_to_file, "r")
    xml = fd_xml_file.read()
    fd_xml_file.close()

    return create_record(xml)


def create_records_from_string(xml):
    """
    Wrapping function using docextract_record.create_record function to return a
    list of BibRecord structures.
    """
    from invenio.docextract_record import create_record
    return create_record(xml)


def validate_date(date_given, date_format="%Y-%m-%d"):
    """
    Returns the date given if valid date format. If not,
    a ValueError exception is raised.
    """
    # FIXME: use datetime.datetime.strptime(date_given, "%Y-%m-%d")
    # after upgrading Python => 2.5
    return datetime.datetime(*(time.strptime(date_given, date_format)[0:6]))


def get_file_modified_date(filepath):
    """
    Returns the last modified date for given file as returned by os.stat(),
    but instead as a datetime object.
    """
    return datetime.datetime.fromtimestamp(os.path.getmtime(filepath))


def get_utc_from_datetime(datetime_obj, fmt="%Y-%m-%d %H:%M:%S"):
    """
    Convert to UTC date string in given format from datetime object.

    Ex: '2013-04-17 16:04:25'
    """
    return time.strftime(fmt, time.gmtime(time.mktime(datetime_obj.timetuple())))


def compare_datetime_to_iso8601_date(date_obj, iso8601_date):
    """
    Compares the given *local-time* object with a proper ISO8601
    date string. Date string expected to be '2013-07-18T16:31:46-0400'.

    The UTC offset will be taken into account.

    Returns True if the file modification date is older than given date.
    """
    # First we need to make all dates UTC
    date_obj_utc = get_utc_from_datetime(date_obj)

    if 'Z' not in iso8601_date:
        # Incoming date format looks like: '2013-07-18T16:31:46-0400'
        offset_from_utc = iso8601_date[-5:]  # Ex: '-0400'
        # offset_from_utc_hour = int(offset_from_utc[1:-2])
        # offset_from_utc_minutes = int(offset_from_utc[-2:])
        offset_from_utc_operator = offset_from_utc[0]

        stripped_date = iso8601_date[:-5]  # Ex: '2013-07-18T16:31:46'
        iso8601_date_obj = datetime.datetime(*time.strptime(stripped_date,
                                             "%Y-%m-%dT%H:%M:%S")[:-3])
        time_dt = datetime.timedelta(hours=int(offset_from_utc[1:-3]),
                                     minutes=int(offset_from_utc[-2:]))

        if offset_from_utc_operator == "-":
            iso8601_date_utc = iso8601_date_obj + time_dt
        elif offset_from_utc_operator == "+":
            iso8601_date_utc = iso8601_date_obj - time_dt
        iso8601_date_utc = iso8601_date_utc.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Incoming date format looks like: '2013-07-18T16:31:46Z'
        iso8601_date_utc = iso8601_date.replace("Z", "").replace("T", " ")

    return date_obj_utc < iso8601_date_utc


def create_work_folder(base_folder):
    """Returns the path of a working folder with a naming schema.

    Will return the path of a folder with a naming schema using dates
    in the specified base folder, with increment.

    For example: 2014-05.05.1
    """
    create_folders(base_folder)

    run = 1
    date = datetime.datetime.now().strftime("%Y.%m.%d")
    out_folder = os.path.join(base_folder, date + "-" + str(run))
    while(os.path.exists(out_folder)):
        run += 1
        out_folder = os.path.join(base_folder, date + "-" + str(run))
    os.mkdir(out_folder)
    return out_folder


def create_folders(new_folder):
    """Create folders if they do not exist"""
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
    return new_folder


def write_record_to_file(filename, record_list):
    """Writes a new MARCXML file to specified path from BibRecord list."""
    from invenio.bibrecord import record_xml_output

    if len(record_list) > 0:
        out = []
        out.append("<collection>")
        for record in record_list:
            if record != {}:
                out.append(record_xml_output(record))
        out.append("</collection>")
        if len(out) > 2:
            file_fd = open(filename, 'w')
            file_fd.write("\n".join(out))
            file_fd.close()
            return True


def get_record_from_doi(doi):
    """
    Given a DOI we fetch the record from the DB and return
    tuple of record id and last record update.

    @param doi: DOI identifier to match a record against
    @type doi: string/int

    @return: record ID of record found
    @rtype: int
    """
    if not doi:
        return

    # Search pattern returns intbitset, lets make it a list instead
    recids = list(search_pattern(p=doi, f=CFG_APSHARVEST_RECORD_DOI_TAG, m='e'))
    if not recids:
        return
    elif len(recids) != 1:
        raise APSHarvesterSearchError("DOI mismatch: %s did not find only 1 record: %s" %
                                      ",".join(recids))
    return int(recids[0])


def get_doi_from_record(recid):
    """
    Given a record ID we fetch it from the DB and return
    the first DOI found as specified by the config variable
    CFG_APSHARVEST_RECORD_DOI_TAG.

    @param recid:  record id record containing a DOI
    @type recid: string/int

    @return: first DOI found in record
    @rtype: string
    """
    if not recid:
        return

    record = BibFormatObject(int(recid))
    possible_dois = record.fields(CFG_APSHARVEST_RECORD_DOI_TAG[:-1])
    for doi in possible_dois:
        if '2' in doi and doi.get('2', "") == "DOI":
            # Valid DOI present, add it
            try:
                return doi['a']
            except KeyError:
                continue


def generate_xml_for_records(records, directory, prefix="apsharvest_result_",
                             suffix=".xml", pretty=True):
    """
    Given a list of APSRecord objects, generate a MARCXML containing Metadata
    and FFT for all of them.
    """
    new_filename = get_temporary_file(prefix=prefix,
                                      suffix=suffix,
                                      directory=directory)

    generated_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                    "<collection>\n%s\n</collection>" % \
                    ("\n".join([record.to_xml() for record in records]),)

    try:
        fd = open(new_filename, 'w')
        fd.write(generated_xml)
        fd.close()
    except IOError, e:
        write_message("\nException caught: %s" % e, sys.stderr)
        write_message(traceback.format_exc()[:-1])
        task_update_status("CERROR")
        return

    if pretty:
        return prettify_xml(new_filename)
    return new_filename


def prettify_xml(filepath):
    """
    Will prettify an XML file for better readability.

    Returns the new, pretty, file.
    """
    new_filename = "%s_pretty.xml" % (os.path.splitext(filepath)[0],)
    cmd = "xmllint --format %s" % (filepath,)
    exit_code, std_out, err_msg = run_shell_command(cmd=cmd,
                                                    filename_out=new_filename)
    if exit_code:
        write_message("\nError caught: %s" % (err_msg,))
        task_update_status("CERROR")
        return

    return new_filename


def submit_bibupload_for_records(mode, new_filename, silent):
    """
    Given a list of APSRecord objects, generate a bibupload job.

    NB: we do not change the modified date of the record as we otherwise
    would be caught by ourselves again.
    """
    if len(mode) == 1:
        mode = "-" + mode
    else:
        mode = "--" + mode

    task_arguments = []
    if silent:
        task_arguments.append("--notimechange")
    task_arguments.append(mode)
    task_arguments.append(new_filename)
    return task_low_level_submission("bibupload", "apsharvest",
                                     *tuple(task_arguments))


def is_beyond_threshold_date(threshold_date, fulltext_file):
    """
    Checks the given fulltext file to see if the published date is
    beyond the threshold or not. Returns True if it is beyond and
    False if not.
    """
    write_message("Checking the threshold...", verbose=3)
    with open(fulltext_file, "r") as fd:
        parsed_xml_tree = BeautifulSoup(fd, features="xml")
        # Looking for the published tag
        pub_element = parsed_xml_tree.find("pub-date", attrs={"pub-type": 'epub'})
        if not pub_element:
            # Is it old format?
            pub_element = parsed_xml_tree.find('published')
            if not pub_element:
                return False
            published_date = pub_element.get("date")
        else:
            # It is new format
            published_date = pub_element.get('iso-8601-date')
        return published_date < threshold_date
    # No published date found, impossible to check
    return False


def submit_records_via_ftp(filename, location=""):
    """Submits given file to FTP server as defined.

    The FTP server uploaded to is controlled with the config variables:

    CFG_FTP_AUTHENTICATION_FILE (netrc_file)
    CFG_FTP_SERVER

    @param filename: file to upload
    @type filename: str

    @param location: location on FTP server. Defaults to root.
    @type location: str
    """
    from invenio.config import (CFG_FTP_SERVER,
                                CFG_FTP_AUTHENTICATION_FILE,)

    try:
        ftp = FtpHandler(CFG_FTP_SERVER, netrc_file=CFG_FTP_AUTHENTICATION_FILE)
        ftp.upload(filename, location)
        ftp.close()
        write_message("%s successfully uploaded to FTP server" % filename)
    except Exception as e:
        write_message("Failed to upload %s to FTP server: %s\n%s"
                      % (filename, str(e), traceback.format_exc()))


def submit_records_via_mail(subject, body, toaddr):
    """
    Performs the call to mailutils.send_email to attach XML and submit
    via e-mail to the desired receipient (CFG_APSHARVEST_EMAIL).

    @param subject: email subject.
    @type subject: string

    @param body: email contents.
    @type body: string

    @return: returns the given taskid upon submission.
    @rtype: int
    """
    return send_email(fromaddr=CFG_SITE_SUPPORT_EMAIL,
                      toaddr=toaddr,
                      subject=subject,
                      content=body)
