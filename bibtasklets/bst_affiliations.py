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

"""Affiliation guess script.

Using BibAuthorId data generates a table with the affiliations for each
author appearing in a paper. This is used later in BibEdit to propose
affiliations for those authors that don't have one.
"""

from re import compile as re_compile
from re import split as re_split
from invenio.dbquery import run_sql

from invenio.dbquery import run_sql
from invenio.search_engine import perform_request_search
from invenio.bibformat import format_record as real_format_record
from invenio.bibauthorid_dbinterface import populate_table, get_name_by_bibref, \
                populate_partial_marc_caches, destroy_partial_marc_caches
from invenio.webauthorprofile_corefunctions import canonical_name, \
            _get_person_names_dicts_bai, _get_person_names_dicts_fallback

from invenio.webauthorprofile_config import deserialize as real_deserialize
from invenio.webauthorprofile_config import  CFG_WEBAUTHORPROFILE_USE_BIBAUTHORID, serialize

from invenio.bibtask import write_message, task_update_progress

import collections
import functools
import random
import gc

from zlib import decompress


year_pattern = re_compile(r'(\d{4})')
AVG_PAPERS_PER_BUNCH = 10000


class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   Keeps at most cache_limit elements. Deletes half of caches in case of overflow.
   '''
   cache_limit = 2000000
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache:
         return self.cache[args]
      else:
         value = self.func(*args)
         self.cache[args] = value
         if len(self.cache) > self.cache_limit:
             keys  = self.cache.keys()
             random.shuffle(keys)
             to_delete = keys[0:self.cache_limit/2]
             map(self.cache.pop, to_delete)
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)


get_name_by_bibref = memoized(get_name_by_bibref)

def gc_des(*args):
    gc.disable()
    x = real_deserialize(*args)
    gc.enable()
    return x

deserialize = memoized(gc_des)

cid_recid_association_cache = dict()
def populate_cid_cache():
    global cid_recid_association_cache
    cid_pid = run_sql("select data, personid from aidPERSONIDDATA where tag='canonical_name'")
    cid_pid = dict(cid_pid)
    pid_recs = run_sql('select personid, bibrec from aidPERSONIDPAPERS')
    pr = collections.defaultdict(list)
    for p,r in pid_recs:
        pr[p].append(int(r))
    cid_recid_association_cache = {'cid_pid':cid_pid , 'pid_recs':pr}

def cached_prs(rg,p):
    try:
        pid = cid_recid_association_cache['cid_pid'][p.split(':')[1]]
        return cid_recid_association_cache['pid_recs'][pid]
    except (IndexError, KeyError):
        return perform_request_search(rg=rg, p=p)

prs = cached_prs

format_cache = dict()
def populate_format_cache():
    global format_cache
    format_cache['WAPAFF'] = dict((k,decompress(v)) for k,v in run_sql("select id_bibrec, value from bibfmt where format='WAPAFF'"))
    format_cache['WAPDAT'] = dict((k,decompress(v)) for k,v in run_sql("select id_bibrec, value from bibfmt where format='WAPDAT'"))

def fake_format_record(recid, fmt):
    try:
        return format_cache[fmt][recid]+'!---THEDELIMITER---!'
    except KeyError:
        return ""

format_record = fake_format_record

def process_authors(pids):
    # get the author - paper associations for authors
    # with id: min_pid <= id < max_pid (excluding rejected papers)
    associations = set(run_sql("""select personid, bibref_table, bibref_value, bibrec
                                  from aidPERSONIDPAPERS
                                  where flag > -2
                                  and personid in ( %s ) """ % ' , '.join("'"+str(p)+"'" for p in pids)))


    # get mapping of: (bibref_table, bibref_value) -> name
    bibref_to_name = dict()
    bibrefs = set([(table, ref) for _, table, ref, _ in associations])
    counter = 0
    for bibref in bibrefs:
        counter += 1
        bibref_to_name[bibref] = get_name_by_bibref(bibref)
        write_message('Got name: %s for bibref: %s.' % (bibref_to_name[bibref], str(bibref)))

    # get mapping of: author -> affiliations
    pid_to_affiliations = dict()
    counterr = 0
    for pid in pids:
        counterr += 1
        pid_to_affiliations[pid] = get_affiliations_for_author(pid)
        write_message('Got affiliations: %s for author: %s.' % (pid_to_affiliations[pid], str(pid)))

    # get the affiliated records for this group of authors: (rec, name, affiliation, ... + some extra info)
    affiliated_records = list()
    for pid, table, ref, rec in associations:
        # we don't want to keep records which have no affiliation/s
        affiliations, year = pid_to_affiliations[pid]
        if not affiliations:
            continue
        affiliated_records += [rec, bibref_to_name[(table, ref)], serialize(affiliations), table, ref, year]

    # flush data to db
    if affiliated_records:
        write_message('Populating table with %s records.' % len(affiliated_records))
        populate_table('bibEDITAFFILIATIONS_tmp', ['bibrec','name','affiliations','bibref_table','bibref_value', 'year'], affiliated_records, empty_table_first=False)

    return len(affiliated_records)

def _get_institute_pubs_dict(recids, names_list):
    a = ''.join(format_record(x, 'WAPAFF') for x in recids)
    a = [deserialize(p) for p in a.strip().split('!---THEDELIMITER---!') if p]
    affdict = {}
    for rec, affs in a:
        keys = affs.keys()
        for name in names_list:
            if name in keys and affs[name][0]:
                for aff in affs[name]:
                    try:
                        affdict[aff].add(rec)
                    except KeyError:
                        affdict[aff] = set([rec])
    # the serialization function (msgpack.packb) cannot serialize a python set
    for key in affdict.keys():
        affdict[key] = list(affdict[key])
    return affdict

def get_affiliations_for_author(pid):
    # get all papers for the specified author
    # (different query for the search engine of INSPIRE and Atlantis db)
    names_dict = _get_person_names_dicts_bai(pid)
    cname = canonical_name(pid)
    recs = prs(0, 'author:%s' % str(cname))

    # get mapping of: affiliation -> papers
    names_list = names_dict['db_names_dict'].keys()
    affiliation_to_recs = _get_institute_pubs_dict(recs, names_list)

    # get mapping of: paper -> year it was written
    a = ''.join(format_record(r, 'WAPDAT') for r in recs)
    rec_to_years = [deserialize(p) for p in a.strip().split('!---THEDELIMITER---!') if p]

    # inverse the above mapping to: year -> papers that where written that year
    year_to_recs = dict()
    for rec, year_fields in rec_to_years:
        years = list()
        for date in year_fields['year_fields']:
            try:
                # 'date' may be in a form like: '1941-02-01'
                # so we extract the year from the date with regex
                years.append(int(re_split(year_pattern, date[0])[1]))
            except IndexError:
                continue
        if years:
        # from the set of years that the paper is
        # associated with we keep the oldest year
            try:
                year_to_recs[min(years)].add(rec)
            except KeyError:
                year_to_recs[min(years)] = set([rec])

    # we are interested in the affiliation of the paper/s
    # which were written most recently
    most_recent_papers = list()
    for year in sorted(year_to_recs.keys(), reverse=True):
        most_recent_papers.append((year_to_recs[year], year))

    # inverse the mapping of: affiliation -> papers
    # to: paper -> affiliations
    rec_to_aff = dict()
    for affiliation, papers in affiliation_to_recs.iteritems():
        for rec in papers:
            rec_to_aff.setdefault(rec, []).append(affiliation)

    # get the affiliations of the most recent papers
    affiliations = set()
    aff_year = None
    for papers, year in most_recent_papers:
        for rec in papers:
            try:
                for aff in rec_to_aff[rec]:
                    affiliations.add(aff)
            except KeyError:
                pass
        if affiliations:
            aff_year = year
            break

    return list(affiliations), aff_year


def bst_affiliations():
    # create temporary table
    task_update_progress("creating temporary table...")
    run_sql("""CREATE TABLE IF NOT EXISTS `bibEDITAFFILIATIONS_tmp` (
                  `bibrec` MEDIUMINT( 8 ) UNSIGNED NOT NULL ,
                  `name` VARCHAR( 256 ) NOT NULL ,
                  `affiliations` longblob ,
                  `bibref_table` ENUM(  '100',  '700' ) NOT NULL ,
                  `bibref_value` MEDIUMINT( 8 ) UNSIGNED NOT NULL ,
                  `year` SMALLINT UNSIGNED NOT NULL ,
                  INDEX `bibrec-b` (`bibrec`) ,
                  INDEX `name-b` (`name`) ,
                  INDEX `bibrec-name-b` (`bibrec`,`name`)
                ) ENGINE = MYISAM;""")

    run_sql("""truncate table `bibEDITAFFILIATIONS_tmp`""")

    task_update_progress("populating format cache")
    populate_format_cache()
    task_update_progress("populating perform_request_search by cid cache")
    populate_cid_cache()

    pids = list(set(x[0] for x in run_sql("select personid from aidPERSONIDPAPERS")))
    recs_num = dict(run_sql("""select personid, count(*) from aidPERSONIDPAPERS group by personid"""))
    total_pids = len(pids)
    # process authors in groups (of size INTERVAL_LENGTH)
    # each time, so not all records are brought into memory
    while True:
        pids_bunch = list()
        papers_bunch = 0
        while papers_bunch < AVG_PAPERS_PER_BUNCH:
            try:
                pid = pids.pop()
                pids_bunch.append(pid)
                papers_bunch += recs_num[pid]
            except IndexError:
                break
        if not pids_bunch:
            break
        #print "Processing ", papers_bunch, 'papers on ', len(pids_bunch), ' persons ' ,' cycle count: ', cycle_count
        process_authors(pids_bunch)
        task_update_progress('processed %s out of %s persons' % (total_pids-len(pids), total_pids))

    # copy data from one table to another
    task_update_progress('moving data to bibEDITAFFILIATIONS')
    run_sql("""truncate bibEDITAFFILIATIONS""")
    run_sql("""insert into bibEDITAFFILIATIONS select * from bibEDITAFFILIATIONS_tmp""")

if __name__ == '__main__':
    bst_affiliations()
