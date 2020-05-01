"""
Implementation of In-Progress class
"""
import pickle
import time
from c20_server import job_queue_errors
from c20_server.server_logger import LOGGER


class InProgress:

    def __init__(self, database):
        self.r_database = database

    def assign(self, job, user_id):
        job = pickle.dumps((self.get_current_time(), job))
        self.r_database.hset('assigned_jobs', user_id, job)

    def unassign(self, user_id):
        if not self.r_database.hexists('assigned_jobs', user_id):
            LOGGER.error('The user#%s is invalid', user_id)
            raise job_queue_errors.UnassignInvalidDataException
        job = self.r_database.hget('assigned_jobs', user_id)
        self.r_database.hdel('assigned_jobs', user_id)
        job = pickle.loads(job)
        return job[1]  # (time_when_assigned, job)

    def get_num_assigned_jobs(self):
        return self.r_database.hlen('assigned_jobs')

    def get_all_assigned_jobs(self):
        return self.r_database.hgetall('assigned_jobs')

    @staticmethod
    def get_current_time():
        """
        Gets the current time.
        """
        return float(time.time())
