import json
import pytest
from c20_server import job
from c20_server import job_translator
from c20_server import job_translator_errors
from c20_server.job import\
    DocumentsJob, DocumentJob, DocketJob, DownloadJob, NoneJob


def test_handle_job_empty_json():
    assert job_translator.handle_jobs({}) == {}


def test_throw_invalid_job_type_exception():
    json_example = {
        "job_type": "invalid",
        "job_id": "ab0ebb71-d669-4386-b6b3-9bc0c51d6513"
    }
    with pytest.raises(job_translator_errors.UnrecognizedJobTypeException):
        job_translator.json_to_job(json_example)


def test_documents_job_to_json():
    job_example = DocumentsJob("d022c3f5-6d69-4cbe-9330-b2a5cc8e6ff5",
                               "1000",
                               "2005-08-04T00:00:00-04:00",
                               "2005-10-03T23:59:59-04:00")

    job_json = job_translator.job_to_json(job_example)

    job_json_expected = {"job_id": "d022c3f5-6d69-4cbe-9330-b2a5cc8e6ff5",
                         "page_offset": "1000",
                         "start_date": "2005-08-04T00:00:00-04:00",
                         "end_date": "2005-10-03T23:59:59-04:00",
                         "job_type": "documents"}
    job_json_expected = json.dumps(job_json_expected)
    assert job_json == job_json_expected


def test_document_job_to_json():
    job_example = DocumentJob("bfcadfea-db21-44aa-a234-9833291cbbc9",
                              "CMS-2005-0001-0001")

    job_json = job_translator.job_to_json(job_example)

    job_json_expected = {"job_id": "bfcadfea-db21-44aa-a234-9833291cbbc9",
                         "document_id": "CMS-2005-0001-0001",
                         "job_type": "document"}
    job_json_expected = json.dumps(job_json_expected)
    assert job_json == job_json_expected


def test_docket_job_to_json():
    job_example = DocketJob("172dc679-c2d7-4a84-b766-8cd5ee138057",
                            "CMS-2005-0001")

    job_json = job_translator.job_to_json(job_example)

    job_json_expected = {"job_id": "172dc679-c2d7-4a84-b766-8cd5ee138057",
                         "docket_id": "CMS-2005-0001",
                         "job_type": "docket"}
    job_json_expected = json.dumps(job_json_expected)
    assert job_json == job_json_expected


def test_download_job_to_json():
    url = "https://api.data.gov/regulations/v3/download \
           ?documentId=CMS-2005-0001-0001&contentType=pdf"
    job_example = \
        DownloadJob("2aae0fca-bf7d-4444-ab9b-0120414aa0b5",
                    "CMS/CMS-2005/",
                    "title_of_file",
                    "pdf",
                    url)

    job_json = job_translator.job_to_json(job_example)

    job_json_expected = \
        {"job_id": "2aae0fca-bf7d-4444-ab9b-0120414aa0b5",
         "folder_name": "CMS/CMS-2005/",
         "file_name": "title_of_file",
         "file_type": "pdf",
         "url": url,
         "job_type": "download"}
    job_json_expected = json.dumps(job_json_expected)
    assert job_json == job_json_expected


def test_none_job_to_json():
    job_example = NoneJob("2aae0fca-bf7d-4444-ab9b-0120414aa0b5")

    job_json = job_translator.job_to_json(job_example)
    job_json_expected = \
        {"job_id": "2aae0fca-bf7d-4444-ab9b-0120414aa0b5",
         "job_type": "none"}
    job_json_expected = json.dumps(job_json_expected)
    assert job_json == job_json_expected


def test_single_documents_json_to_job():
    json_example = {
        "job_type": "documents",
        "page_offset": "2000",
        "start_date": "2017-11-09T00:00:00-05:00",
        "end_date": "2017-11-29T23:59:59-05:00"
    }
    test_job = job_translator.json_to_job(json_example)
    documents_job = job.DocumentsJob(test_job[0],
                                     "2000",
                                     "2017-11-09T00:00:00-05:00",
                                     "2017-11-29T23:59:59-05:00")
    assert test_job == documents_job


def test_single_document_json_to_job():
    json_example = {
        "job_type": "document",
        "document_id": "FAA-2012-1137-0017"
    }
    test_job = job_translator.json_to_job(json_example)
    document_job = job.DocumentJob(test_job[0],
                                   "FAA-2012-1137-0017")
    assert test_job == document_job


def test_single_docket_json_to_job():
    json_example = {
        "job_type": "docket",
        "docket_id": "FAA-2012-1137"
    }
    test_job = job_translator.json_to_job(json_example)
    docket_job = job.DocketJob(test_job[0],
                               "FAA-2012-1137")
    assert test_job == docket_job


def test_single_download_json_to_job():
    url = "https://api.data.gov/regulations/v3/download \
           ?documentId=CMS-2005-0001-0001&contentType=pdf"
    json_example = \
        {
            "job_type": "download",
            "folder_name": "CMS/CMS-2005/",
            "file_name": "title_of_file",
            "file_type": "pdf",
            "url": url
        }
    test_job = job_translator.json_to_job(json_example)
    download_job = \
        job.DownloadJob(test_job[0],
                        "CMS/CMS-2005/",
                        "title_of_file",
                        "pdf",
                        url)
    assert test_job == download_job


