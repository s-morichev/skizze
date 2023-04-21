from logging.config import dictConfig
from typing import Any

from app.core.config import settings

logging_config: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s: %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
}

if settings.debug:
    logging_config["root"]["level"] = "DEBUG"

dictConfig(logging_config)
