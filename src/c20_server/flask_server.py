import json
import sys
from flask import Flask, request
from c20_server.user import User
from c20_server.job import DocumentsJob
from c20_server.job_manager import JobManager
from c20_server.job_translator import job_to_json, handle_jobs
from c20_server.data_extractor import DataExtractor
from c20_server.data_repository import DataRepository
from c20_server.database import Database
from c20_server.server_logger import LOGGER
from c20_server.user_manager import UserManager


def create_app(job_manager, data_repository, database):
    app = Flask(__name__)

    # Note: endpoint names begin with an "_" so that Pylint does not complain
    # about unused functions.

    @app.route('/get_user_id')
    def _get_client_id():
        user_manager = UserManager(database)
        user_id = user_manager.get_new_user_id()
        LOGGER.info('Sending user_id: %s', user_id)
        user_id_json = {'user_id': user_id}
        return user_id_json

    @app.route('/get_job')
    def _get_job():
        LOGGER.info('Requesting Job From Job Queue...')
        requested_job = job_manager.request_job(User(100))
        job = job_to_json(requested_job)
        LOGGER.info('Sending Job to user...')
        return job

    @app.route('/return_result', methods=['POST'])
    def _return_result():
        LOGGER.info('Receiving Data from user...')
        client_data = request.json
        print(client_data)
        if client_data is None:
            LOGGER.error('No Data received to be saved')
            return {}, 400

        update_job_manager(job_manager, client_data)
        save_data(data_repository, client_data['data'])

        return {}, 200

    @app.route('/report_failure', methods=['POST'])
    def _report_failure():
        client_data = request.json
        user_id = client_data['client_id']
        user = User(user_id)
        job_manager.report_failure(user)
        return {}, 200

    return app


def update_job_manager(job_manager, client_data):
    json_data = json.dumps(client_data)
    job_list = handle_jobs(json_data)
    print()
    for job in job_list:
        job_manager.add_job(job)
        LOGGER.info('Adding Job To Job Manager...')
        print('Adding Job To Job Manager...')
        print(job, '\n')


def save_data(data_repository, list_of_data_dicts):
    data_items = DataExtractor.extract(list_of_data_dicts)
    LOGGER.info('Saving the data into the disk...')
    for data_item in data_items:
        data_repository.save_data(data_item.folder_name,
                                  data_item.file_name, data_item.contents)


def redis_connect():
    database = Database()
    if not database.connect():
        LOGGER.error('Redis-server is not running!')
        sys.exit()
    return database.r_database


def launch():
    database = redis_connect()
    job_manager = JobManager(database)
    job_manager.add_job(DocumentsJob('1', 0, '12/28/19', '1/23/20'))
    data_repository = DataRepository(base_path='data')
    app = create_app(job_manager, data_repository, database)
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    launch()
