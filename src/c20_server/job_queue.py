
"""
implementation of Job_Queue class

"""
import pickle
import threading
from c20_server import job_queue_errors
from c20_server.server_logger import LOGGER


class JobQueue:

    def __init__(self, database):
        self.r_database = database
        self.lock = threading.RLock

    def add_job(self, job_object):
        # with self.lock:
        job_ = pickle.dumps(job_object)
        self.r_database.rpush('unassigned_jobs', job_)

    def get_job(self):
        # with self.lock:
        job_from_queue = self.r_database.lpop('unassigned_jobs')
        if not job_from_queue:
            LOGGER.error('No Job available to be done')
            raise job_queue_errors.NoJobsAvailableException
        job = pickle.loads(job_from_queue)
        return job  # job_from_queue

    def get_num_unassigned_jobs(self):
        return self.r_database.llen('unassigned_jobs')
