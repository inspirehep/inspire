import sys
import time

from datetime import datetime
from functools import partial
from ftplib import FTP
from os import listdir
from os.path import join, walk
from tarfile import TarFile
from tempfile import mkdtemp
from xml.dom.minidom import parseString, parse
from zipfile import ZipFile

from contrast_out_config import *
from invenio.config import (CFG_CONTRASTOUT_DOWNLOADDIR, CFG_TMPSHAREDDIR)
from invenio.scoap3utils import (MD5Error,
                                 NoNewFiles,
                                 FileTypeError,
                                 progress_bar,
                                 check_pkgs_integrity)
from invenio.contrast_out_utils import (contrast_out_cmp,
                                        find_package_name)
from invenio.minidom_utils import (xml_to_text,
                                   get_value_in_tag)
from invenio.errorlib import register_exception

CFG_READY_PACKAGES = join(CFG_CONTRASTOUT_DOWNLOADDIR, "ready_pkgs")
CFG_TAR_FILES = join(CFG_CONTRASTOUT_DOWNLOADDIR, "tar_files")

class ContrastOutConnector(object):
    def __init__(self, logger):
        self.ftp = None
        self.files_list = []
        self.retrieved_packages = {}
        self.retrieved_packages_unpacked = []
        self.path = None
        self.retrieved_packages_unpacked = []
        self.found_articles = []
        self.found_issues = []
        self.path_r_pkg = []
        self.logger = logger

    def connect(self):
        """Logs into the specified ftp server and returns connector."""
        try:
            self.ftp = FTP(CFG_CONTRAST_OUT_URL)
            self.ftp.login(user=CFG_CONTRAST_OUT_LOGIN, passwd=CFG_CONTRAST_OUT_PASSWORD)
            self.logger.debug("Succesful connection to the Elsevier server")
        except Exception as err:
            self.logger.error("Faild to connect to the Elsevier server. %s" % (err,))
            raise Exception

    def _get_file_listing(self, phrase=None, new_only=True):
        if phrase:
            self.files_list = filter(lambda x: phrase in x, self.ftp.nlst())
        else:
            self.files_list = self.ftp.nlst()
        if new_only:
            self.files_list = set(self.files_list) - set(listdir(CFG_READY_PACKAGES))

        return self.files_list

    def _download_file_listing(self):
        if self.files_list:
            # Prints stuff
            print >> sys.stdout, "\nDownloading %i \".ready\" files." % (len(self.files_list))
            # Create progrss bar
            p_bar = progress_bar(len(self.files_list))
            # Print stuff
            sys.stdout.write(p_bar.next())
            sys.stdout.flush()

            for filename in self.files_list:
                self.logger.info("Downloading: %s" % (filename,))
                pkg_path = join(CFG_READY_PACKAGES, filename)
                self.path_r_pkg.append(pkg_path)
                try:
                    ready_file = open(pkg_path, 'wb')
                    self.ftp.retrbinary('RETR %s' % (filename,), ready_file.write)
                    ready_file.close()
                except:
                    self.logger.error("Error downloading file: %s" % (filename,))
                    print >> sys.stdout, "\nError downloading %s file!" % (filename,)
                    print >> sys.stdout, sys.exc_info()
                # Print stuff
                sys.stdout.write(p_bar.next())
                sys.stdout.flush()
            return self.path_r_pkg
        else:
            print >> sys.stdout, "No new packages to download."
            self.logger.info("No new packages to download.")
            raise NoNewFiles

    def _get_packages(self):
        # Prints stuff
        print >> sys.stdout, "\nRetrieving packages names."
        # Create progrss bar
        p_bar = progress_bar(len(self.files_list))
        # Print stuff
        sys.stdout.write(p_bar.next())
        sys.stdout.flush()

        for pack in self.path_r_pkg:
            self.logger.info("Retrieved package name: %s" % (pack,))
            pack_xml = parse(pack)
            package_file = pack_xml.getElementsByTagName('dataset-package-file')
            for pf in package_file:
                filename = pf.getElementsByTagName('filename')[0]
                md5_val = pf.getElementsByTagName('md5')[0]
                self.retrieved_packages[xml_to_text(filename)] = xml_to_text(md5_val)
             # Print stuff
            sys.stdout.write(p_bar.next())
            sys.stdout.flush()

        return self.retrieved_packages

    def _download_tars(self, check_integrity=True):
        if check_integrity:
            check_pkgs_integrity(self.retrieved_packages, self.logger, self.ftp)

        print >> sys.stdout, "\nDownloading %i tar packages." \
                 % (len(self.retrieved_packages))
        # Create progrss bar
        p_bar = progress_bar(len(self.files_list))
        # Print stuff
        sys.stdout.write(p_bar.next())
        sys.stdout.flush()

        for filename in self.retrieved_packages.iterkeys():
            self.logger.info("Downloading tar package: %s" % (filename,))
            unpack_path = join(CFG_TAR_FILES, filename)
            self.retrieved_packages_unpacked.append(unpack_path)
            try:
                tar_file = open(unpack_path, 'wb')
                self.ftp.retrbinary('RETR %s' % filename, tar_file.write)
                tar_file.close()
            except:
                register_exception(alert_admin=True, prefix="Elsevier package download faild.")
                self.logger.error("Error downloading tar file: %s" % (filename,))
                print >> sys.stdout, "\nError downloading %s file!" % (filename,)
                print >> sys.stdout, sys.exc_info()
            # Print stuff
            sys.stdout.write(p_bar.next())
            sys.stdout.flush()

        return self.retrieved_packages_unpacked

    def _check_md5(self):
        import hashlib

        for filename, md5 in self.retrieved_packages.iteritems():
            our_md5 = hashlib.md5(open(join(CFG_TAR_FILES, filename)).read()).hexdigest()
            try:
                if our_md5 != md5:
                    raise MD5Error(filename)
            except MD5Error as e:
                register_exception(alert_admin=True, prefix="Elsevier MD5 error.")
                self.logger.error("MD5 error: %s" % (filename,))
                print >> sys.stdout, "\nError in MD5 of %s" % (filename,)
                print >> sys.stdout, "oryginal: %s, ours: %s" % (md5, our_md5)

    def _extract_packages(self):
        """
        Extract a package in a new temporary directory.
        """
        self.path_unpacked = mkdtemp(prefix="scoap3_package_", dir=CFG_TMPSHAREDDIR)
        for path in self.retrieved_packages_unpacked:
            try:
                if ".tar" in path:
                    TarFile.open(path).extractall(self.path_unpacked)
                elif ".zip" in path:
                    ZipFile(path).extractall(self.path_unpacked)
                else:
                    raise FileTypeError("It's not a TAR or ZIP archive.")
            except:
                register_exception(alert_admin=True, prefix="Elsevier error extracting package.")
                self.logger.error("Error extraction package file: %s" % (path,))
                print >> sys.stdout, "\nError extracting package file: %s" % (path,)

        return self.path_unpacked

    def _get_issues(self):
        for name in self.files_list:
            dataset_link = join(self.path_unpacked, name.split('.')[0], 'dataset.xml')

            try:
                dataset_xml = parse(dataset_link)
            except Exception, err:
                register_exception(alert_admin=True, prefix="Elsevier error reading dataset.xml file.")
                self.logger.error("Error reading dataset.xml file: %s" % (dataset_link,))
                print >> sys.stdout, "\nError reading dataset.xml file: %s" % (dataset_link,)
                continue

            journal_issues = dataset_xml.getElementsByTagName('journal-issue')
            if journal_issues:
                for journal_issue in journal_issues:
                    filename = xml_to_text(journal_issue.getElementsByTagName('ml')[0].getElementsByTagName('pathname')[0])
                    self.logger.info("Found issue %s in %s." % (filename, name))
                    pathname = join(self.path_unpacked, name.split('.')[0], filename)
                    self.found_issues.append(pathname)
            else:
                def visit(arg, dirname, names):
                    if "issue.xml" in names:
                        self.found_issues.append(join(dirname, "issue.xml"))
                walk(join(self.path_unpacked, name.split('.')[0]), visit, None)
        return self.found_issues

    def _get_metadata_and_fulltex_dir(self):
        # Prints stuff
        print >> sys.stdout, "\nRetrieving journal items directories."
        # Create progrss bar
        p_bar = progress_bar(len(self.files_list))
        # Print stuff
        sys.stdout.write(p_bar.next())
        sys.stdout.flush()

        for name in self.files_list:
            dataset_link = join(self.path_unpacked, name.split('.')[0], 'dataset.xml')

            try:
                dataset_xml = parse(dataset_link)
            except Exception, err:
                register_exception(alert_admin=True, prefix="Elsevier error reading dataset.xml file.")
                self.logger.error("Error reading dataset.xml file: %s" % (dataset_link,))
                print >> sys.stdout, "\nError reading dataset.xml file: %s" % (dataset_link,)
                continue

            # created = get_value_in_tag(dataset_xml.getElementsByTagName('dataset-unique-ids')[0], 'timestamp')
            journal_items = dataset_xml.getElementsByTagName('journal-item')
            self.logger.info("Getting metadata and fulltex directories for %i journal items." % (len(journal_items),))
            for journal_item in journal_items:
                xml_pathname = join(self.path_unpacked, name.split('.')[0], xml_to_text(journal_item.getElementsByTagName('ml')[0].getElementsByTagName('pathname')[0]))
                pdf_pathname = join(self.path_unpacked, name.split('.')[0], xml_to_text(journal_item.getElementsByTagName('web-pdf')[0].getElementsByTagName('pathname')[0]))
                self.found_articles.append(dict(xml=xml_pathname, pdf=pdf_pathname))
            self.logger.info("Got metadata and fulltex directories of %i journals." % (len(self.found_articles),))
            # Print stuff
            sys.stdout.write(p_bar.next())
            sys.stdout.flush()

        self.sort_results()
        return self.found_articles

    def sort_results(self):
        self.found_articles = sorted(self.found_articles, key=lambda x: find_package_name(x['xml']), cmp=contrast_out_cmp)

    def run(self):
        self.connect()
        self._get_file_listing('.ready')
        try:
            self._download_file_listing()
        except:
            self.logger.info("No new packages to process.")
            print >> sys.stdout, "No new packages to process."
            return
        self._get_packages()
        self._download_tars()
        self._check_md5()
        self._extract_packages()
        self._get_metadata_and_fulltex_dir()
