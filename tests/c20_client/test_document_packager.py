import pytest
from c20_client import document_packager

CLIENT_ID = '1'
JOB_ID = 1

TEST_JSON = {
    'agencyAcronym': {'value': 'test'},
    'docketId': {'value': 'docket-number-5'},
    'documentId': {'value': 'document-number-10'}
}


@pytest.fixture(name='document')
def fixture_document():
    response = document_packager.package_document(TEST_JSON,
                                                  CLIENT_ID, JOB_ID)
    return response


ONE_FILE_FORMAT_JSON = {
    'fileFormats': [
        'DOCUMENTS_URL&contentType=pdf'
    ],
    'agencyAcronym': {'value': 'test'},
    'docketId': {'value': 'docket-number-5'},
    'documentId': {'value': 'document-number-10'}
}


@pytest.fixture(name='one_downloads_document')
def fixture_one_downloads_document():
    response = document_packager.package_document(ONE_FILE_FORMAT_JSON,
                                                  CLIENT_ID, JOB_ID)
    return response


MANY_FILE_FORMAT_JSON = {
    'fileFormats': [
        'DOCUMENTS_URL&contentType=pdf',
        'URL2&contentType=html'
    ],
    'agencyAcronym': {'value': 'test'},
    'docketId': {'value': 'docket-number-5'},
    'documentId': {'value': 'document-number-10'}
}


@pytest.fixture(name='many_downloads_document')
def fixture_many_downloads_document():
    response = document_packager.package_document(MANY_FILE_FORMAT_JSON,
                                                  CLIENT_ID, JOB_ID)
    return response


ONE_ATTACHMENT_JSON = {
    "attachments": [{
        "attachmentOrderNumber": 1,
        'fileFormats': [
            'DOCUMENTS_URL&contentType=pdf'
        ],
        'title': 'stay_in_school'
    }],
    'agencyAcronym': {'value': 'test'},
    'docketId': {'value': 'docket-number-5'},
    'documentId': {'value': 'document-number-10'}
}


@pytest.fixture(name='one_attachment_document')
def fixture_one_attachment_document():
    response = document_packager.package_document(ONE_ATTACHMENT_JSON,
                                                  CLIENT_ID, JOB_ID)
    return response


ATTACHMENT_MANY_FILES_JSON = {
    "attachments": [{
        "attachmentOrderNumber": 1,
        'fileFormats': [
            'DOCUMENTS_URL&contentType=pdf'
        ],
        'title': 'stay_in_school'
    }, {
        "attachmentOrderNumber": 2,
        'fileFormats': [
            'URL2&contentType=html'
        ],
        'title': 'read_books'
    }],
    'agencyAcronym': {'value': 'test'},
    'docketId': {'value': 'docket-number-5'},
    'documentId': {'value': 'document-number-10'}
}


@pytest.fixture(name='one_attachment_many_file_document')
def fixture_one_attachment_many_files_document():
    response = document_packager.package_document(ATTACHMENT_MANY_FILES_JSON,
                                                  CLIENT_ID, JOB_ID)
    return response


MANY_ATTACHMENTS_JSON = {
    "attachments": [{
        "attachmentOrderNumber": 1,
        'fileFormats': [
            'DOCUMENTS_URL&contentType=pdf'
        ],
        'title': 'stay_in_school'
    }, {
        "attachmentOrderNumber": 2,
        'fileFormats': [
            'URL2&contentType=html'
        ],
        'title': 'read_books'
    }],
    'agencyAcronym': {'value': 'test'},
    'docketId': {'value': 'docket-number-5'},
    'documentId': {'value': 'document-number-10'}
}


@pytest.fixture(name='many_attachments_document')
def fixture_many_attachments_document():
    response = document_packager.package_document(ATTACHMENT_MANY_FILES_JSON,
                                                  CLIENT_ID, JOB_ID)
    return response


NO_ATTACHMENT_JSON = {
    "attachments": [{
        "attachmentOrderNumber": 1
    }],
    'agencyAcronym': {'value': 'test'},
    'docketId': {'value': 'docket-number-5'},
    'documentId': {'value': 'document-number-10'}
}


@pytest.fixture(name='no_attachment_document')
def fixture_no_attachment_document():
    response = document_packager.package_document(NO_ATTACHMENT_JSON,
                                                  CLIENT_ID, JOB_ID)
    return response


def test_client_id(document):
    assert document['client_id'] == CLIENT_ID


def test_job_id(document):
    assert document['job_id'] == JOB_ID


def test_folder_name(document):
    assert document['data'][0]['folder_name'] == \
           'test/docket-number-5/document-number-10/'


def test_file_name(document):
    assert document['data'][0]['file_name'] == \
           'basic_document.json'


def test_document_data(document):
    assert document['data'][0]['data'] == TEST_JSON


def test_one_job(one_downloads_document):
    assert one_downloads_document['jobs'][0]['url'] ==\
           'DOCUMENTS_URL&contentType=pdf'


def test_multiple_fileformats(many_downloads_document):
    assert many_downloads_document['jobs'][0]['url'] ==\
           'DOCUMENTS_URL&contentType=pdf'
    assert many_downloads_document['jobs'][1]['url'] ==\
        'URL2&contentType=html'


def test_one_attachment(one_attachment_document):
    assert one_attachment_document['jobs'][0]['url'] ==\
           'DOCUMENTS_URL&contentType=pdf'


def test_one_attachment_many_fileformats(one_attachment_many_file_document):
    assert one_attachment_many_file_document['jobs'][0]['url'] == \
        'DOCUMENTS_URL&contentType=pdf'
    assert one_attachment_many_file_document['jobs'][1]['url'] == \
        'URL2&contentType=html'


def test_many_attachments(many_attachments_document):
    assert many_attachments_document['jobs'][0]['url'] == \
        'DOCUMENTS_URL&contentType=pdf'
    assert many_attachments_document['jobs'][1]['url'] == \
        'URL2&contentType=html'


def test_attachment_with_no_url(no_attachment_document):
    assert len(no_attachment_document['jobs']) == 0
