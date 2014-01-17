# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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
"""
	Returns template subject and content for:
	an institution ticket
"""
def get_template_data(record):
	from invenio.config import CFG_SITE_URL
	from invenio.bibrecord import record_get_field_value

	recid = record_get_field_value(record,'001','','','')
	queue = "INST_add+cor"
	subject = "new inst"
	content = "The record %(site)s/record/edit/%(recid)s has an unknown affiliation. The information given is:\n\n\
	Please create an Institutions record, if not done in the meantime, and update the paper at\
	 %(site)s/record/edit/%(recid)s with the correct inst short name." % { 'site' : CFG_SITE_URL, 'recid' : recid }
	return (queue, subject, content)