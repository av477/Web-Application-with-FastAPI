# app/logging_config.py

"""
Module: logging_config.py

Central logging setup for the calculator application. Log records are written both to
the console and to a rotating log file so that operations and errors can be reviewed
after the server has stopped.

Configuration (environment variables):
- LOG_LEVEL: Minimum level to record (DEBUG, INFO, WARNING, ERROR). Defaults to INFO.
- LOG_FILE: Path of the log file. Defaults to logs/app.log.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_LOG_FILE = "logs/app.log"
MAX_LOG_BYTES = 1_000_000  # Rotate the log file once it reaches about 1 MB
BACKUP_COUNT = 3           # Keep the three most recent rotated log files


def configure_logging() -> None:
    """
    Configure the root logger with a console handler and a rotating file handler.

    Calling this function more than once is safe: handlers are only added the first
    time, so log lines are never duplicated.
    """
    root_logger = logging.getLogger()
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger.setLevel(getattr(logging, level_name, logging.INFO))

    if getattr(root_logger, "_calculator_configured", False):
        return

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    log_file = Path(os.getenv("LOG_FILE", DEFAULT_LOG_FILE))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    root_logger._calculator_configured = True
