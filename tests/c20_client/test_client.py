from os import getenv, environ
from unittest.mock import mock_open
import requests_mock
import pytest
from c20_client.do_client_job import do_job, handling_erorr
from c20_client.connection_error import NoConnectionError
from c20_client.get_client_id import ClientManager
from c20_client.connection_error import ServiceUnavailableError
from c20_client.reggov_api_doc_error import IncorrectApiKeyException
from c20_client.reggov_api_doc_error import IncorrectIDPatternException
from c20_client.reggov_api_doc_error import BadDocIDException
from c20_client.reggov_api_doc_error import ExceedCallLimitException

CLIENT_ID = '1'
JOB_ID = 1
API_KEY = ''
OFFSET = '1000'
START_DATE = '11/06/13'
END_DATE = '03/06/14'
DATE = START_DATE + '-' + END_DATE
URL = 'https://api.data.gov/regulations/v3/download?' \
      'documentId=NBA-ABC-123&contentType=pdf'
WRONG_DOCKETID_PATTREN_URL = 'https://api.data.gov:443/regulations/' \
                             'v3/docket.json?api_key="VALID KEY"' \
                             '&docketID=ASD-EPA-HQ-OAR-2011-0028-DDD"'
NO_API_KEY_URL = 'https://api.data.gov:443/regulations/v3/' \
                 'documents.json?api_key=' \
                 '"&po=1000&crd=11/06/13 - 03/06/14'
BAD_DOCUMENTID_URL = "https://api.data.gov:443/regulations/v3" \
                     "/docket.json?api_key=VALID KEY" \
                     "'&documentID=EPA-HQ-OAR-2011-0028-0108-0000"
DOCUMENTS_URL = "https://api.data.gov:443/regulations/v3/document." \
                "json?api_key=VALID KEY&po=1000&crd=11/06/13 - 03/06/14"


@pytest.fixture(name="manager")
def fixture_client_manager_unset(mocker):
    with requests_mock.Mocker() as mockr:
        mockr.get('http://capstone.cs.moravian.edu:5000/get_user_id',
                  json={'user_id': CLIENT_ID})
        mocker.patch('c20_client.get_client_id.open', mock_open())

        manager = ClientManager()

        # Delete the environment variable if it is loaded
        if getenv('API_KEY') is not None:
            del environ['API_KEY']

        # Delete the environment variable if it is loaded
        if getenv('CLIENT_ID') is not None:
            del environ['CLIENT_ID']

        environ['API_KEY'] = API_KEY
        environ['CLIENT_ID'] = CLIENT_ID
        # Start with both keys as None
        manager.reset_keys()

        return manager


def test_do_job_documents_endpoint_call(manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_job',
                 json={'job_type': 'documents', "page_offset": OFFSET,
                       'start_date': START_DATE, 'end_date': END_DATE,
                       'job_id': JOB_ID})
        mock.get('https://api.data.gov:443/regulations' +
                 '/v3/documents.json?api_key=' + API_KEY +
                 '&po=' + OFFSET + '&crd=' + DATE,
                 json={'documents': [{
                     "agencyAcronym": 'NBA',
                     'docketId': 'NBA-ABC',
                     'documentId': 'NBA-ABC-123'}]})
        data = [{
            'folder_name': 'NBA/NBA-ABC/NBA-ABC-123',
            'file_name': 'basic_documents.json',
            'data': {"agencyAcronym": 'NBA',
                     'docketId': 'NBA-ABC',
                     'documentId': 'NBA-ABC-123'}
        }]
        job = [
            {
                'job_type': 'document',
                'document_id': 'NBA-ABC-123'
            },
            {
                'job_type': 'docketId',
                'document_id': 'NBA-ABC'
            }
        ]
        mock.post('http://capstone.cs.moravian.edu:5000/return_result',
                  json={'client_id': CLIENT_ID,
                        'job_id': JOB_ID,
                        'data': data,
                        'jobs': job})

        do_job(manager)
        history = mock.request_history

        assert len(history) == 3
        assert 'capstone' in history[0].url
        assert 'api.data.gov' in history[1].url
        assert 'capstone' in history[2].url


def test_do_job_document_endpoint_call(manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_job',
                 json={'job_type': 'document', 'job_id': JOB_ID,
                       'document_id': 'NBA-ABC-123'})
        mock.get('https://api.data.gov:443/regulations/v3/document.json?' +
                 '&api_key=' + API_KEY + "&documentId=NBA-ABC-123",
                 json={
                     "agencyAcronym": {'value': 'NBA'},
                     'fileFormats': ['url&contentType=pdf'],
                     'docketId': {'value': 'NBA-ABC'},
                     'documentId': {'value': 'NBA-ABC-123'}})
        data = [{
            'folder_name': 'NBA/NBA-ABC/NBA-ABC-123',
            'file_name': 'document.json',
            'data': {"agencyAcronym": 'NBA',
                     'fileFormats': ['url&contentType=pdf']}
        }]
        jobs = [
            'url&contentType=pdf'
        ]
        mock.post('http://capstone.cs.moravian.edu:5000/return_result',
                  json={'client_id': CLIENT_ID,
                        'job_id': JOB_ID,
                        'data': data,
                        'jobs': jobs})

        do_job(manager)
        history = mock.request_history

        assert len(history) == 3
        assert 'capstone' in history[0].url
        assert 'api.data.gov' in history[1].url
        assert 'capstone' in history[2].url


