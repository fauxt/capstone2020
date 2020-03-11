import pytest
import requests_mock
from c20_server import document_download
from c20_server import regulations_api_errors

URL = "https://api.data.gov:443/regulations/v3/documents.json?"
DOCUMENT_URL = "https://api.data.gov:443/regulations/v3/document.json?"
DOC_ID = "EPA-HQ-OAR-2011-0028-0108"
API_KEY = "12345"


def test_mock_response():
    with requests_mock.Mocker() as mock:
        mock.get(URL + "&api_key=" + "12345" + '&rpp=1', json='document received')
        response = document_download.download_document(API_KEY)
        assert response == 'document received'


def test_no_api_key():
    with requests_mock.Mocker() as mock:
        mock.get(URL + "&api_key=" + '' + '&rpp=1', json={'a': 'b'}, status_code=403)
        with pytest.raises(regulations_api_errors.InvalidApiKeyException):
            document_download.download_document("")


def test_1000_calls():
    with requests_mock.Mocker() as mock:
        mock.get(URL + "&api_key=" + API_KEY + '&rpp=1', json={'a': 'b'}, status_code=429)
        with pytest.raises(regulations_api_errors.RateLimitException):
            document_download.download_document(API_KEY)


def test_document_id():
    with requests_mock.Mocker() as mock:
        mock.get(DOCUMENT_URL + "&api_key=" + API_KEY + "&documentId=" + DOC_ID,
                 json='Json response')
        response = document_download.download_document(API_KEY, DOC_ID)
        assert response == 'Json response'


def test_bad_document_id():
    with requests_mock.Mocker() as mock:
        mock.get(DOCUMENT_URL + "&api_key=" + API_KEY + "&documentId=" + DOC_ID,
                 json={'a': 'b'}, status_code=404)
        with pytest.raises(regulations_api_errors.BadDocumentIDException):
            document_download.download_document(API_KEY, DOC_ID)


def test_document_id_and_no_document_id():
    with requests_mock.Mocker() as mock:
        mock.get(DOCUMENT_URL + "&api_key=" + API_KEY + "&documentId=" + DOC_ID,
                 json='document ID response')
        mock.get(URL + "&api_key=" + API_KEY + '&rpp=1', json='non-document ID response')
        id_response = document_download.download_document(API_KEY, DOC_ID)
        response = document_download.download_document(API_KEY)
        assert response == 'non-document ID response'
        assert id_response == 'document ID response'
