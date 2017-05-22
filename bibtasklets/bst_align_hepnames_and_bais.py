#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys

from invenio.dbquery import run_sql
from invenio.search_engine import get_collection_reclist, get_record
from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances
from invenio.bibtaskutils import ChunkedBibUpload
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.bibauthorid_dbinterface import add_external_id_to_author
from invenio.bibtask import write_message, task_update_progress

def valid_bai(bai):
    return re.match(r"([\w\-']+\.)+\d+", bai.decode('utf8'), re.U)


def valid_orcid(orcid):
    return re.match(r'\d{4}-\d{4}-\d{4}-\d{3}[0-9X]', orcid.upper())


def valid_inspire(inspire):
    return re.match(r'INSPIRE-\d{8}', inspire)


def valid_kaken(kaken):
    return re.match(r'\d{8}', kaken)


def build_hepnames_knowledge():
    recids = get_collection_reclist('HepNames')
    ret = {}
    for recid in recids:
        ids = {'recid': recid}
        record = get_record(recid)
        for field in record_get_field_instances(record, '035'):
            id_type = None
            id_value = None
            for code, value in field_get_subfield_instances(field):
                code = code.strip()
                value = value.strip()
                if code == '9':
                    if id_type and id_type != value.upper():
                        write_message("ERROR: http://inspirehep.net/record/{recid} has invalid IDs".format(recid=recid), stream=sys.stderr)
                        break
                    id_type = value.upper()
                if code == 'a':
                    if id_value and id_value != value:
                        write_message("ERROR: http://inspirehep.net/record/{recid} has invalid IDs".format(recid=recid), stream=sys.stderr)
                        break
                    id_value = value
            if not id_type or not id_value:
                # Incomplete IDs
                continue
            else:
                if id_type == 'BAI':
                    if not valid_bai(id_value):
                        write_message("ERROR: http://inspirehep.net/record/{recid} has invalid BAI: {value}".format(recid=recid, value=id_value), stream=sys.stderr)
                        continue
                elif id_type == 'INSPIRE':
                    if not valid_inspire(id_value):
                        write_message("ERROR: http://inspirehep.net/record/{recid} has invalid INSPIRE: {value}".format(recid=recid, value=id_value), stream=sys.stderr)
                        continue
                elif id_type == 'ORCID':
                    if not valid_orcid(id_value):
                        write_message("ERROR: http://inspirehep.net/record/{recid} has invalid ORCID: {value}".format(recid=recid, value=id_value), stream=sys.stderr)
                        continue
                elif id_type == 'KAKEN':
                    if not valid_kaken(id_value):
                        write_message("ERROR: http://inspirehep.net/record/{recid} has invalid KAKEN: {value}".format(recid=recid, value=id_value), stream=sys.stderr)
                        continue
                ids[id_type] = id_value.upper()
                if id_type == 'BAI':
                    ids['ORIGINAL_BAI'] = id_value
        ret[recid] = ids
    return ret.values()


def build_bai_knowledge():
    ret = {}
    for personid, tag, data in run_sql("SELECT personid, tag, data FROM aidPERSONIDDATA WHERE tag LIKE 'extid:%' OR tag = 'canonical_name' or tag = 'uid'"):
        if tag == 'canonical_name':
            tag = 'BAI'
        elif tag == 'extid:INSPIREID':
            tag = 'INSPIRE'
        elif tag == 'extid:ORCID':
            tag = 'ORCID'
        elif tag == 'extid:KAKEN':
            tag = 'KAKEN'
        elif tag == 'uid':
            tag = 'UID'
        else:
            continue
        data = data.strip()
        if personid not in ret:
            ret[personid] = {'personid': personid}
        if tag in ret[personid]:
            write_message("ERROR: http://inspirehep.net/author/profile/{personid} has invalid IDs".format(personid=personid), stream=sys.stderr)
            continue
        ret[personid][tag] = data.upper()
        if tag == 'BAI':
            ret[personid]['ORIGINAL_BAI'] = data
    return ret.values()


def format_entry(entry):
    if 'recid' in entry:
        return "http://inspirehep.net/record/{recid} ({ids})".format(recid=entry['recid'], ids=', '.join(["%s:%s" % item for item in entry.items()]))
    elif 'personid' in entry:
        return "http://inspirehep.net/author/profile/{personid} ({ids})".format(personid=entry['personid'], ids=', '.join(["%s:%s" % item for item in entry.items()]))
    assert False


def project_ids(kb, id_type):
    ret = {}
    broken = []
    for value in kb:
        if id_type not in value:
            continue
        if value[id_type] in ret:
            write_message("ERROR: duplicate usage of {id_type}:{id_value}: {entry1} Vs. {entry2}".format(id_type=id_type, id_value=value[id_type], entry1=format_entry(ret[value[id_type]]), entry2=format_entry(value)), stream=sys.stderr)
            broken.append(value)
        ret[value[id_type]] = value
    return ret, broken


