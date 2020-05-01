import pickle
from c20_server.job_queue import JobQueue
from c20_server.in_progress import InProgress
from c20_server.job import NoneJob
from c20_server.server_logger import LOGGER


class JobManager:

    def __init__(self, database):
        self.r_database = database
        self.job_queue = JobQueue(self.r_database)
        self.in_progress_jobs = InProgress(self.r_database)

    def add_job(self, job):
        LOGGER.info('Adding new Job to JobQueue')
        self.job_queue.add_job(job)

    def request_job(self, user):
        if self.num_unassigned() == 0:
            LOGGER.error('No Job available to be done')
            return NoneJob(-1)
        job = self.job_queue.get_job()
        LOGGER.info('Job #%s is assigned with user #%s',
                    job.job_id, str(user.user_id))
        self.in_progress_jobs.assign(job, user.user_id)
        return job

    def report_success(self, user):
        LOGGER.info('Job is successfully done by user # %s', str(user.user_id))
        self.in_progress_jobs.unassign(user.user_id)

    def report_failure(self, user):
        LOGGER.info('User # %s failed to complete the job', str(user.user_id))
        job = self.in_progress_jobs.unassign(user.user_id)
        LOGGER.info('Sending the job #%s back to JobQueue', str(job.job_id))
        self.job_queue.add_job(job)

    def reset_stale_job(self, time_to_expire):
        for user in self.in_progress_jobs.get_all_assigned_jobs():
            job_info = self.r_database.hget('assigned_jobs', user)
            time_, job = pickle.loads(job_info)
            if time_ < time_to_expire:
                LOGGER.info('User #%s failed to complete the job'
                            ' in the given time', user)
                job = self.in_progress_jobs.unassign(user)
                LOGGER.info('Sending the stale job #%s back to JobQueue',
                            str(job.job_id))
                self.job_queue.add_job(job)

    def num_assigned(self):
        return self.in_progress_jobs.get_num_assigned_jobs()

    def num_unassigned(self):
        return self.job_queue.get_num_unassigned_jobs()
