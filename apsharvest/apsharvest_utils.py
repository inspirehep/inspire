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
from invenio.config import CFG_TMPDIR
from tempfile import mkdtemp, mkstemp
from invenio.bibdocfile import guess_format_from_url, \
                               calculate_md5_external


class InvenioFileChecksumError(Exception):
    """Exception raised when a file is not matching its checksum.
    """
    pass


def unzip(zipped_file, output_directory=None):
    """
    Uncompress a zipped file from given filepath to an (optional) location.
    If no location is given, a temporary folder will be generated inside
    CFG_TMPDIR, prefixed with "apsharvest_unzip_".
    """
    input_extension = guess_format_from_url(zipped_file)
    if not input_extension.endswith('.zip'):
        # Are you sure this is a zipfile?
        raise IOError("This is not a valid file to unzip")
    if not output_directory:
        # We create a temporary directory to extract our stuff in
        try:
            output_directory = mkdtemp(prefix="apsharvest_unzip_", dir=CFG_TMPDIR)
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
    for path, dirs, files in os.walk(os.path.abspath(root)):
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
    validated_files = []
    for filename in locate(md5key_filename, root=in_folder):
        file_fd = open(filename, 'r')
        contents = file_fd.readlines()
        for line in contents:
            split_line = line.split(' ')
            if len(split_line) == 2:
                hashkey, hashkey_target = split_line
                hashkey_target = os.path.join(os.path.dirname(filename), \
                                              hashkey_target.strip())
                hashkey = hashkey.strip()
                found_hashkey = calculate_md5_external(hashkey_target).strip()
                if found_hashkey != hashkey:
                    raise InvenioFileChecksumError("Error matching checksum of %s:"
                                                   " %s is not equal to %s" % \
                                                   (hashkey_target, \
                                                    found_hashkey, \
                                                    hashkey))
                validated_files.append(hashkey_target)
    return validated_files


def get_temporary_file(prefix="apsharvest_test_", suffix="", dir=""):
    """
    Using a similar interface as tempfile.mkstemp, this function wraps
    the call to mkstemp and returns a safe and closed filepath.
    """
    try:
        file_fd, filepath = mkstemp(prefix=prefix, \
                                    suffix=suffix, \
                                    dir=dir)
        os.close(file_fd)
    except IOError, e:
        try:
            os.remove(filepath)
        except Exception:
            pass
        raise e
    return filepath
