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

"""Invenio Bibliographic Tasklet.

Move a local dbdump to AFS.
"""

import shutil
import os
from invenio.dbquery import CFG_DATABASE_NAME
from invenio.bibtask import write_message, task_update_progress
from invenio.dbdump import _delete_old_dumps


def bst_move_dbdump(sourcedir, destdir, number_to_keep):
    """
    Will move a MySQL dump from local machine to a remote space.

    @param sourcedir: directory where the local dump is stored.
    @type sourcedir: string

    @param destdir: directory where the dump should live.
    @type destdir: string
    """
    output_file_prefix = CFG_DATABASE_NAME + '-dbdump-'
    files = [x for x in os.listdir(sourcedir)
             if x.startswith(output_file_prefix)]
    task_update_progress("Starting moving of database-dump")
    if len(files) != 1:
        write_message("... none or too many files found. Exiting.")
        return
    filename = files[0]
    full_path_source = sourcedir + os.sep + filename
    write_message("... moving %s" % (full_path_source,))
    full_path_destination = destdir + os.sep + filename
    try:
        shutil.copy(full_path_source, full_path_destination)
    except Exception, e:
        write_message("... could not move %s to %s: %s" %
                      (full_path_source, full_path_destination, str(e)))
        return
    if os.path.getsize(full_path_source) == \
       os.path.getsize(full_path_destination):
        write_message("... move completed. Removing %s" % (full_path_source,))
        os.remove(full_path_source)
        _delete_old_dumps(destdir, output_file_prefix, number_to_keep)
        task_update_progress("Completed database dump move")
    else:
        write_message("File was not successfully copied.")
        task_update_progress("Database dump move failed")
