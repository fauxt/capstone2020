"""
Gets a job from the server and handles the job based on the type of job
"""
import argparse
import requests
from c20_client.connection_error import NoConnectionError

from c20_client.client_decide_call import handle_specific_job

from c20_client.client_logger import LOGGER


def do_job(api_key):
    """
    Gets a job from the server and handles the job based on the type of job
    """
    try:
        LOGGER.info('Getting job from server...')
        job = requests.get('http://capstone.cs.moravian.edu/get_job')
        job = job.json()
        LOGGER.info("Job aquired")

    except Exception:
        raise NoConnectionError

    results = handle_specific_job(job, api_key)

    if results is None:
        return

    LOGGER.info("Packaging Successful")
    LOGGER.info("Posting data to server")
    if job['job_type'] == 'download':
        file = {'file': (results['data'][0]['file_name'], results['data'][0]['data']) }
        data = {
            'client_id': results['client_id'],
            'job_id': results['job_id'],
            'file_name': results['data'][0]['file_name'],
            'folder_name': results['data'][0]['folder_name']
        }
        #file = [('document', (results['data'][0]['file_name'],
        #                      results['data'][0]['data'],
        #                     results['data'][0]['folder_name']))]
        requests.post('http://capstone.cs.moravian.edu/return_file',
                      files=file, data=data)
    else:
        requests.post('http://capstone.cs.moravian.edu/return_result',
                      json=results)
    LOGGER.info("Data successfully posted to server!")


def main():
    parser = argparse.ArgumentParser(
        description="get files from regulations.gov")
    parser.add_argument("API_key", help="api key for regulations.gov")
    args = parser.parse_args()
    do_job(args.API_key)


if __name__ == '__main__':
    main()
