# Common Utilities Scaffold

Shared utility modules for ID generation, pagination, timezone handling, input sanitization, and database connectivity.

## app/core/common/__init__.py

```python
from .id.short_id import generate_id
from .logger import get_logger
from .pagination import calculate_offset, calculate_total_pages, validate_page_number
from .sanitize import sanitize_input
from .timezone import format_iso, local_now, parse_iso, utc_now

__all__ = [
    "generate_id",
    "get_logger",
    "calculate_offset",
    "calculate_total_pages",
    "validate_page_number",
    "sanitize_input",
    "format_iso",
    "local_now",
    "parse_iso",
    "utc_now",
]
```

---

## ID Generation

### app/core/common/id/__init__.py

```python
from .short_id import generate_id

__all__ = ["generate_id"]
```

### app/core/common/id/snowflake.py

Twitter Snowflake algorithm: 64-bit IDs (41-bit timestamp + 10-bit node + 12-bit sequence). Thread-safe, ~4096 IDs/ms/node.

```python
import os
import threading
import time

DEFAULT_EPOCH = 1735689600000  # Jan 1, 2025 00:00:00 UTC
NODE_ID_BITS = 10
SEQUENCE_BITS = 12
MAX_NODE_ID_VALUE = (1 << NODE_ID_BITS) - 1
MAX_SEQUENCE_VALUE = (1 << SEQUENCE_BITS) - 1
MILLISECONDS_MULTIPLIER = 1000


class SnowflakeIDGenerator:
    """Generates 64-bit unique IDs: 1 sign + 41 timestamp + 10 node + 12 sequence."""

    def __init__(self, node_id=None, epoch=DEFAULT_EPOCH):
        if node_id is None:
            node_id = os.getpid() & MAX_NODE_ID_VALUE

        if node_id < 0 or node_id > MAX_NODE_ID_VALUE:
            raise ValueError(f"Node ID must be between 0 and {MAX_NODE_ID_VALUE}")

        self.node_id = node_id
        self.epoch = epoch
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

        self.node_id_shift = SEQUENCE_BITS
        self.timestamp_shift = NODE_ID_BITS + SEQUENCE_BITS

    def _current_timestamp(self):
        return int(time.time() * MILLISECONDS_MULTIPLIER)

    def _wait_for_next_millis(self, last_timestamp):
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def generate_id(self) -> int:
        with self.lock:
            timestamp = self._current_timestamp()

            if timestamp < self.last_timestamp:
                raise RuntimeError(
                    f"Clock moved backwards by {self.last_timestamp - timestamp}ms"
                )

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & MAX_SEQUENCE_VALUE
                if self.sequence == 0:
                    timestamp = self._wait_for_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp
            return (
                ((timestamp - self.epoch) << self.timestamp_shift)
                | (self.node_id << self.node_id_shift)
                | self.sequence
            )

    def parse_id(self, snowflake_id: int) -> dict:
        sequence = snowflake_id & MAX_SEQUENCE_VALUE
        node_id = (snowflake_id >> self.node_id_shift) & MAX_NODE_ID_VALUE
        timestamp_offset = snowflake_id >> self.timestamp_shift
        timestamp = timestamp_offset + self.epoch
        return {
            "timestamp": timestamp,
            "node_id": node_id,
            "sequence": sequence,
            "datetime": time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.gmtime(timestamp / MILLISECONDS_MULTIPLIER),
            ),
        }
```

### app/core/common/id/short_id.py

Prefixed short IDs using base62-encoded snowflakes: `item_3kTMd92xF`.

```python
from .snowflake import SnowflakeIDGenerator

BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

_generator = SnowflakeIDGenerator()


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID: '{prefix}_{base62_snowflake}'."""
    return f"{prefix}_{_int_to_base62(_generator.generate_id())}"


def _int_to_base62(value: int) -> str:
    if value == 0:
        return BASE62_CHARS[0]
    result = []
    while value > 0:
        value, remainder = divmod(value, 62)
        result.append(BASE62_CHARS[remainder])
    return "".join(reversed(result))
```

