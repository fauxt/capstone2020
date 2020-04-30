import pytest
import requests_mock
from c20_client import get_download
from c20_client import reggov_api_doc_error

CLIENT_ID = 1
JOB_ID = 1

URL = "https://api.data.gov:443/regulations/v3/download.json?" \
      "documentId=EPA-HQ-OAR-2011-0028-0108&contentType=pdf"
BAD_URL = "https://api.data.gov:443/regulations/v3/download.json?" \
          "documentId=EPA-HQ-OAR-2011-0000-0108&contentType=pdf"
API_KEY = "12345"


def test_incorrect_api_key():
    with requests_mock.Mocker() as mock:
        mock.get(URL, text='file received',
                 status_code=403)
        with pytest.raises(reggov_api_doc_error.IncorrectApiKeyException):
            get_download.download_file('INVALID', URL)


def test_exceed_call_limit():
    with requests_mock.Mocker() as mock:
        mock.get(URL, text='file received',
                 status_code=429)
        with pytest.raises(reggov_api_doc_error.ExceedCallLimitException):
            get_download.download_file(API_KEY, URL)


def test_bad_url_id():
    with requests_mock.Mocker() as mock:
        mock.get(BAD_URL, text='file received',
                 status_code=404)
        with pytest.raises(reggov_api_doc_error.BadDocIDException):
            get_download.download_file(API_KEY, BAD_URL)


def test_file_downloaded():
    with requests_mock.Mocker() as mock:
        mock.get(URL, text='file received')
        response = get_download.download_file(API_KEY, URL)
        assert response.content == b'file received'
