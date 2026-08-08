"""Centralized logging configuration for CoralAI."""
import logging
import sys

from app.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance for the given module name."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        logger.propagate = False

    return logger
