"""Production logging configuration for HSRAI."""

import logging
import logging.config
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_format: Optional[str] = None,
    json_output: bool = False,
) -> None:
    """Configure structured logging for the HSRAI system."""
    if log_format is None:
        if json_output:
            log_format = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
        else:
            log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": log_format},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
        "loggers": {
            "hsrai": {"level": level, "propagate": False},
            "urcm": {"level": level, "propagate": False},
            "uvicorn": {"level": "WARNING"},
            "uvicorn.access": {"level": "WARNING"},
        },
    })
