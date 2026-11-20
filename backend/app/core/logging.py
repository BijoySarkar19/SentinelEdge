"""Structured logging configuration for SentinelEdge.

Usage
-----
    from app.core.logging import get_logger, setup_logging

    setup_logging()          # call once at application startup
    log = get_logger(__name__)
    log.info("server started", port=8000)
"""
from __future__ import annotations

import logging
import logging.config
import sys
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger

from app.core.config import settings


# ---------------------------------------------------------------------------
# Custom processors
# ---------------------------------------------------------------------------

def _add_app_context(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Inject static application-level fields into every log record."""
    event_dict.setdefault("app", "sentineledge")
    event_dict.setdefault("env", settings.app_env)
    return event_dict


def _drop_color_message_key(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Remove the ``color_message`` key injected by uvicorn's access logger."""
    event_dict.pop("color_message", None)
    return event_dict


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

def get_logger(name: str | None = None, **initial_values: Any) -> structlog.BoundLogger:
    """Return a bound structlog logger.

    Parameters
    ----------
    name:
        Usually ``__name__`` of the calling module.
    **initial_values:
        Extra key-value pairs that are bound permanently to this logger instance.

    Returns
    -------
    structlog.BoundLogger
    """
    logger = structlog.get_logger(name, **initial_values)
    return logger


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    """Configure stdlib logging and structlog.

    Call this **once** at application startup, before any log messages are
    emitted.  Subsequent calls are idempotent.

    * **Development / test**: human-readable, colourised, pretty-printed output.
    * **Production / staging**: machine-readable JSON (one JSON object per line).
    """
    log_level_name: str = settings.log_level.upper()
    log_level: int = getattr(logging, log_level_name, logging.INFO)
    is_production: bool = settings.is_production

    # ------------------------------------------------------------------
    # Shared processors that run on *every* log record regardless of renderer
    # ------------------------------------------------------------------
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        _add_app_context,
        _drop_color_message_key,
    ]

    # ------------------------------------------------------------------
    # Renderer – JSON in production, pretty ConsoleRenderer in development
    # ------------------------------------------------------------------
    if is_production:
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # ------------------------------------------------------------------
    # Configure structlog itself
    # ------------------------------------------------------------------
    structlog.configure(
        processors=[
            *shared_processors,
            # This processor bridges structlog → stdlib so that any stdlib
            # logger (e.g. uvicorn, sqlalchemy) is also formatted by structlog.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )

    # ------------------------------------------------------------------
    # Configure stdlib logging to use structlog's ProcessorFormatter
    # ------------------------------------------------------------------
    formatter = structlog.stdlib.ProcessorFormatter(
        # These processors only run when a *stdlib* logger emits a record.
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Remove any handlers that may have been added by previous calls or
    # by uvicorn/FastAPI before our setup runs.
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Silence very noisy third-party loggers in production
    for noisy in ("sqlalchemy.engine", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(
            logging.WARNING if log_level <= logging.INFO else log_level
        )

    # Let uvicorn and alembic use the root handler we just configured
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error", "alembic"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True

    get_logger(__name__).info(
        "logging configured",
        log_level=log_level_name,
        renderer="json" if is_production else "console",
    )
