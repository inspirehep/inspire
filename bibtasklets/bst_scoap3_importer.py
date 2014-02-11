import urllib
from os import fdopen
from os.path import join
from tempfile import mkstemp
from invenio.errorlib import register_exception
from invenio.search_engine import perform_request_search
from invenio.bibdocfile import BibRecDocs
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibtask import task_low_level_submission

def bst_scoap3_importer():
    f = urllib.urlopen('http://repo.scoap3.org/ffts_for_inspire.py/csv')

    fd1, name1 = mkstemp(suffix='.xml', prefix='bibupload_scoap3_', dir=CFG_TMPSHAREDDIR)
    out_update = fdopen(fd1, 'w')
    fd2, name2 = mkstemp(suffix='.xml', prefix='bibupload_scoap3_', dir=CFG_TMPSHAREDDIR)
    out_new = fdopen(fd2, 'w')
    print >> out_update, "<collection>"
    print >> out_new, "<collection>"

    line_count_new = 0  # to avoid empty bibupload
    line_count_update = 0  # to avoid empty bibupload
    for d in f:
        d = [x.strip() for x in d.split(',')]
        print d
        if d[0] not in ["recid", ''] and d[4] != "no pdf":
            inspire_record = perform_request_search(p="037:%s" % (d[1],), cc="HEP")
            try:
                if not len(inspire_record):
                    raise IndexError
                elif len(inspire_record) > 1:
                    raise IndexError
                else:
                    action = 0  # do nothing
                    rec = {}
                    record = BibRecDocs(inspire_record[0])
                    for doc in record.list_latest_files():
                        if doc.format in ('.pdf', '.pdf;pdfa'):
                            if doc.bibdoc.doctype is 'SCOAP3':
                                if doc.checksum is d[3]:
                                    print "File alredy attached"
                                else:
                                    action = 1  # update
                            else:
                                action = 2  # new

                    if action:
                        if d[5] == '.pdf;pdfa':
                            record_add_field(rec, 'FFT', subfields=[('a', d[4]), ('n', 'scoap3-fulltext'), ('f', '.pdf;pdfa'), ('t', 'SCOAP3'), ('d', 'Article from SCOAP3')])
                        else:
                            record_add_field(rec, 'FFT', subfields=[('a', d[4]), ('n', 'scoap3-fulltext'), ('t', 'SCOAP3'), ('d', 'Article from SCOAP3')])

                        record_add_field(rec, '001', controlfield_value=inspire_record[0])
                    if action == 1:
                        line_count_update = line_count_update + 1
                        print >> out_update, record_xml_output(rec)
                    elif action == 2:
                        line_count_new = line_count_new + 1
                        print >> out_new, record_xml_output(rec)
            except IndexError:
                register_exception(alert_admin=True, prefix="ERROR - PDF import from SCOAP3. No record with: %s" % (d[1],))
                continue
            except:
                register_exception(alert_admin=True, prefix="ERROR - PDF import from SCOAP3.")
                continue

    print >> out_update, "</collection>"
    print >> out_new, "</collection>"
    out_new.close()
    out_update.close()

    if line_count_new:
        task_low_level_submission("bibupload", "admin", "-N", "SCOAP3-import", "-a", name2)
    if line_count_update:
        task_low_level_submission("bibupload", "admin", "-N", "SCOAP3-import", "-c", name1)