def filter_out_broken_ids(hepname_kb, bai_kb):
    broken = []
    for id_type in ('BAI', 'INSPIRE', 'ORCID', 'KAKEN'):
        broken.extend(project_ids(hepname_kb, id_type)[1])
        broken.extend(project_ids(bai_kb, id_type)[1])
    write_message("Broken entries: {len}".format(len=len(broken)), stream=sys.stderr)
    broken_ids = {}
    for elem in broken:
        for key, value in elem.iteritems():
            if key not in broken_ids:
                broken_ids[key] = set([value])
            else:
                broken_ids[key].add(value)
    new_hepname_kb = []
    for elem in hepname_kb:
        for key, value in elem.iteritems():
            if value in broken_ids.get(key, set()):
                break
        else:
            new_hepname_kb.append(elem)

    new_bai_kb = []
    for elem in bai_kb:
        for key, value in elem.iteritems():
            if value in broken_ids.get(key, set()):
                break
        else:
            new_bai_kb.append(elem)

    return new_hepname_kb, new_bai_kb


def align_entries(hepname_kb, bai_kb):
    hepname_updates= {}
    bai_updates = {}
    for key in ('ORCID', 'BAI', 'INSPIRE', 'KAKEN'):
        projected_hepnames = project_ids(hepname_kb, key)[0]
        projected_bais = project_ids(bai_kb, key)[0]
        for id_value in set(projected_hepnames.iterkeys()) & set(projected_bais.iterkeys()):
            merged_entry = dict(projected_hepnames[id_value].items())
            for key, value in projected_bais[id_value].iteritems():
                if key in merged_entry and merged_entry[key].upper() != value.upper():
                    write_message("ERROR: conflicting entries {entry1} Vs. {entry2}".format(entry1=format_entry(projected_hepnames[id_value]), entry2=format_entry(projected_bais[id_value])))
                    break
            else:
                merged_entry.update(projected_bais[id_value])
                if (set(merged_entry.keys()) ^ set(projected_hepnames[id_value].keys())) & set(['ORCID', 'BAI', 'INSPIRE', 'KAKEN']):
                    write_message("INFO: {hepname} should be updated to {merged_entry}".format(hepname=format_entry(projected_hepnames[id_value]), merged_entry=format_entry(merged_entry)))
                    recid = merged_entry['recid']
                    if recid in hepname_updates:
                        if hepname_updates[recid] != merged_entry:
                            write_message("ERROR: conflict for recid {recid}: {entry1} Vs. {entry2}".format(recid=recid, entry1=format_entry(hepname_updates[recid]), entry2=format_entry(merged_entry)), stream=sys.stderr)
                    else:
                        hepname_updates[recid] = merged_entry

                if (set(merged_entry.keys()) ^ set(projected_bais[id_value].keys())) & set(['ORCID', 'BAI', 'INSPIRE', 'KAKEN']):
                    write_message("INFO: {bai} should be updated to {merged_entry}".format(bai=format_entry(projected_bais[id_value]), merged_entry=format_entry(merged_entry)))
                    personid = merged_entry['personid']
                    if personid in bai_updates:
                        if bai_updates[personid] != merged_entry:
                            write_message("ERROR: conflict for personid {personid}: {entry1} Vs. {entry2}".format(personid=personid, entry1=format_entry(bai_updates[recid]), entry2=format_entry(merged_entry)), stream=sys.stderr)
                    else:
                        bai_updates[personid] = merged_entry
    return hepname_updates, bai_updates


def apply_hepnames_updates(hepname_updates):
    bibupload = ChunkedBibUpload(mode='a', user='align_hepnames_and_bais')
    for recid, entry in hepname_updates.iteritems():
        record = {}
        record_add_field(record, '001', controlfield_value=str(recid))
        for key, value in entry.iteritems():
            if key in ('ORCID', 'ORIGINAL_BAI', 'INSPIRE', 'KAKEN'):
                if key == 'ORIGINAL_BAI':
                    key = 'BAI'
                record_add_field(record, '035', subfields=[('a', value), ('9', key)])
        write_message(record_xml_output(record))
        bibupload.add(record_xml_output(record))


def apply_bai_updates(bai_updates):
    for personid, entry in bai_updates.iteritems():
        for key, value in entry.iteritems():
            if key in ('ORCID', 'INSPIRE', 'KAKEN'):
                if key == 'INSPIRE':
                    key = 'INSPIREID'
                add_external_id_to_author(personid, key, value)
                write_message("{personid} -> {key}: {value}".format(personid=personid, key=key, value=value))


def bst_align_hepnames_and_bais():
    task_update_progress("Building HEPNames KB")
    hepname_kb = build_hepnames_knowledge()
    task_update_progress("Building BAI KB")
    bai_kb = build_bai_knowledge()
    task_update_progress("Filtering out broken IDs")
    hepname_kb, bai_kb = filter_out_broken_ids(hepname_kb, bai_kb)
    task_update_progress("Aligning entries")
    hepname_updates, bai_updates = align_entries(hepname_kb, bai_kb)
    task_update_progress("Applying HEPNames updates")
    apply_hepnames_updates(hepname_updates)
    task_update_progress("Applying BAI updates")
    apply_bai_updates(bai_updates)


if __name__ == "__main__":
    bst_align_hepnames_and_bais()