def test_do_job_docket_endpoint_call(manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_job',
                 json={'job_type': 'docket', 'job_id': JOB_ID,
                       'docket_id': 'ABC'})
        mock.get("https://api.data.gov:443/" +
                 "regulations/v3/docket.json?api_key=" +
                 API_KEY + "&docketId=ABC",
                 json={
                     "agencyAcronym": 'NBA',
                     'information': 'some data',
                     'docketId': 'NBA-ABC'})
        data = [{
            'folder_name': 'NBA/NBA-ABC/',
            'file_name': 'docket.json',
            'data': {"agencyAcronym": 'NBA',
                     'information': 'some data'}
        }]
        mock.post('http://capstone.cs.moravian.edu:5000/return_result',
                  json={'client_id': CLIENT_ID,
                        'job_id': JOB_ID,
                        'data': data})

        do_job(manager)
        history = mock.request_history

        assert len(history) == 3
        assert 'capstone' in history[0].url
        assert 'api.data.gov' in history[1].url
        assert 'capstone' in history[2].url


def test_do_job_download_endpoint_call(manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_job',
                 json={'job_type': 'download', 'job_id': JOB_ID,
                       'folder_name': 'NBA/NBA-ABC/NBA-ABC-123/',
                       'file_name': 'NBA-ABC-123',
                       'file_type': 'pdf',
                       'url': URL})
        mock.get("https://api.data.gov/regulations/v3/"
                 "download?documentId=NBA-ABC-123"
                 "&contentType=pdf",
                 text='return data')
        data = {
            'folder_name': 'NBA/NBA-ABC/NBA-ABC-123/',
            'file_name': 'NBA-ABC-123',
            'file_type': 'pdf',
            'data': {"agencyAcronym": 'NBA',
                     'fileContent': 'some data'}
        }
        mock.post('http://capstone.cs.moravian.edu:5000/return_file',
                  json={'client_id': CLIENT_ID,
                        'job_id': JOB_ID,
                        'data': data})

        do_job(manager)
        history = mock.request_history

        assert len(history) == 3
        assert 'capstone' in history[0].url
        assert 'api.data.gov' in history[1].url
        assert 'capstone' in history[2].url


def test_do_job_none_job(manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_job',
                 json={'job_type': 'none', 'job_id': JOB_ID,
                       })
        do_job(manager)
        history = mock.request_history

        assert len(history) == 1
        assert 'capstone' in history[0].url


def test_no_connection_made_to_server(manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_job',
                 exc=True)

        with pytest.raises(NoConnectionError):
            do_job(manager)


def test_bad_request_error():
    with requests_mock.Mocker() as mock:
        mock.get(WRONG_DOCKETID_PATTREN_URL,
                 status_code=400)

        with pytest.raises(IncorrectIDPatternException):
            result = handling_erorr(WRONG_DOCKETID_PATTREN_URL,
                                    message_report=[":received 400:"
                                                    " Bad Requests"])
            mock.post('http://capstone.cs.moravian.edu/report_failure',
                      json={'client_id': CLIENT_ID,
                            'job_id': JOB_ID,
                            'message': result})


def test_forbidden_error():
    with requests_mock.Mocker() as mock:
        mock.get(NO_API_KEY_URL,
                 status_code=403)

        with pytest.raises(IncorrectApiKeyException):
            result = handling_erorr(NO_API_KEY_URL,
                                    message_report=[":received 403:"
                                                    " Forbidden"])
            mock.post('http://capstone.cs.moravian.edu/report_failure',
                      json={'client_id': CLIENT_ID,
                            'job_id': JOB_ID,
                            'message': result})


def test_not_found_error():
    with requests_mock.Mocker() as mock:
        mock.get(BAD_DOCUMENTID_URL,
                 status_code=404)

        with pytest.raises(BadDocIDException):
            result = handling_erorr(BAD_DOCUMENTID_URL,
                                    message_report=[":received 404:"
                                                    " Not Found"])
            mock.post('http://capstone.cs.moravian.edu/report_failure',
                      json={'client_id': CLIENT_ID,
                            'job_id': JOB_ID,
                            'message': result})


def test_too_many_requests_error():
    with requests_mock.Mocker() as mock:
        mock.get(DOCUMENTS_URL,
                 status_code=429)

        with pytest.raises(ExceedCallLimitException):
            result = handling_erorr(DOCUMENTS_URL,
                                    message_report=[":received 429:"
                                                    " Too Many Requests"])
            mock.post('http://capstone.cs.moravian.edu/report_failure',
                      json={'client_id': CLIENT_ID,
                            'job_id': JOB_ID,
                            'message': result})


def test_server_overloaded_error():
    with requests_mock.Mocker() as mock:
        mock.get(DOCUMENTS_URL,
                 status_code=503)

        with pytest.raises(ServiceUnavailableError):
            result = handling_erorr(DOCUMENTS_URL,
                                    message_report=[":received 503:"
                                                    " Service Unavailable"])
            mock.post('http://capstone.cs.moravian.edu/report_failure',
                      json={'client_id': CLIENT_ID,
                            'job_id': JOB_ID,
                            'message': result})
