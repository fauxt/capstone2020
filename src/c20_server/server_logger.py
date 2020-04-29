import logging

LOGGER = logging.getLogger(__name__)
HDLR = logging.FileHandler('server.log')
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
HDLR.setFormatter(FORMATTER)
LOGGER.addHandler(HDLR)
LOGGER.setLevel(logging.INFO)
