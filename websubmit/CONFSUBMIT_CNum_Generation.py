## This file is part of Invenio.
## Copyright (C) 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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
"""Description:   function CONFSUBMIT_CNum_Generation
                  This function creates a reference for the submitted
                  document and saves it in the specified file.
    Author:       L.Barnes / J. Lavik"""
__revision__ = "$Id$"

import os
from invenio.sequtils_cnum import CnumSeq

def CONFSUBMIT_CNum_Generation(parameters, curdir, form, user_info=None):
    """
    This function creates a reference for the submitted
    document and saves it in the specified 'edsrn' file.

    After generating the reference, also sets the global variable 'rn'
    containing this reference.

    Parameters:

      * cnum: name of the file in which the cnum is saved
      * sdat: name of the file in which the start-date is saved
    """
    fp = open("%s/%s" % (curdir,parameters['sdat']),"r")
    start_date = fp.read()
    fp.close()

    cnum_seq = CnumSeq()
    new_cnum = cnum_seq.next_value(start_date=start_date.strip())
    # The program must automatically generate the report number
    # The file cnumfile is created in the submission directory, and it stores the c-number
    fp = open("%s/%s" % (curdir, parameters['cnum']), "w")
    fp.write(new_cnum)
    fp.close()
