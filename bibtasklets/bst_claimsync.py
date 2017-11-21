from time import strftime

import sys, os
import redis
import json

from invenio.config import CFG_REDIS_HOST_LABS, CFG_TMPSHAREDDIR
from invenio.bibformat_elements.bfe_INSPIRE_enhanced_marcxml import get_hepname_id, get_personid_canonical_id
from invenio.bibtask import write_message
from invenio.dbquery import run_sql

LASTRUN_PATH = os.path.join(CFG_TMPSHAREDDIR, 'claimsync_lastrun.txt')
REDIS_KEY = 'legacy_claims'

def get_lastrun():
    try:
        with open(LASTRUN_PATH) as input:
            return input.read().strip()
    except IOError:
        return '1970-01-01 00:00:00'


def set_lastrun(now):
    with open(LASTRUN_PATH, "w") as output:
        output.write(now)


def bst_claimsync():
    """
    Append to a the redis key %s on %s all the claims generated
    since the last time.
    A claim is a tuple with the structure:
    (bai, hepname_id, bibrec, name, flag)

    Note: if the key is not empty (meaning that Labs hasn't finished
    to process all the claims yet, then no new claims will be added)

    Note2: in order to set the lastrun to a particular date edit
    the file CFG_TMPSHAREDDIR/claimsync_lastrun.txt.
    """
    from invenio.bibsched_tasklets.bst_prodsync import run_ro_on_slave_db
    r = redis.StrictRedis.from_url(CFG_REDIS_HOST_LABS)
    if r.llen(REDIS_KEY) != 0:
        write_message("Skipping prodsync: Redis queue is not yet empty")
        return
    now = strftime('%Y-%m-%d %H:%M:%S')
    lastrun = get_lastrun()
    write_message("Syncing claims modified since %s" % lastrun)
    with run_ro_on_slave_db():
        claims = run_sql("""SELECT personid, bibrec, name, flag
            FROM aidPERSONIDPAPERS
            WHERE (
                last_updated>=%s OR
                personid IN (
                    SELECT distinct personid
                    FROM aidPERSONIDDATA
                    WHERE last_updated>=DATE_SUB(%s, INTERVAL 2 DAY)
                )
            ) AND (flag=2 OR flag=-2)
        """, (lastrun, lastrun))
        write_message("Adding %s claims" % len(claims))
        for personid, bibrec, name, flag in claims:
            bai = get_personid_canonical_id().get(personid)
            if bai:
                hepname_id = get_hepname_id(personid)
                if hepname_id:
                    r.rpush(REDIS_KEY, json.dumps((bai, hepname_id, bibrec, name, flag)))
                else:
                    write_message("Skipping claim %s because no hepname_id corresponds to it" % ((bai, personid, bibrec, name, flag),), stream=sys.stderr)
            else:
                write_message("Skipping claim %s because no BAI corresponds to it" % ((personid, bibrec, name, flag),), stream=sys.stderr)
    set_lastrun(now)
    write_message("DONE!")
