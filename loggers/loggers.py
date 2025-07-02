from json import load
from os import path
from logging.config import dictConfig

LOGGER_PATH = path.join(path.dirname(__file__), "loggers.json")


def setup_logging():
    with open(LOGGER_PATH) as loggers:
        dictConfig(load(loggers))
