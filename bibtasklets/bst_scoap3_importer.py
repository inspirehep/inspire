import urllib
import sys
from os import fdopen, remove
from os.path import join
from tempfile import mkstemp
from invenio.errorlib import register_exception
from invenio.search_engine import perform_request_search
from invenio.bibdocfile import BibRecDocs
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibtask import task_low_level_submission, write_message, task_sleep_now_if_required

def bst_scoap3_importer():
    task_sleep_now_if_required(can_stop_too=True)
    f = urllib.urlopen('http://repo.scoap3.org/ffts_for_inspire.py/csv')

    fd_update, name_update = mkstemp(suffix='.xml', prefix='bibupload_scoap3_', dir=CFG_TMPSHAREDDIR)
    out_update = fdopen(fd_update, 'w')
    fd_new, name_new = mkstemp(suffix='.xml', prefix='bibupload_scoap3_', dir=CFG_TMPSHAREDDIR)
    out_new = fdopen(fd_new, 'w')
    print >> out_update, "<collection>"
    print >> out_new, "<collection>"

    line_count_new = 0  # to avoid empty bibupload
    line_count_update = 0  # to avoid empty bibupload
    f.readline() ## Let's strip the header line

    for d in f:
        task_sleep_now_if_required(can_stop_too=True)
        recid, arxiv_id, cr_date, checksum, link, type, doi = [x.strip() for x in d.split(',')]
        write_message(d.strip())
        if checksum == "None":
            write_message("... no PDF. Skipping")
            continue
        if arxiv_id == "None":
            inspire_record = perform_request_search(p="doi:%s" % (doi, ), cc="HEP")
        else:
            inspire_record = perform_request_search(p="037:%s or doi:%s" % (arxiv_id, doi), cc="HEP")
        if len(inspire_record) > 1:
            write_message("ERROR: more than one INSPIRE record matched %s and %s for SCOAP3 record %s: %s" % (arxiv_id, doi, recid, list(inspire_record)), stream=sys.stderr)
            continue
        elif not inspire_record:
            write_message("WARNING: no INSPIRE record matched %s or %s for SCOAP3 record %s" % (arxiv_id, doi, recid), stream=sys.stderr)
            continue
        action = None  # do nothing
        rec = {}
        inspire_record = inspire_record[0]
        record = BibRecDocs(inspire_record)
        for doc in record.list_latest_files():
            if doc.format in ('.pdf', '.pdf;pdfa'):
                if doc.bibdoc.doctype == 'SCOAP3':
                    if doc.checksum == checksum:
                        write_message("... OK: file alredy attached to INSPIRE record %s (doc.checksum=%s, checksum=%s)" % (inspire_record, doc.checksum, checksum))
                    else:
                        write_message("... OK: new revision available for INSPIRE record %s (doc.checksum=%s, checksum=%s)" % (inspire_record, doc.checksum, checksum))
                        action = "UPDATE"
                    break
        else:
            write_message("... OK: need to add new file to INSPIRE record %s" % inspire_record)
            action = "APPEND"
        if action:
            if type == '.pdf;pdfa':
                record_add_field(rec, 'FFT', subfields=[('a', link), ('n', 'scoap3-fulltext'), ('f', '.pdf;pdfa'), ('t', 'SCOAP3'), ('d', 'Article from SCOAP3')])
            else:
                record_add_field(rec, 'FFT', subfields=[('a', link), ('n', 'scoap3-fulltext'), ('t', 'SCOAP3'), ('d', 'Article from SCOAP3')])

            record_add_field(rec, '001', controlfield_value=str(inspire_record))
        if action == "UPDATE":
            line_count_update += 1
            print >> out_update, record_xml_output(rec)
        elif action == "APPEND":
            line_count_new += 1
            print >> out_new, record_xml_output(rec)
    print >> out_update, "</collection>"
    print >> out_new, "</collection>"
    out_new.close()
    out_update.close()

    if line_count_new:
        id = task_low_level_submission("bibupload", "admin", "-N", "SCOAP3-import", "-a", name_new)
        write_message("Scheduled bibupload --append %s with ID #%s" % (name_new, id))
    else:
        remove(name_new)
    if line_count_update:
        id = task_low_level_submission("bibupload", "admin", "-N", "SCOAP3-import", "-c", name_update)
        write_message("Scheduled bibupload --correct %s with ID #%s" % (name_new, id))
    else:
        remove(name_update)
