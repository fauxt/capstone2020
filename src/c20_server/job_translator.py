import json
import uuid
from collections import namedtuple
from c20_server import job_translator_errors
from c20_server.job import\
    DocumentsJob, DocumentJob, DocketJob, DownloadJob, NoneJob
from c20_server.server_logger import LOGGER

DOCUMENTS = "documents"
DOCUMENT = "document"
DOCKET = "docket"
DOWNLOAD = "download"
NONE_JOB = "none"


def job_to_json(job_object):
    job_type = ""

    if isinstance(job_object, DocumentsJob):
        job_type = DOCUMENTS
    elif isinstance(job_object, DocumentJob):
        job_type = DOCUMENT
    elif isinstance(job_object, DocketJob):
        job_type = DOCKET
    elif isinstance(job_object, DownloadJob):
        job_type = DOWNLOAD
    elif isinstance(job_object, NoneJob):
        job_type = NONE_JOB
    return encode_job(job_type, job_object)


def encode_job(job_type, job_object):
    json_data = job_object._asdict()
    json_data["job_type"] = job_type
    json_job = json.dumps(json_data)
    return json_job


def handle_jobs(json_data):
    """
    handle_jobs will take the return result json from client and split it up
    into multiple json objects that get sent to json_to_job
    """

    job_list = []

    try:
        json_data = json.loads(json_data)
    except TypeError:
        LOGGER.error('Received wrong data format')
        return {}

    json_jobs = json_data["jobs"]

    for job in json_jobs:
        job = json_to_job(job)
        job_list.append(job)
    return job_list


def json_to_job(json_job):
    job_id = str(uuid.uuid4())
    json_job["job_id"] = job_id
    job_type = json_job["job_type"]
    Record = namedtuple('Record', 'job_id job_type')
    input_array_line = [job_id, job_type]
    record = Record(*input_array_line)

    return add_specific_job_data(record, json_job)


def add_specific_job_data(record, json_job):
    if record.job_type == DOCUMENTS:
        return create_documents_job(record, json_job)

    if record.job_type == DOCUMENT:
        return create_document_job(record, json_job)

    if record.job_type == DOCKET:
        return create_docket_job(record, json_job)

    if record.job_type == DOWNLOAD:
        return create_download_job(record, json_job)
    LOGGER.error('Attempted to Add an unrecognized Job type to the JobQueue')
    raise job_translator_errors.UnrecognizedJobTypeException


def create_documents_job(record, json_job):
    page_offset = json_job["page_offset"]
    start_date = json_job["start_date"]
    end_date = json_job["end_date"]
    return DocumentsJob(record.job_id, page_offset, start_date, end_date)


def create_document_job(record, json_job):
    document_id = json_job["document_id"]
    return DocumentJob(record.job_id, document_id)


def create_docket_job(record, json_job):
    docket_id = json_job["docket_id"]
    return DocketJob(record.job_id, docket_id)


def create_download_job(record, json_job):
    folder_name = json_job["folder_name"]
    file_name = json_job["file_name"]
    file_type = json_job["file_type"]
    url = json_job["url"]
    return DownloadJob(record.job_id, folder_name, file_name, file_type, url)


def create_none_job(record):
    return NoneJob(record.job_id)
