from c20_client.get_documents import get_documents
from c20_client.get_document import download_document
from c20_client.retrieve_docket import get_docket
from c20_client.get_download import download_file
from c20_client.download_packager import package_downloads

from c20_client.documents_packager import package_documents
from c20_client.docket_packager import package_docket
from c20_client.document_packager import package_document

from c20_client.client_logger import LOGGER

CLIENT_ID = '1'


def handle_specific_job(job, api_key):
    """
    Makes request to correct endpoint at reg.gov
    """
    job_id = job['job_id']
    job_type = job['job_type']

    if job_type == 'documents':
        results = find_documents_data(api_key, job, job_id)

    elif job_type == 'document':
        results = find_document_data(api_key, job, job_id)

    elif job_type == 'docket':
        results = find_docket_data(api_key, job, job_id)

    elif job_type == 'download':
        results = find_download_data(api_key, job, job_id)

    elif job_type == 'none':
        return None

    return results


def find_documents_data(api_key, job, job_id):
    print("Getting documents from regulations.gov...\n")
    data = get_documents(
        api_key,
        job["page_offset"],
        job["start_date"],
        job["end_date"])
    LOGGER.info("Job#%s: Packaging documents...", str(job_id))
    results = package_documents(data, CLIENT_ID, job_id)
    return results


def find_document_data(api_key, job, job_id):
    print("Getting document from regulations.gov...\n")
    data = download_document(
        api_key,
        job['document_id']
    )
    LOGGER.info("Job#%s: Packaging document...", str(job_id))
    results = package_document(data, CLIENT_ID, job_id)
    return results


def find_docket_data(api_key, job, job_id):
    print("Getting docket from regulations.gov...\n")
    data = get_docket(
        api_key,
        job['docket_id']
    )
    LOGGER.info("Job#%s: Packaging docket..", str(job_id))
    results = package_docket(data, CLIENT_ID, job_id)
    return results


def find_download_data(api_key, job, job_id):
    print("Getting download from regulations.gov...\n")
    data = download_file(
        api_key,
        job['url']
    )
    data_json = {'folder_name': job['folder_name'],
                 'file_name': job['file_name'],
                 'file_type': job['file_type'],
                 'data': data.text
                 }
    LOGGER.info("Job#%s: Packaging downloads..", str(job_id))
    results = package_downloads(data_json, CLIENT_ID, job_id)
    return results
