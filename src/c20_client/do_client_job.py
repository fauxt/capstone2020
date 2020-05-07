import time
import requests

from c20_client.client_logger import LOGGER

from c20_client.connection_error import NoConnectionError
from c20_client.do_wait import get_wait_time
from c20_client.client_decide_call import handle_specific_job
from c20_client import reggov_api_doc_error
from c20_client import connection_error


def do_job(api_key):
    """
    Gets a job from the server and handles the job based on the type of job
    """
    try:
        LOGGER.info('Getting job from server...')
        job = requests.get('http://capstone.cs.moravian.edu:5000/get_job')
        job = job.json()
        LOGGER.info("Job has been acquired")

    except Exception:
        LOGGER.error("A connection error has occurred")
        raise NoConnectionError

    results = handle_specific_job(job, api_key)

    if results is None:
        return

    post_job(results, job['job_type'])


def do_multiple_job(api_key):
    """
       Gets multiple job from the server
       and handles the job based on the type of job
    """
    try:
        print("Getting job...\n")
        while True:
            do_job(api_key)
            time.sleep(get_wait_time())

    except Exception:
        raise NoConnectionError


def post_job(results, job_type):
    LOGGER.info("Packaging successful!")
    LOGGER.info("Posting job to server")
    if job_type == 'download':
        file = {'file': (results['data'][0]['file_name'],
                         results['data'][0]['data'])
                }
        data = {
            'client_id': results['client_id'],
            'job_id': results['job_id'],
            'file_name': results['data'][0]['file_name'],
            'folder_name': results['data'][0]['folder_name']
        }
        # file = [('document', (results['data'][0]['file_name'],
        #                      results['data'][0]['data'],
        #                     results['data'][0]['folder_name']))]
        requests.post('http://capstone.cs.moravian.edu:5000/return_file',
                      files=file, data=data)
    else:
        requests.post('http://capstone.cs.moravian.edu:5000/return_result',
                      json=results)
    LOGGER.info("Job has successfully been posted!")


def handling_erorr(url, message_report=None):
    message_report = []
    result = requests.get(url)
    if result.status_code == 400:
        message_report.append(url + ":received 400:Bad Requests")
        raise reggov_api_doc_error.IncorrectIDPatternException
    if result.status_code == 403:
        message_report.append(url + ":received 403:Forbidden")
        raise reggov_api_doc_error.IncorrectApiKeyException
    if result.status_code == 404:
        message_report.append(url + ":received 404:Not Found")
        raise reggov_api_doc_error.BadDocIDException
    if result.status_code == 429:
        message_report.append(url + ":received 404:Too Many Requests")
        raise reggov_api_doc_error.ExceedCallLimitException
    if result.status_code == 503:
        message_report.append(url + "received 503:Service Unavailable Error")
        raise connection_error.ServiceUnavailableError
    return result
