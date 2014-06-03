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
import fnmatch
import zipfile
import codecs
import re
import datetime
import time

from tempfile import mkdtemp, mkstemp
from invenio.config import (CFG_FTP_SERVER,
                            CFG_FTP_AUTHENTICATION_FILE)
from harvestingkit.ftp_utils import FtpHandler


class InvenioFileChecksumError(Exception):
    """Exception raised when a file is not matching its checksum.
    """
    pass


class APSHarvesterConversionError(Exception):
    """Exception raised when more a record cannot be converted using Java Saxon.
    """
    pass


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
    InvenioFileChecksumError is returned.

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
                    raise InvenioFileChecksumError("Error matching checksum of %s:"
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
        folders = new_folder.split("/")
        folder = "/"
        for i in range(1, len(folders)):
            folder = os.path.join(folder, folders[i]).strip()
            if not os.path.exists(folder):
                os.mkdir(folder)


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


def upload_to_FTP(filename, location=''):
    """ Uploads a file to the FTP server"""
    ftp = FtpHandler(CFG_FTP_SERVER, netrc_file=CFG_FTP_AUTHENTICATION_FILE)
    ftp.upload(filename, location)
    ftp.close()
