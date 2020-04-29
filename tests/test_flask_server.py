import json
from unittest.mock import patch
import pytest
from c20_server.flask_server import create_app, redis_connect
from c20_server.mock_job_manager import MockJobManager
from c20_server.spy_data_repository import SpyDataRepository
from c20_server.job import DocumentsJob
from c20_server.database import MockDatabase


@pytest.fixture(name='job_manager')
def job_manager_fixture():
    r_database = MockDatabase(True).fake_redis
    job_manager = MockJobManager(r_database)
    return job_manager


@pytest.fixture(name='client')
def client_fixture(job_manager):
    r_database = MockDatabase(True).fake_redis
    app = create_app(job_manager, SpyDataRepository(), r_database)
    app.config['TESTING'] = True
    return app.test_client()


def test_initialize_user_ids(client):
    result = client.get('/get_user_id')
    json_ = json.loads(result.data)
    assert json_['user_id'] == 'User1'


def test_return_result_success(job_manager, client):
    app = create_app(job_manager, SpyDataRepository(), MockDatabase(True))
    app.config['TESTING'] = True
    client = app.test_client()

    json_data = {
        'client_id': 'client1',
        'job_id': 'job1',
        'data': [
            {
                'folder_name': 'thisisafoldername',
                'file_name': 'thisisafilename',
                'data': {}
            }
        ],
        'jobs': [
            {
                'job_type': 'documents',
                'job_id': 'thisiajobid',
                'page_offset': 'thisiapageoffset',
                'start_date': 'thisisastartdate',
                'end_date': 'thisisanenddate'
            },
        ]
    }
    result = client.post('/return_result', data=json.dumps(json_data),
                         content_type='application/json')
    assert result.status_code == 200
    assert job_manager.add_job_called
    assert job_manager.num_unassigned() == 1


def test_return_result_empty_data(client):
    result = client.post('/return_result', data={})
    assert result.status_code == 400


def test_single_job_return(job_manager):
    job_manager.add_job(DocumentsJob(job_id=1, page_offset=0,
                                     start_date='03-01-2020',
                                     end_date='04-01-2020'))
    app = create_app(job_manager, SpyDataRepository(), MockDatabase(True))
    app.config['TESTING'] = True
    client = app.test_client()
    result = client.get('/get_job')
    assert job_manager.request_job_called
    assert result.data == b'{"job_id": 1,' \
                          b' "page_offset": 0,' \
                          b' "start_date": "03-01-2020",' \
                          b' "end_date": "04-01-2020",' \
                          b' "job_type": "documents"}'


def test_none_job_return_when_no_job(job_manager):
    app = create_app(job_manager, SpyDataRepository(), MockDatabase(True))
    app.config['TESTING'] = True
    client = app.test_client()
    result = client.get('/get_job')
    assert job_manager.request_job_called
    job = json.loads(result.data)
    assert job['job_type'] == 'none'


def test_report_one_job_as_failure(job_manager):
    job_manager.add_job(DocumentsJob(job_id=1, page_offset=0,
                                     start_date='03-01-2020',
                                     end_date='04-01-2020'))
    app = create_app(job_manager, SpyDataRepository(), MockDatabase(True))
    app.config['TESTING'] = True
    client = app.test_client()
    assert job_manager.num_unassigned() == 1

    client.get('/get_job')
    assert job_manager.request_job_called
    assert job_manager.num_unassigned() == 0

    json_data = {
        'client_id': 100,
        'job_id': 0,
        'client_message': 'Regulations.gov API is not working.'
    }
    result = client.post('/report_failure', data=json.dumps(json_data),
                         content_type='application/json')
    assert result.status_code == 200
    assert job_manager.num_unassigned() == 1


def test_store_single_data_item(job_manager):
    data_repository_spy = SpyDataRepository()
    app = create_app(job_manager, data_repository_spy, MockDatabase(True))
    app.config['TESTING'] = True
    client = app.test_client()

    json_data = {
        'client_id': '1',
        'job_id': '1',
        'data': [
            {
                'folder_name': 'foldername',
                'file_name': 'filename',
                'data': {}
            }
        ],
        'jobs': []
    }

    client.post('/return_result', data=json.dumps(json_data),
                content_type='application/json')

    first_save = data_repository_spy.saved_items[0]

    assert first_save.directory_name == 'foldername'
    assert first_save.filename == 'filename'
    assert first_save.contents == {}


def test_store_multiple_data_items(job_manager):
    data_repository_spy = SpyDataRepository()
    app = create_app(job_manager, data_repository_spy, MockDatabase(True))
    app.config['TESTING'] = True
    client = app.test_client()

    json_data = {
        'client_id': '1',
        'job_id': '1',
        'data': [
            {
                'folder_name': 'foldername1',
                'file_name': 'filename1',
                'data': {}
            },
            {
                'folder_name': 'foldername1',
                'file_name': 'filename2',
                'data': {}
            },
            {
                'folder_name': 'foldername2',
                'file_name': 'filename3',
                'data': {}
            }
        ],
        'jobs': []
    }

    client.post('/return_result', data=json.dumps(json_data),
                content_type='application/json')

    first_save = data_repository_spy.saved_items[0]
    assert first_save.directory_name == 'foldername1'
    assert first_save.filename == 'filename1'
    assert first_save.contents == {}

    second_save = data_repository_spy.saved_items[1]
    assert second_save.directory_name == 'foldername1'
    assert second_save.filename == 'filename2'
    assert second_save.contents == {}

    third_save = data_repository_spy.saved_items[2]
    assert third_save.directory_name == 'foldername2'
    assert third_save.filename == 'filename3'
    assert third_save.contents == {}


def test_run_server_with_no_redis_connection():
    with patch('sys.exit') as exit_server:
        redis_connect()
        assert exit_server.called
