## This file is part of Invenio.
## Copyright (C) 2007, 2008, 2009, 2010, 2011 CERN.
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
"""Functions shared by websubmit_functions for ConfSubmit"""

import os
from invenio.config import CFG_SITE_LANG
from invenio.dbquery import run_sql
from invenio.bibsched import server_pid
from invenio.messages import gettext_set_language
from invenio.websubmit_functions.Shared_Functions import ParamFromFile

def get_confsubmit_message(curdir, ln=CFG_SITE_LANG):
    """
    @return: a message suitable to display to the user, explaining the current
        status of the system.
    @rtype: string
    """
    bibupload_id = ParamFromFile(os.path.join(curdir, 'bibupload_id'))
    if not bibupload_id:
        ## No BibUpload scheduled? Then we don't care about bibsched
        return ""
    ## Let's get an estimate about how many processes are waiting in the queue.
    ## Our bibupload might be somewhere in it, but it's not really so important
    ## WRT informing the user.
    _ = gettext_set_language(ln)
    res = run_sql("SELECT id,proc,runtime,status,priority FROM schTASK WHERE (status='WAITING' AND runtime<=NOW()) OR status='SLEEPING'")
    pre = _("Note that your submission has been inserted into the task queue and is waiting for execution.\n")
    if server_pid():
        ## BibSched is up and running
        msg = _("The task queue is currently running in automatic mode, and there are currently %s tasks waiting to be executed. Your record should be available within a few minutes and searchable within an hour or thereabouts.\n") % (len(res),)
    else:
        msg = _("Because of a human intervention or a temporary problem, the task queue is currently set to the manual mode. Your submission is well registered but may take longer than usual before it is fully integrated and searchable.\
n")

    return pre + msg

