import sys
import os
import time
import shutil

from invenio.intbitset import intbitset
from invenio.config import CFG_CERN_SITE, CFG_INSPIRE_SITE, CFG_SITE_NAME, CFG_TMPSHAREDDIR
from invenio.search_engine import perform_request_search, get_collection_reclist, search_pattern
from invenio.search_engine import get_record
from invenio.bibrecord import record_get_field_instances, record_get_field_values, field_get_subfield_instances, record_add_field, record_xml_output
from invenio.bibtask import write_message, task_update_progress, task_low_level_submission, task_sleep_now_if_required


if CFG_INSPIRE_SITE:
    CFG_THIS_SITE = "Inspire"
    CFG_OTHER_SITE = "CDS"
elif CFG_CERN_SITE:
    CFG_THIS_SITE = "CDS"
    CFG_OTHER_SITE = "Inspire"

CFG_SHARED_PATH = '/afs/cern.ch/project/inspire/cds-synchro'
CFG_EXPORT_FILE = os.path.join(CFG_SHARED_PATH, '%s2%s.ids' % (CFG_THIS_SITE, CFG_OTHER_SITE))
CFG_IMPORT_FILE = os.path.join(CFG_SHARED_PATH, '%s2%s.ids' % (CFG_OTHER_SITE, CFG_THIS_SITE))

COUNTER = 0
NOW = time.strftime('%Y%m%d%H%M%S')

def get_out_file():
    global COUNTER
    COUNTER += 1
    filename = os.path.join(CFG_TMPSHAREDDIR, 'inspireids-%s-%03d.xml' % (NOW, COUNTER))
    print "--> Outputting to %s" % filename
    return open(filename, "w")

def get_all_recids():
    if CFG_INSPIRE_SITE:
        all_recids = get_collection_reclist(CFG_SITE_NAME)
    elif CFG_CERN_SITE:
        all_recids = get_collection_reclist(CFG_SITE_NAME) | get_collection_reclist("CERN Articles & Preprints") | get_collection_reclist("CERN Series") | get_collection_reclist("CERN Departments") | get_collection_reclist("CERN Experiments") | get_collection_reclist("CERN R&D Projects")
    else:
        all_recids = intbitset()
    return all_recids

def get_record_ids_to_export():
    all_recids = get_all_recids()
    recids_with_a_doi = search_pattern(p='doi:"**"')
    recids_with_an_arxiv_id = search_pattern(p='035__9:"arXiv"')
    recids_with_other_id = search_pattern(p='035__9:%s' % CFG_OTHER_SITE)
    return (recids_with_a_doi | recids_with_an_arxiv_id | recids_with_other_id) & all_recids

def get_ids_from_recid(recid):
    record = get_record(recid)

    ## Retrieving DOI
    doi = ""
    dois = record_get_field_values(record, '024', '7', code='a')
    dois = [doi for doi in dois if doi.startswith('10.')]
    if len(dois) > 1:
        print >> sys.stderr, "WARNING: record %s have more than one DOI: %s" % (recid, dois)
    elif len(dois) == 1:
        doi = dois[0]

    ## Retrieving arXiv eprint
    eprint = ""
    eprints = record_get_field_values(record, '035', code='a')
    eprints = [an_eprint[len('oai:arXiv.org:'):] for an_eprint in eprints if an_eprint.lower().startswith('oai:arxiv.org:')]
    if len(eprints) > 1:
        print >> sys.stderr, "WARNING: record %s have more than one arXiv eprint: %s" % (recid, eprints)
    elif len(eprints) == 1:
        eprint = eprints[0]

    ## Retrieving Other service ID
    other_id = ''
    for field in record_get_field_instances(record, '035'):
        subfields = dict(field_get_subfield_instances(field))
        if subfields.get('9', '').upper() == CFG_OTHER_SITE.upper() and subfields.get('a'):
            other_id = subfields['a']
    reportnumbers = record_get_field_values(record, '037', code='a')
    return [str(recid), doi, eprint, other_id] + reportnumbers

def iter_export_rows(recids=None):
    if recids is None:
        recids = get_record_ids_to_export()
    for recid in recids:
        ids = get_ids_from_recid(recid)
        yield '\t'.join(ids)

