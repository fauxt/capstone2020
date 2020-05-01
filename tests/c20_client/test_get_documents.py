"""
Test the retrieve_docket.py file
"""
import requests_mock
import pytest
from c20_client.get_documents import get_documents
from c20_client import reggov_api_doc_error

CLIENT_ID = 1
JOB_ID = 1
URL = 'https://api.data.gov:443/regulations/v3/documents.json?api_key='
API_KEY = "VALID KEY"
OFFSET = '1000'
START_DATE = '11/06/13'
END_DATE = '03/06/14'


def test_get_documents():
    with requests_mock.Mocker() as mock:
        mock.get(URL + API_KEY + "&po=" + OFFSET +
                 '&crd=' + START_DATE + '-' + END_DATE,
                 json={'test': 'The test is successful'})
        response = get_documents(API_KEY, OFFSET, START_DATE, END_DATE)

        assert response == {'test': 'The test is successful'}


def test_bad_url():
    with requests_mock.Mocker() as mock:
        mock.get(URL + API_KEY + "&po=" + OFFSET +
                 '&crd=' + START_DATE + '-' + END_DATE,
                 json='The test yields a bad id', status_code=404)

        with pytest.raises(reggov_api_doc_error.BadDocIDException):
            get_documents(API_KEY, OFFSET, START_DATE, END_DATE)


def test_bad_api_key():
    with requests_mock.Mocker() as mock:
        mock.get(URL + 'INVALID' + "&po=" + OFFSET +
                 '&crd=' + START_DATE + '-' + END_DATE,
                 json='The test yields a bad api key', status_code=403)

        with pytest.raises(reggov_api_doc_error.IncorrectApiKeyException):
            get_documents('INVALID', OFFSET, START_DATE, END_DATE)


def test_no_api_key():
    with requests_mock.Mocker() as mock:
        mock.get(URL + '' + "&po=" + OFFSET +
                 '&crd=' + START_DATE + '-' + END_DATE,
                 json='The test yields a bad api key', status_code=403)

        with pytest.raises(reggov_api_doc_error.IncorrectApiKeyException):
            get_documents('', OFFSET, START_DATE, END_DATE)


def test_maxed_api_key():
    with requests_mock.Mocker() as mock:
        mock.get(URL + API_KEY + "&po=" + OFFSET +
                 '&crd=' + START_DATE + '-' + END_DATE,
                 json='The test yields a overused api key', status_code=429)

        with pytest.raises(reggov_api_doc_error.ExceedCallLimitException):
            get_documents(API_KEY, OFFSET, START_DATE, END_DATE)
