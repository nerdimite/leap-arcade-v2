# Logger Scaffold

## app/core/common/logger.py

Structured JSON logging using `structlog`. Production environments get JSON output with file logging; local development gets colorized console output.

```python
import logging
import sys
from pathlib import Path

import structlog
from structlog.stdlib import LoggerFactory


def configure_json_logging(settings) -> None:
    """Configure structured logging. Call once at app startup."""
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.ENVIRONMENT in ("production", "staging", "dev"):
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )

    if settings.ENVIRONMENT in ("production", "staging", "dev"):
        log_dir = Path(__file__).parent.parent.parent.parent / ".logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.json")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
```

## Usage

```python
from app.core.common.logger import get_logger

logger = get_logger(__name__)

# Structured key-value logging
logger.info("order_created", order_id="ord_123", amount=99.99)
logger.warning("rate_limit_approaching", endpoint="/api/v1/items", remaining=5)
logger.error("payment_failed", order_id="ord_123", error="insufficient_funds")
```

## Initialization

Called once in `main.py` at module level:

```python
from app.config.settings import get_settings
from app.core.common.logger import configure_json_logging

settings = get_settings()
configure_json_logging(settings)
```

## Reducing Noisy Libraries

After `configure_json_logging`, suppress verbose third-party loggers:

```python
import logging

logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("sqlalchemy").setLevel(logging.INFO)
```

## Output Formats

**Local** (console, colored):
```
2025-01-15 10:30:45 [info] order_created  order_id=ord_123 amount=99.99
```

**Production** (JSON, also written to `.logs/app.json`):
```json
{"event": "order_created", "order_id": "ord_123", "amount": 99.99, "level": "info", "timestamp": "2025-01-15T10:30:45.123Z"}
```

## Dependencies

```bash
uv add structlog rich
```
