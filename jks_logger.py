#!/usr/bin/env python
# filename: jks_logger.py
#


import logging

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


def logger(log_level=None,
           log_fmt="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"):
    """
    The log message is only emitted if the handler and logger are
    configured to emit messages of that level or higher.
    :param log_level: Set the root logger level to the specified level.
    :param log_fmt: Use the specified format string for the handler.
    :return: a logger with specified name and format
    """
    _level = LEVELS.get(log_level, logging.NOTSET)

    logging.basicConfig(level=_level,
                        format=log_fmt
                        )

    _logger = logging.getLogger(__name__)
    return _logger
