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

"""APSHarvest custom exceptions."""


class APSFileChecksumError(Exception):
    """Exception raised when a file is not matching its checksum.
    """
    pass


class APSHarvesterConversionError(Exception):
    """Exception raised when more a record cannot be converted using Java Saxon.
    """
    pass


class APSHarvesterSearchError(Exception):
    """Exception raised when more then one record is found while DOI matching.
    """
    pass


class APSHarvesterConnectionError(Exception):
    """Exception raised when unable to connect to APS servers.
    """
    pass


class APSHarvesterSubmissionError(Exception):
    """Exception raised when unable to submit new/updated records.
    """
    pass


class APSHarvesterFileExits(Exception):
    """Exception raised when local file is the newest.
    """
    pass