def add_other_id(other_id=None, doi="", eprint="", recid=None, reportnumbers=None, all_recids=None):
    if all_recids is None:
        all_recids = get_all_recids()
    if reportnumbers is None:
        reportnumbers = []
    if recid is not None and recid not in all_recids:
        write_message("WARNING: %s thought that their record %s had recid %s in %s but this seems wrong" % (CFG_OTHER_SITE, other_id, recid, CFG_THIS_SITE), stream=sys.stderr)
        recid = None
    if recid is None and eprint:
        arxiv_ids = search_pattern(p='oai:arXiv.org:%s' % (eprint,), f='035__a', m='e') & all_recids
        if len(arxiv_ids) > 1:
            write_message("ERROR: %s record %s matches more than one record in %s via arXiv eprint matching: %s" % (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, arxiv_ids), stream=sys.stderr)
            return
        elif len(arxiv_ids) == 1:
            recid = arxiv_ids[0]
    if recid is None and doi:
        doi_ids = search_pattern(p='doi:"%s"' % doi) & all_recids
        if len(doi_ids) > 1:
            write_message("ERROR: %s record %s matches more than one record in %s via DOI matching: %s" % (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, doi_ids), stream=sys.stderr)
            return
        elif len(doi_ids) == 1:
            recid = doi_ids[0]
    if recid is None and reportnumbers:
        reportnumbers_ids = intbitset()
        for rn in reportnumbers:
            reportnumbers_ids |= search_pattern(p=rn, f='037__a', m='e')
        reportnumbers_ids &= all_recids()
        if len(reportnumbers_ids) > 1:
            write_message("ERROR: %s record %s matches more than one record in %s via reportnumber matching: %s" % (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, reportnumbers_ids), stream=sys.stderr)
            return
        elif len(reportnumbers_ids) == 1:
            recid = reportnumbers_ids[0]
    if recid:
        record = get_record(recid)
        fields = record_get_field_instances(record, '035')
        for field in fields:
            subfields = dict(field_get_subfield_instances(field))
            if CFG_OTHER_SITE.upper() == subfields.get('9', '').upper():
                stored_recid = int(subfields.get('a', 0))
                if stored_recid and stored_recid != other_id:
                    write_message("ERROR: %s record %s matches %s record %s which already points back to a different record %s in %s" % (CFG_OTHER_SITE, other_id, CFG_THIS_SITE, recid, stored_recid, CFG_OTHER_SITE), stream=sys.stderr)
                return
        rec = {}
        record_add_field(rec, '001', controlfield_value='%s' % recid)
        record_add_field(rec, '035', ind1=' ', ind2=' ', subfields=(('9', CFG_OTHER_SITE), ('a', other_id)))
        return record_xml_output(rec)

def import_recid_list(input_stream=sys.stdin):
    all_recids = get_all_recids()
    output_file = get_out_file()
    i = 0
    for row in input_stream:
        if row.endswith('\n'):
            row = row[:-1]
        row = row.split('\t')
        if row:
            other_id, doi, eprint, recid, reportnumbers = row[0], row[1], row[2], row[3], row[4:]
            if other_id:
                other_id = int(other_id)
            else:
                other_id = None
            if recid:
                recid = int(recid)
            else:
                recid = None
            try:
                result = add_other_id(other_id, doi, eprint, recid, reportnumbers, all_recids)
            except Exception, err:
                write_message("ERROR: unexpected error where calling add_other_id(%s, %s, %s, %s, %s): %s" % (other_id, doi, eprint, recid, reportnumbers, err), stream=sys.stderr)
                continue
            if result:
                print >> output_file, result
                i += 1
                if i % 1000 == 0:
                    output_file.close()
                    task_low_level_submission('bibupload', 'bst_inspire_cds_synchro', '-a', output_file.name, '-n')
                    write_message("Scheduled bibupload --append %s" % output_file.name)
                    task_sleep_now_if_required()
                    output_file = get_out_file()
                    i = 0
    if i > 0:
        output_file.close()
        task_low_level_submission('bibupload', 'bst_inspire_cds_synchro', '-a', output_file.name, '-n')
        write_message("Scheduled bibupload --append %s" % output_file.name)

def bst_inspire_cds_synchro():
    task_update_progress("Phase 1: extracting IDs for %s" % CFG_OTHER_SITE)
    export_file = open(CFG_EXPORT_FILE + '.part', "w")
    for i, row in enumerate(iter_export_rows()):
        print >> export_file, row
        if i % 100 == 0:
            task_sleep_now_if_required(can_stop_too=True)
    export_file.close()
    shutil.move(CFG_EXPORT_FILE + '.part', CFG_EXPORT_FILE)
    task_sleep_now_if_required(can_stop_too=True)
    if os.path.exists(CFG_IMPORT_FILE):
        task_update_progress("Phase 2: importing IDs from %s" % CFG_OTHER_SITE)
        import_recid_list(open(CFG_IMPORT_FILE))

def main():
    open()
    for row in iter_export_rows():
        print row


if __name__ == '__main__':
    main()
