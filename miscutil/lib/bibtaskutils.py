import os
import time

from tempfile import mkstemp

from invenio.dbquery import run_sql
from invenio.config import CFG_TMPSHAREDDIR
from invenio.bibtask import task_low_level_submission


def all_recids(start=1):
    max_id = run_sql("SELECT max(id) FROM bibrec")[0][0]
    return xrange(start, max_id + 1)


def loop(recids, callback):
    for done, recid in enumerate(recids):
        callback(recid)
        if done % 50 == 0:
            print 'done %s of %s' % (done + 1, len(recids))


def wait_for_task(task_id):
    sql = 'select status from schTASK where id = %s'
    while run_sql(sql, [task_id])[0][0] not in ('DONE', 'ACK', 'ACK DONE'):
        time.sleep(5)


def submit_bibupload_task(to_submit, mode, user, priority=3, notimechange=False):
    # Save new record to file
    (temp_fd, temp_path) = mkstemp(prefix=user,
                                   dir=CFG_TMPSHAREDDIR)
    temp_file = os.fdopen(temp_fd, 'w')
    temp_file.write('<?xml version="1.0" encoding="UTF-8"?>')
    temp_file.write('<collection>')
    for el in to_submit:
        temp_file.write(el)
    temp_file.write('</collection>')
    temp_file.close()

    args = ['bibupload', user,
            '-P', str(priority), '-%s' % mode,
            temp_path]
    if notimechange:
        args += ['--notimechange']

    return task_low_level_submission(*args)


def submit_bibindex_task(to_update, indexes, user, priority=3):
    recids = [str(r) for r in to_update]
    return task_low_level_submission('bibindex', user,
                                     '-w', indexes,
                                     '-P', str(priority),
                                     '-i', ','.join(recids))


def submit_bibrank_task(to_update, methods, user, priority=3):
    recids = [str(r) for r in to_update]
    return task_low_level_submission('bibrank', user,
                                     '-w', methods,
                                     '-P', str(priority),
                                     '-i', ','.join(recids))


def submit_refextract_task(to_update, user, priority=3):
    recids = [str(r) for r in to_update]
    return task_low_level_submission('refextract', user,
                                     '-P', str(priority),
                                     '--recids', ','.join(recids))


class ChunkedTask(object):
    """Groups elements in chunks before submitting them to bibsched"""
    chunk_size = 500
    submitter = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.to_submit = []

    def submit_task(self, to_submit):
        if self.submitter is None:
            raise Exception('Task submitter not defined')
        task_id = self.submitter(to_submit, *self.args, **self.kwargs)
        wait_for_task(task_id)

    def add(self, el):
        self.to_submit.append(el)
        if len(self.to_submit) == self.chunk_size:
            to_submit = self.to_submit
            self.to_submit = []
            self.submit_task(to_submit)

    def cleanup(self):
        if self.to_submit:
            to_submit = self.to_submit
            self.to_submit = []
            self.submit_task(to_submit)

    def __del__(self):
        self.cleanup()


class ChunkedBibUpload(ChunkedTask):
    submitter = staticmethod(submit_bibupload_task)


class ChunkedBibIndex(ChunkedTask):
    submitter = staticmethod(submit_bibindex_task)


class ChunkedBibRank(ChunkedTask):
    submitter = staticmethod(submit_bibrank_task)


class ChunkedRefextract(ChunkedTask):
    submitter = staticmethod(submit_refextract_task)
