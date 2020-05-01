from os import getenv, environ
import requests_mock
from unittest.mock import mock_open
import pytest
from c20_client import client_decide_call
from c20_client.get_client_id import ClientManager

DOCUMENTS_URL = 'https://api.data.gov:443/regulations/v3/documents.json?'
API_KEY = '123'
OFFSET = '0'
START_DATE = '12/03/19'
END_DATE = '01/05/20'
DOCUMENTS_JOB = {
        "page_offset": OFFSET,
        "start_date": START_DATE,
        "end_date": END_DATE
}
DOCUMENTS_JSON = {
    'documents': [{
        'agencyAcronym': 'test',
        'data': 'test Documents',
        'docketId': 'docket-number-3',
        'documentId': 'document-number-100'
    }]
}


DOCUMENT_URL = 'https://api.data.gov:443/regulations/v3/document.json?'
DOC_ID = "EPA-HQ-OAR-2011-0028-0108"
DOCUMENT_JOB = {
    'job_id': 'ABC123',
    'job_type': 'document',
    'document_id': 'EPA-HQ-OAR-2011-0028-0108'
}
DOCUMENT_JSON = {
    'agencyAcronym': {'value': 'test'},
    'docketId': {'value': 'docket-number-5'},
    'documentId': {'value': 'document-number-10'}
}


DOCKET_URL = 'https://api.data.gov:443/regulations/v3/docket.json?'
DOCK_ID = 'EPA-HQ-OAR-2011-0028'
DOCKET_JSON = {
    "agencyAcronym": "EPA",
    "docketId": "EPA-HQ-OAR-2011-0028",
}

DOCKET_JOB = {
    'job_id': 'ABC123',
    'job_type': 'docket',
    'docket_id': 'EPA-HQ-OAR-2011-0028'
}

DOWNLOAD_URL = 'https://api.data.gov/regulations/v3/download?' \
               'documentId=EPA-HQ-OAR-2011-0028-0108&contentType=pdf'
DOWNLOAD_JSON = {
    'data': 'test data',
    'file_name': 'test_file',
    'file_type': 'pdf',
    'folder_name': 'abc/docket-id-3/document-id-7/'
    }
DOWNLOAD_JOB = {
    'job_id': '123abc',
    'job_type': 'download',
    'folder_name': 'abc/abc-123/abc-123-xyz/',
    'file_name': 'title_of_file',
    'file_type': 'pdf',
    'url':
        'https://api.data.gov/regulations/v3/download?'
        'documentId=EPA-HQ-OAR-2011-0028-0108&contentType=pdf'
}

@pytest.fixture(name="manager")
def fixture_client_manager_unset(mocker):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu/get_user_id',
                 json={'user_id': 'id'})
        mocker.patch('c20_client.get_client_id.open', mock_open())

        manager = ClientManager()

        # Delete the environment variable if it is loaded
        if getenv('CLIENT_ID') is not None:
            del environ['CLIENT_ID']

        # Delete the environment variable if it is loaded
        if getenv('API_KEY') is not None:
            del environ['API_KEY']

        environ['CLIENT_ID'] = '1'
        environ['API_KEY'] = API_KEY
        # Start with both keys as None
        manager.reset_keys()

        return manager


def test_documents_data(manager):
    with requests_mock.Mocker() as mock:
        mock.get(DOCUMENTS_URL + 'api_key=' + API_KEY + "&po=" + OFFSET +
                 '&crd=' + START_DATE + '-' + END_DATE,
                 json=DOCUMENTS_JSON)
        result = client_decide_call.find_documents_data(
            manager, DOCUMENTS_JOB, 1)
        assert result['data'][0]['data']['agencyAcronym'] == 'test'
        assert result['data'][0]['data']['data'] == 'test Documents'
        assert result['data'][0]['data']['docketId'] == 'docket-number-3'
        assert result['data'][0]['data']['documentId'] == 'document-number-100'


def test_document_data(manager):
    with requests_mock.Mocker() as mock:
        mock.get(DOCUMENT_URL + 'api_key=' + API_KEY +
                 '&documentId=' + DOC_ID, json=DOCUMENT_JSON)
        result = client_decide_call.find_document_data(
            manager, DOCUMENT_JOB, 'ABC123')
        assert result['data'][0]['folder_name'] == \
            'test/docket-number-5/document-number-10/'
        assert result['data'][0]['file_name'] == \
            'basic_document.json'


def test_docket_data(manager):
    with requests_mock.Mocker() as mock:
        mock.get(DOCKET_URL + 'api_key=' + API_KEY + '&docketId=' + DOCK_ID,
                 json=DOCKET_JSON)
        result = client_decide_call.find_docket_data(manager, DOCKET_JOB, 1)
        assert result['data'][0]['folder_name'] == 'EPA/EPA-HQ-OAR-2011-0028/'
        assert result['data'][0]['file_name'] == 'docket.json'
        assert result['data'][0]['data']['agencyAcronym'] == 'EPA'
        assert result['data'][0]['data']['docketId'] == 'EPA-HQ-OAR-2011-0028'
        assert result['data'][0]['data'] == {
            "agencyAcronym": "EPA",
            "docketId": "EPA-HQ-OAR-2011-0028"
        }


def test_download_data(manager):
    with requests_mock.Mocker() as mock:
        mock.get(DOWNLOAD_URL + '&api_key=' + API_KEY, json=DOWNLOAD_JSON)
        result = client_decide_call.find_download_data(
            manager, DOWNLOAD_JOB, 1)
        print('------')
        print(manager.client_id)
        print('------')
        assert result['client_id'] == '1'
        assert result['data'][0]['folder_name'] ==\
            'abc/abc-123/abc-123-xyz/'
        assert result['data'][0]['file_name'] == 'title_of_file.pdf'
