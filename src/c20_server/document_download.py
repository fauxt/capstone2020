import json
import requests
from c20_server import regulations_api_errors
import os
from dotenv import load_dotenv, find_dotenv


def download_document(api_key, document_id=""):
    """
    downloads a file based on a url, api key and document_id (if given)
    """

    if document_id == "":
        url = "https://api.data.gov:443/regulations/v3/documents.json?"
        data = requests.get(url + api_key + '&rpp=1')
    else:
        url = "https://api.data.gov:443/regulations/v3/document.json?"
        data = requests.get(url + api_key + "&documentId=" + document_id)
    if data.status_code == 403:
        raise regulations_api_errors.InvalidApiKeyException
    if data.status_code == 429:
        raise regulations_api_errors.RateLimitException
    if data.status_code == 404:
        raise regulations_api_errors.BadDocumentIDException
    get_attachments(data)
    document = data.json()
    return document


def get_attachments(data):
    doc = data.json()
    print(json.dumps(doc, indent="     "))


def main():
    load_dotenv(find_dotenv())
    api_key = os.getenv("API_KEY")
    doc_id = "EPA-HQ-OAR-2006-0859-0159"
    result = download_document("api_key=" + api_key, doc_id)


if __name__ == '__main__':
    main()
