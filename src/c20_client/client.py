"""
Gets a job from the server and handles the job based on the type of job
"""

from c20_client.do_client_job import do_multiple_job
from c20_client.get_client_id import ClientManager


def main():
    """
    Run the program
    """
    manager = ClientManager()
    do_multiple_job(manager)


if __name__ == '__main__':
    main()
