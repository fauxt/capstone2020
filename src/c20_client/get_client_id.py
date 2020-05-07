"""
File used to check for an environment variable for id and to
get an id form server and assign the id to the enviornment
variable if the environment variable does not yet exist
"""
from os import getenv
import requests
from dotenv import load_dotenv
from c20_client.connection_error import NoConnectionError


class ClientManager():
    """
    Manages id functions for getting, saving, and
    checking the existence of an id
    """
    def __init__(self):
        load_dotenv()
        self.client_id = getenv("CLIENT_ID")
        self.api_key = getenv("API_KEY")
        self.check_for_id()

    def reset_keys(self):
        """
        Function is used mainly for testing purposes.
        Sets keys to currently loaded enviornment variables.
        """
        self.client_id = getenv("CLIENT_ID")
        self.api_key = getenv("API_KEY")

    def check_for_id(self):
        """
        Checks for an id, if not exist the Manager makes
        the request for an id and saves it
        """
        # If client does not have an id
        if not self.client_has_id():
            save_client_env_variable(self.request_id())

    def request_id(self):
        """
        Ask Moravian server endpoint for id
        Returns an id
        """
        try:
            response = requests.get(
                'http://capstone.cs.moravian.edu:5000/get_user_id')
        except Exception:
            raise NoConnectionError

        self.client_id = response.json()['user_id']
        return self.client_id

    def client_has_id(self):
        """
        Checks for the client id as a .env variable called CLIENT_ID
        """
        # Client does not yet have an id
        if self.client_id is None:
            return False

        # Client has an id assigned
        return True


def save_client_env_variable(client_id):
    """
    Append client id to the environment varibale file
    Will create file if does not already exist
    """
    writer = open('.env', 'a+')
    writer.write("CLIENT_ID=" + str(client_id) + "\n")
    writer.close()
