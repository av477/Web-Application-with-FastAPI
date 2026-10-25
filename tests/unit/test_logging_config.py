# tests/unit/test_logging_config.py

"""
Unit tests for app/logging_config.configure_logging.

The root logger is shared by the whole test session, so each test saves its state,
starts from a clean logger, and restores the original state afterwards.
"""

import logging
from logging.handlers import RotatingFileHandler

import pytest

from app.logging_config import configure_logging


@pytest.fixture
def clean_root_logger():
    """Give each test an unconfigured root logger, then restore the original one."""
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    saved_flag = getattr(root, "_calculator_configured", False)

    root.handlers = []
    root._calculator_configured = False
    yield root

    for handler in root.handlers:
        handler.close()
    root.handlers = saved_handlers
    root.setLevel(saved_level)
    root._calculator_configured = saved_flag


def test_adds_console_and_file_handlers(clean_root_logger, tmp_path, monkeypatch):
    """Logging goes to both the console and a rotating log file."""
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "app.log"))

    configure_logging()

    handler_types = {type(h) for h in clean_root_logger.handlers}
    assert logging.StreamHandler in handler_types
    assert RotatingFileHandler in handler_types


def test_writes_records_to_log_file(clean_root_logger, tmp_path, monkeypatch):
    """Records are written to the file named by LOG_FILE, creating missing folders."""
    log_file = tmp_path / "nested" / "calc.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))

    configure_logging()
    logging.getLogger("test.logging_config").info("hello from the test")
    for handler in clean_root_logger.handlers:
        handler.flush()

    contents = log_file.read_text(encoding="utf-8")
    assert "hello from the test" in contents
    assert "INFO" in contents


@pytest.mark.parametrize(
    "env_value, expected_level",
    [("DEBUG", logging.DEBUG), ("warning", logging.WARNING), ("not-a-level", logging.INFO)],
    ids=["debug", "lowercase_warning", "invalid_falls_back_to_info"],
)
def test_level_comes_from_environment(clean_root_logger, tmp_path, monkeypatch, env_value, expected_level):
    """LOG_LEVEL sets the level; unknown values fall back to INFO."""
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "app.log"))
    monkeypatch.setenv("LOG_LEVEL", env_value)

    configure_logging()

    assert clean_root_logger.level == expected_level


def test_default_level_is_info(clean_root_logger, tmp_path, monkeypatch):
    """Without LOG_LEVEL, the root logger records INFO and above."""
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "app.log"))
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    configure_logging()

    assert clean_root_logger.level == logging.INFO


def test_calling_twice_does_not_duplicate_handlers(clean_root_logger, tmp_path, monkeypatch):
    """configure_logging is idempotent, so log lines are never written twice."""
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "app.log"))

    configure_logging()
    handler_count = len(clean_root_logger.handlers)
    configure_logging()

    # pytest attaches its own capture handlers too, so compare counts instead of a fixed number
    assert len(clean_root_logger.handlers) == handler_count
    file_handlers = [h for h in clean_root_logger.handlers if isinstance(h, RotatingFileHandler)]
    assert len(file_handlers) == 1