def test_handle_single_job():
    json_result_sample = \
        {
            "Data": [
                {
                    "folder_name": "CMS/CMS-2005-0001/CMS-2005-0001-0001/",
                    "file_name": "basic_document.json",
                    "contents": {}
                }
            ],
            "jobs": [
                {
                    "job_type": "documents",
                    "job_id": "c08d740a-6fde-47d9-a0f1-addfba271342",
                    "page_offset": "3000",
                    "start_date": "2005-08-04T00:00:00-04:00",
                    "end_date": "2005-10-03T23:59:59-04:00"
                },
            ]
        }
    json_result_sample = json.dumps(json_result_sample)

    test_job = job_translator.handle_jobs(json_result_sample)

    job_list = [
        job.DocumentsJob(
            job_id=test_job[0][0],
            page_offset="3000",
            start_date="2005-08-04T00:00:00-04:00",
            end_date="2005-10-03T23:59:59-04:00")
    ]
    assert test_job == job_list


def test_handle_documents_return_data():
    json_documents_return_data = \
        {
            "Data": [
                {
                    "folder_name": "CMS/CMS-2005-0001/CMS-2005-0001-0001/",
                    "file_name": "basic_document.json",
                    "contents": {}
                }
            ],
            "jobs": [
                {
                    "job_type": "document",
                    "document_id": "CMS-2005-0001-0001"
                },
                {
                    "job_type": "docket",
                    "docket_id": "CMS-2005-0001"
                },
                {
                    "job_type": "document",
                    "document_id": "FAA-2012-1137-0017"
                },
                {
                    "job_type": "docket",
                    "docket_id": "FAA-2012-1137"
                }
            ]
        }
    json_documents_return_data = json.dumps(json_documents_return_data)

    test_job = job_translator.handle_jobs(json_documents_return_data)

    job_list = [
        job.DocumentJob(
            job_id=test_job[0][0],
            document_id="CMS-2005-0001-0001"),
        job.DocketJob(
            job_id=test_job[1][0],
            docket_id="CMS-2005-0001"),
        job.DocumentJob(
            job_id=test_job[2][0],
            document_id="FAA-2012-1137-0017"),
        job.DocketJob(
            job_id=test_job[3][0],
            docket_id="FAA-2012-1137")
    ]

    assert test_job == job_list


def test_handle_document_return_data():
    url1 = "https://api.data.gov/regulations/v3/download \
            ?documentId=CMS-2005-0001-0001&contentType=pdf"
    url2 = "https://api.data.gov/regulations/v3/download \
            ?documentId=CMS-2005-0001-0001&contentType=pdf"
    url3 = "https://api.data.gov/regulations/v3/download \
            ?documentId=CMS-2005-0001-0001&contentType=pdf"
    json_document_return_data = \
        {
            "Data": [
                {
                    "folder_name": "CMS/CMS-2005-0001/CMS-2005-0001-0001/",
                    "file_name": "basic_document.json",
                    "contents": {}
                }
            ],
            "jobs": [
                {
                    "job_type": "download",
                    "folder_name": "CMS/CMS-2005/",
                    "file_name": "CMS_file",
                    "file_type": "pdf",
                    "url": url1
                },
                {
                    "job_type": "download",
                    "folder_name": "DMS/DMS-2050/",
                    "file_name": "DMS_file",
                    "file_type": "html",
                    "url": url2
                },
                {
                    "job_type": "download",
                    "folder_name": "LAO/LAO-1450/",
                    "file_name": "LAO_file",
                    "file_type": "excel",
                    "url": url3
                },

            ]
        }
    json_document_return_data = json.dumps(json_document_return_data)

    test_job = job_translator.handle_jobs(json_document_return_data)

    job_list = [
        job.DownloadJob(
            job_id=test_job[0][0],
            folder_name="CMS/CMS-2005/",
            file_name="CMS_file",
            file_type="pdf",
            url=url1),
        job.DownloadJob(
            job_id=test_job[1][0],
            folder_name="DMS/DMS-2050/",
            file_name="DMS_file",
            file_type="html",
            url=url2),
        job.DownloadJob(
            job_id=test_job[2][0],
            folder_name="LAO/LAO-1450/",
            file_name="LAO_file",
            file_type="excel",
            url=url3)
    ]
    assert test_job == job_list


def test_json_data_key_error():
    """
    KeyError exception is thrown when there is no jobs field
    supplied in the json return result value from the client.
    """
    json_return_data = \
        {
            "Data": [
                {
                    "folder_name": "CMS/CMS-2005-0001/CMS-2005-0001-0001/",
                    "file_name": "basic_document.json",
                    "contents": {}
                }
            ]
        }

    json_return_data = json.dumps(json_return_data)
    handled_job = job_translator.handle_jobs(json_return_data)

    assert handled_job == {}
