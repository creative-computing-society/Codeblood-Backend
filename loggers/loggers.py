import logging
from json import load
from os import path
from logging.config import dictConfig

LOGGER_PATH = path.join(path.dirname(__file__), "loggers.json")


class LevelFilter(logging.Filter):
    def __init__(self, level: int):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level


def setup_logging():
    with open(LOGGER_PATH) as loggers:
        dictConfig(load(loggers))
