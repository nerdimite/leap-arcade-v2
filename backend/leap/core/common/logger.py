"""Structured logging via structlog.

Configures both structlog and the stdlib root logger so that all log output —
including from the OpenAI Agents SDK — shares the same formatter.
"""

import logging
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import structlog
from structlog.stdlib import LoggerFactory, ProcessorFormatter


def configure_json_logging(log_level: str = "INFO", environment: str = "development") -> None:
    """Configure structlog and stdlib root logger with shared formatting.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        environment: Runtime environment. Production/staging use JSON output.
    """
    resolved_level = getattr(logging, log_level.upper(), logging.INFO)
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        timestamper,
    ]

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            *shared_processors,
            ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    use_json = environment in ("production", "staging")

    formatter = ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer()
            if use_json
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(resolved_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    if use_json:
        log_dir = Path(__file__).parent.parent.parent / ".logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / f"{environment}.json")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def configure_openai_agents_logging(*, agents_log_level: str = "DEBUG") -> None:
    """Route OpenAI Agents SDK logs through the same formatter as app stdout.

    Call this after configure_json_logging() if you want SDK debug output.

    Args:
        agents_log_level: Level for openai.agents and openai.agents.tracing.
    """
    root = logging.getLogger()
    if not root.handlers:
        return

    stream_formatter = root.handlers[0].formatter
    resolved = getattr(logging, agents_log_level.upper(), logging.DEBUG)

    for name in ("openai.agents", "openai.agents.tracing"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.setLevel(resolved)
        lg.propagate = False
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(stream_formatter)
        lg.addHandler(handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structured logger bound to the given module name.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        BoundLogger that accepts key/value pairs per log call.
    """
    return structlog.get_logger(name)


@contextmanager
def pipeline_context(*, pipeline: str, doc_id: str, **fields: Any) -> Iterator[None]:
    """Bind pipeline and doc_id to the structlog context for a run.

    Safe for async code when using structlog.contextvars.merge_contextvars.
    """
    bind: dict[str, Any] = {"pipeline": pipeline, "doc_id": doc_id, **fields}
    structlog.contextvars.bind_contextvars(**bind)
    try:
        yield
    finally:
        structlog.contextvars.unbind_contextvars(*bind.keys())
