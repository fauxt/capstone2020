from os import environ, getenv
from unittest.mock import mock_open
import pytest
import requests_mock
from c20_client.get_client_id import (
    ClientManager,
    save_client_env_variable
)

CLIENT_ID = '1234'
API_KEY = 'xxxx-xyz-xxxx'


@pytest.fixture(name="manager")
def fixture_client_manager_unset(mocker):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_user_id',
                 json={'user_id': CLIENT_ID})
        mocker.patch('c20_client.get_client_id.open', mock_open())

        manager = ClientManager()

        # Delete the environment variable if it is loaded
        if getenv('CLIENT_ID') is not None:
            del environ['CLIENT_ID']

        # Delete the environment variable if it is loaded
        if getenv('API_KEY') is not None:
            del environ['API_KEY']

        # Start with both keys as None
        manager.reset_keys()

        return manager


def test_request_id_call(manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_user_id',
                 json={'user_id': CLIENT_ID})

        client_id = manager.request_id()
        history = mock.request_history

        assert len(history) == 1
        assert 'capstone' in history[0].url
        assert client_id == CLIENT_ID
        assert manager.client_id == CLIENT_ID


def test_write_env_variable(mocker):
    file_mock = mocker.patch('c20_client.get_client_id.open', mock_open())
    save_client_env_variable(CLIENT_ID)
    file_mock.assert_called_once_with('.env', 'a+')
    file_mock().write.assert_called_once_with("CLIENT_ID=" + CLIENT_ID + "\n")


def test_id_not_exist_in_env(manager):
    manager.reset_keys()
    assert not manager.client_has_id()
    assert manager.client_id is None


def tests_check_not_in_environment(mocker, manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_user_id',
                 json={'user_id': CLIENT_ID})
        file_mock = mocker.patch('c20_client.get_client_id.open', mock_open())

        manager.check_for_id()
        history = mock.request_history

        assert len(history) == 1
        assert 'capstone' in history[0].url
        file_mock.assert_called_once_with('.env', 'a+')
        file_mock().write.assert_called_once_with(
            "CLIENT_ID=" + CLIENT_ID + "\n")
        assert manager.client_id == CLIENT_ID


def test_id_exist_in_environment(manager):
    environ['CLIENT_ID'] = CLIENT_ID
    manager.reset_keys()
    assert manager.client_has_id()
    assert manager.client_id == CLIENT_ID


def tests_check_in_environment(manager):
    with requests_mock.Mocker() as mock:
        mock.get('http://capstone.cs.moravian.edu:5000/get_user_id',
                 json={'user_id': CLIENT_ID})

        environ['CLIENT_ID'] = CLIENT_ID
        manager.reset_keys()
        manager.check_for_id()
        history = mock.request_history

        assert len(history) == 0
        assert manager.client_id == CLIENT_ID


def test_api_key_from_environment(manager):
    assert manager.api_key is None
    environ['API_KEY'] = API_KEY
    manager.reset_keys()
    assert manager.api_key == API_KEY
