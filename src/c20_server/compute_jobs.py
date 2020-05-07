'''
Compute Jobs from regulations.api
'''
import requests
from c20_client import reggov_api_doc_error
from c20_server.job import DocumentsJob
from c20_server.server_logger import LOGGER
URL = "https://api.data.gov:443/regulations/v3/documents.json?api_key="


def get_number_of_docs(response):
    '''
    Return total number of records
    '''
    number_of_docs = response.get("totalNumRecords")
    return number_of_docs


def get_response_from_api(api_key, start_date, end_date):

    crd = start_date + "-" + end_date

    LOGGER.info('Requesting documents from regulations.gov')
    response = requests.get(URL+api_key+"&crd="+crd)

    if response.status_code == 403:
        LOGGER.error('The given API key is incorrect')
        raise reggov_api_doc_error.IncorrectApiKeyException
    if response.status_code == 429:
        LOGGER.error('The 1000 call an hour limit has been exceeded')
        raise reggov_api_doc_error.ExceedCallLimitException
    LOGGER.info('documents has been retrieved')
    return response.json()


def compute_jobs(api_key, start_date, end_date):
    '''
    Computing Jobs for Documents endpoint
    '''

    response = get_response_from_api(api_key, start_date, end_date)

    number_of_docs = get_number_of_docs(response)

    jobs = []

    for page_offset in range(0, number_of_docs, 1000):
        job_id = "DocsJob" + str(page_offset)
        jobs.append(DocumentsJob(job_id, page_offset, start_date, end_date))

    return jobs