---

## Pagination

### app/core/common/pagination.py

```python
def validate_page_number(page: int, page_size: int, total_items: int) -> int:
    """Validate page is in bounds. Returns total_pages. Raises PaginationError if exceeded."""
    total_pages = calculate_total_pages(total_items, page_size)
    if page > total_pages:
        from app.service.exceptions import PaginationError
        raise PaginationError(page=page, total_pages=total_pages)
    return total_pages


def calculate_offset(page: int, page_size: int) -> int:
    """Convert 1-indexed page to DB offset."""
    return (page - 1) * page_size


def calculate_total_pages(total_items: int, page_size: int) -> int:
    """Calculate total pages (minimum 1)."""
    return (total_items + page_size - 1) // page_size if total_items > 0 else 1
```

---

## Timezone

### app/core/common/timezone.py

```python
import datetime
import pytz


def utc_now() -> datetime.datetime:
    """Current UTC time, timezone-aware."""
    return datetime.datetime.now(pytz.UTC)


def local_now(timezone_name: str = "UTC") -> datetime.datetime:
    """Current time in the given timezone."""
    return datetime.datetime.now(pytz.timezone(timezone_name))


def format_iso(dt: datetime.datetime) -> str:
    """Format datetime as ISO 8601. Assumes UTC if naive."""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt.isoformat()


def parse_iso(iso_string: str) -> datetime.datetime:
    """Parse ISO 8601 string to timezone-aware datetime."""
    dt = datetime.datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt
```

**Dependency:** `uv add pytz`

---

## Sanitize

### app/core/common/sanitize.py

```python
import re
from typing import Optional


def sanitize_input(
    input_str: str,
    lowercase: bool = False,
    separator: str = "-",
    max_length: Optional[int] = None,
) -> str:
    """Sanitize a string for URL safety.

    Examples:
        sanitize_input("My Company Name!") → "My-Company-Name"
        sanitize_input("hello world", lowercase=True) → "hello-world"
        sanitize_input("Long Name Here", max_length=8) → "Long"
    """
    sanitized = re.sub(r"[^a-zA-Z0-9]+", separator, input_str).strip(separator)

    if lowercase:
        sanitized = sanitized.lower()

    if max_length and len(sanitized) > max_length:
        if separator in sanitized[:max_length]:
            sanitized = sanitized[:sanitized[:max_length].rfind(separator)]
        else:
            sanitized = sanitized[:max_length]
        sanitized = sanitized.rstrip(separator)

    return sanitized
```

---

## Database Provider

### app/core/database/base_database.py

```python
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDatabaseProvider(ABC):
    @abstractmethod
    async def get_session(self) -> AsyncSession: ...

    @abstractmethod
    async def health_check(self) -> bool: ...

    @abstractmethod
    async def close(self) -> None: ...
```

### app/core/database/postgres_provider.py

```python
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database.base_database import BaseDatabaseProvider


class PostgresProvider(BaseDatabaseProvider):
    def __init__(self, connection_string: str, **pool_kwargs):
        self.connection_string = connection_string
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None
        self._pool_kwargs = pool_kwargs

    async def _ensure_engine(self):
        if self._engine is None:
            self._engine = create_async_engine(
                self.connection_string,
                pool_size=self._pool_kwargs.get("pool_size", 5),
                max_overflow=self._pool_kwargs.get("max_overflow", 10),
            )
            self._sessionmaker = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )

    async def get_session(self) -> AsyncSession:
        await self._ensure_engine()
        if self._sessionmaker is None:
            raise RuntimeError("Sessionmaker not initialized")
        return self._sessionmaker()

    async def health_check(self) -> bool:
        try:
            async with await self.get_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception:
            return False

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
```

---

## Dependencies

```bash
uv add structlog rich pytz sqlalchemy asyncpg
```
