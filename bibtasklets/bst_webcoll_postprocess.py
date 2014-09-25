#!/usr/bin/env python

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
import requests
from invenio.bibtask import (write_message,
                             task_update_status)
from invenio.config import CFG_WEBCOLL_POST_REQUEST_URL


def bst_webcoll_postprocess(recids=[]):
    session = requests.Session()
    addapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount(CFG_WEBCOLL_POST_REQUEST_URL, addapter)
    response = session.post(CFG_WEBCOLL_POST_REQUEST_URL,
                            data={'recids': recids})
    if response.ok:
        write_message("Post request sent successfully,"
                      " closing connection!")
        session.close()
    else:
        write_message("Post request failed!")
        task_update_status('ERROR')
