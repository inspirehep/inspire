# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2012, 2013, 2014 CERN.
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
The APSharvest unit test suite

The tests will not modifiy the database.
"""

import unittest
import zipfile
from invenio.config import CFG_TMPSHAREDDIR
import os
from invenio.testutils import make_test_suite, run_test_suite
from invenio.apsharvest_utils import (unzip,
                                      find_and_validate_md5_checksums,
                                      get_temporary_file,
                                      validate_date,
                                      get_file_modified_date,
                                      compare_datetime_to_iso8601_date)
from invenio.bibdocfile import calculate_md5_external
from invenio.bibsched_tasklets.bst_apsharvest import APSRecord, APSRecordList


def get_files_and_folders(in_folder):
    """
    Returns a list of files and folders where folders
    are identified by os.sep suffix.
    """
    list_of_files_and_folders = []
    if os.path.isdir(in_folder):
        for path in os.listdir(in_folder):
            relative_path = os.path.join(in_folder, path)
            if os.path.isdir(relative_path):
                list_of_files_and_folders.append(relative_path + os.sep)
                list_of_files_and_folders.extend(get_files_and_folders(relative_path + os.sep))
            elif os.path.isfile(relative_path):
                list_of_files_and_folders.append(relative_path)
    return list_of_files_and_folders


class FileTest(unittest.TestCase):
    def test_unzip(self):
        """
        Test uncompressing function.
        """
        test_zipped_file = "./test/test.zip"

        desired_dir = os.path.join(CFG_TMPSHAREDDIR, 'apsharvest')
        unzipped_folder = unzip(test_zipped_file, desired_dir)
        self.assertTrue(unzipped_folder.startswith(desired_dir),
                        "Unzipped folder is located in the wrong place %s!" %
                        unzipped_folder)

        unzipped_folder = unzip(test_zipped_file)
        self.assertTrue(os.path.exists(unzipped_folder),
                        "Unzipped folder does not exist!")

        z = zipfile.ZipFile(test_zipped_file)
        list_of_zipfiles = z.namelist()
        found_list_of_files = get_files_and_folders(unzipped_folder)
        self.assertTrue(len(list_of_zipfiles) == len(found_list_of_files),
                        "Looks like all files were not extracted!")

    def test_md5_check(self):
        """
        Test md5 checking done by APS Harvester.
        """
        # Create temporary file to test with
        hashtarget_filepath = get_temporary_file(directory="/tmp")
        tmpfd = open(hashtarget_filepath, 'w')
        tmpfd.write("this is a test")
        tmpfd.close()
        dirpath, filename = os.path.split(hashtarget_filepath)

        hashtarget_md5 = calculate_md5_external(hashtarget_filepath)

        # Create a md5 keyfile looking like:
        # 54b0c58c7ce9f2a8b551351102ee0938 apsharvest_test_lFecZz
        md5_keyfile = get_temporary_file(directory="/tmp")
        tmpfd = open(md5_keyfile, 'w')
        tmpfd.write("%s %s\n" % (hashtarget_md5, filename))
        tmpfd.close()

        dirpath, filename = os.path.split(md5_keyfile)
        res = find_and_validate_md5_checksums(in_folder=dirpath, md5key_filename=filename)
        self.assertTrue(len(res) == 1)


class APSRecordTest(unittest.TestCase):
    def test_adding_record(self):
        l = APSRecordList()
        r1 = APSRecord(1, doi=["dummy"])
        l.append(r1)
        self.assertEqual(1, len(l))

        r2 = APSRecord(1, doi=["dummy2"])
        l.append(r2)
        self.assertEqual(1, len(l))


class APSUtilsTest(unittest.TestCase):
    def test_date_validation(self):
        self.assertTrue(validate_date("2012-12-12"))
        self.assertTrue(validate_date("2012-12-12 12:12:12",
                                      date_format="%Y-%m-%d %H:%M:%S"))
        self.assertRaises(ValueError, validate_date, "201222-2-12")
        self.assertRaises(ValueError, validate_date, "202-22-12")
        self.assertRaises(ValueError, validate_date, "2012-22-12")
        self.assertRaises(ValueError, validate_date, "2012-02-42")

    def test_date_comparison(self):
        target_filepath = get_temporary_file(directory="/tmp")
        file_last_modified = get_file_modified_date(target_filepath)
        comparison_date = "2013-07-18T16:31:46-0400"
        self.assertFalse(compare_datetime_to_iso8601_date(file_last_modified,
                                                          comparison_date))
        comparison_date = "2013-07-18T16:31:46Z"
        self.assertFalse(compare_datetime_to_iso8601_date(file_last_modified,
                                                          comparison_date))

TEST_SUITE = make_test_suite(FileTest, APSRecordTest, APSUtilsTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
