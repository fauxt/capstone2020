"""
Gets a job from the server and handles the job based on the type of job
"""
import requests
from c20_client.connection_error import NoConnectionError

from c20_client.client_decide_call import handle_specific_job
from c20_client.get_client_id import ClientManager

from c20_client.client_logger import LOGGER


def post_job(results):
    LOGGER.info("Packaging successful!")
    LOGGER.info("Posting job to server")
    requests.post('http://capstone.cs.moravian.edu/return_result',
                  json=results)
    LOGGER.info("Job has successfully been posted!")


def do_job(manager):
    """
    Gets a job from the server and handles the job based on the type of job
    """
    try:
        LOGGER.info('Getting job from server...')
        job = requests.get('http://capstone.cs.moravian.edu/get_job')
        job = job.json()
        LOGGER.info("Job has been aquired")

    except Exception:
        LOGGER.error("A connection error has occurred")
        raise NoConnectionError

    results = handle_specific_job(job, manager)

    if results is None:
        return

    post_job(results)


def main():
    """
    Run the program
    """
    manager = ClientManager()
    do_job(manager)


if __name__ == '__main__':
    main()
