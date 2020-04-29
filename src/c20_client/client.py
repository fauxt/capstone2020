"""
Gets a job from the server and handles the job based on the type of job
"""
import argparse
import requests
from c20_client.connection_error import NoConnectionError

from c20_client.client_decide_call import handle_specific_job

from c20_client.client_logger import LOGGER


def post_job(results):
    LOGGER.info("Packaging successful!")
    LOGGER.info("Posting job to server")
    requests.post('http://capstone.cs.moravian.edu:5000/return_result',
                  json=results)
    LOGGER.info("Job has successfully been posted!")


def do_job(api_key):
    """
    Gets a job from the server and handles the job based on the type of job
    """
    try:
        LOGGER.info('Getting job from server...')
        job = requests.get('http://capstone.cs.moravian.edu:5000/get_job')
        job = job.json()
        LOGGER.info("Job has been aquired")

    except Exception:
        LOGGER.error("A connection error has occurred")
        raise NoConnectionError

    results = handle_specific_job(job, api_key)

    if results is None:
        return

    post_job(results)


def main():
    parser = argparse.ArgumentParser(
        description="get files from regulations.gov")
    parser.add_argument("API_key", help="api key for regulations.gov")
    args = parser.parse_args()
    do_job(args.API_key)


if __name__ == '__main__':
    main()
