import logging
from typing import Union, Optional
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from sys import stdout


log_formatter = logging.Formatter("[%(asctime)s] %(name)s.%(levelname)s: %(message)s")
log_console_handler = logging.StreamHandler(stdout)
log_console_handler.setFormatter(log_formatter)


def console_logger(name: str, level: Union[int, str] = logging.DEBUG):
    l = logging.getLogger(name)
    l.setLevel(level)
    l.addHandler(log_console_handler)
    return l


class LoggedClass:
    def __init__(self, *args, logger: Optional[logging.Logger] = None, **kwargs):
        if logger:
            self.logger = logger.getChild(f"{self.__class__.__name__}")
        else:
            self.logger = logging.getLogger(f"{self.__class__.__name__}")
        super().__init__()
