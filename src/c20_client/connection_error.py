"""
Errors for connecting to the server
"""


class NoConnectionError(Exception):
    """
    Error for being unable to connect to the server
    """


class ServiceUnavailableError(Exception):
    """
Error for server is overloaded or under maintenance
    """
