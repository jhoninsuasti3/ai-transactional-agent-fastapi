"""Structured logging configuration using structlog.

Provides JSON-formatted logs with automatic context injection.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.stdlib import BoundLogger
from structlog.types import EventDict, Processor

from apps.orchestrator.settings import settings


def add_app_context(_logger: Any, _method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to all log entries.

    Args:
        logger: Logger instance
        method_name: Method name
        event_dict: Event dictionary

    Returns:
        Updated event dictionary with app context
    """
    event_dict["app"] = settings.APP_NAME
    event_dict["version"] = settings.APP_VERSION
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def setup_logging() -> None:
    """Configure structured logging with structlog.

    Sets up:
    - JSON output for production
    - Console output for development
    - Automatic context injection
    - Proper log levels
    """
    # Determine processors based on environment
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]

    # Add exception formatting
    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.format_exc_info)
    else:
        processors.append(structlog.dev.set_exc_info)

    # Configure structlog
    structlog.configure(
        processors=processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    formatter: logging.Formatter
    if settings.LOG_FORMAT == "json":
        formatter = structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
        )
    else:
        formatter = structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
        )

    # Setup handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL)

    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_created", user_id=123, email="user@example.com")
    """
    return structlog.get_logger(name)


# Setup logging on module import
setup_logging()

# Export commonly used logger
logger = get_logger(__name__)
