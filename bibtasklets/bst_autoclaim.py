from invenio.search_engine import perform_request_search, get_record
from invenio.bibauthorid_dbinterface import confirm_papers_to_author, get_all_signatures_of_paper
from invenio.bibrecord import record_get_field_instances, field_get_subfield_instances
from invenio.dbquery import run_sql
from invenio.bibtask import task_update_progress, task_sleep_now_if_required, write_message


def bst_autoclaim():
    orcid_personid_map = get_orcid_personid_map()
    papers = get_papers_with_orcid()
    for i, recid in enumerate(papers):
        autoclaim_paper(recid, orcid_personid_map)
        if i % 10 == 0:
            task_update_progress("Done %s out of %s records (%s%%)" % (i, len(papers), 100*(i)/len(papers)))
            task_sleep_now_if_required(can_stop_too=True)


def get_orcid_personid_map():
    return dict(run_sql("SELECT data, personid FROM aidPERSONIDDATA WHERE tag='extid:ORCID'"))


def get_papers_with_orcid():
    return perform_request_search(p='100__j:"ORCID:*" or 700__j:"ORCID:*"')


def autoclaim_paper(recid, orcid_personid_map):
    record = get_record(recid)
    signature_map = get_signature_map(recid)
    signatures_with_orcid = get_signatures_with_orcid(record)
    for author, orcid in signatures_with_orcid.iteritems():
        personid = orcid_personid_map.get(orcid)
        if personid:
            signature, current_personid, flag = signature_map.get(author, (None, None, None))
            if signature and (current_personid != personid or flag != 2):
                write_message("Claiming paper %s to author %s (%s) with personid %s" % (recid, author, orcid, personid))
                confirm_papers_to_author(personid, [signature])


def get_signature_map(recid):
    all_signatures = run_sql("SELECT personid, bibref_table, bibref_value, name, flag FROM aidPERSONIDPAPERS WHERE bibrec=%s", (recid, ))
    out = {}
    for personid, bibref_table, bibref_value, name, flag in all_signatures:
        # See: _split_signature_string()
        out[name] = ('{bibref_table}:{bibref_value},{rec}'.format(bibref_table=bibref_table, bibref_value=bibref_value, rec=recid), personid, flag)
    return out


def get_signatures_with_orcid(record):
    out = {}
    for field in record_get_field_instances(record, '100') + record_get_field_instances(record, '700'):
        subfields = dict(field_get_subfield_instances(field))
        if subfields.get('j', '').upper().startswith('ORCID:'):
            orcid = subfields['j'][len('ORCID:'):]
            author = subfields['a']
            out[author] = orcid
    return out
