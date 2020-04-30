import pytest
import requests_mock
from c20_client import get_document
from c20_client import reggov_api_doc_error


CLIENT_ID = 1
JOB_ID = 1
URL = "https://api.data.gov:443/regulations/v3/document.json?"
DOC_ID = "EPA-HQ-OAR-2011-0028-0108"
API_KEY = "12345"


def test_mock_response():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json='document received')
        response = get_document.download_document(API_KEY, DOC_ID)
        assert response == 'document received'


def test_incorrect_id_pattern():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'a': 'b'},
                 status_code=400)
        with pytest.raises(reggov_api_doc_error.IncorrectIDPatternException):
            bad_pattern = 'b4d' + DOC_ID + 'b4d'
            get_document.download_document(API_KEY, bad_pattern)


def test_incorrect_api_key():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'a': 'b'},
                 status_code=403)
        with pytest.raises(reggov_api_doc_error.IncorrectApiKeyException):
            get_document.download_document('INVALID', DOC_ID)


def test_bad_document_id():
    with requests_mock.Mocker() as mock:
        bad_id = DOC_ID + "-0101"
        mock.get(URL, json={'a': 'b'},
                 status_code=404)
        with pytest.raises(reggov_api_doc_error.BadDocIDException):
            get_document.download_document(API_KEY, bad_id)


def test_exceed_call_limit():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'a': 'b'},
                 status_code=429)
        with pytest.raises(reggov_api_doc_error.ExceedCallLimitException):
            get_document.download_document(API_KEY, DOC_ID)
