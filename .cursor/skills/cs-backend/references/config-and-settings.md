# Config & Settings

## Settings Class

Uses `pydantic-settings` for environment-driven configuration with a singleton pattern:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"

    # Database
    POSTGRES_CONNECTION_STRING: str = ""
    POSTGRES_POOL_SIZE: int = 5
    POSTGRES_MAX_OVERFLOW: int = 10

    # Auth
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: str = ""
    JWKS_URL: str = ""
    JWKS_ALGORITHM: str = "RS256"

    # API
    API_VERSION_PREFIX: str = "/api/v1"
    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: list[str] = ["*"]

    # Validators for comma-separated lists
    @field_validator("CORS_ALLOWED_ORIGINS", "ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_comma_separated(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

## Settings Groups

Organize settings by concern:

| Group | Variables | Purpose |
|-------|-----------|---------|
| Environment | `ENVIRONMENT`, `LOG_LEVEL`, `LOG_FORMAT` | Runtime environment |
| Database | `POSTGRES_CONNECTION_STRING`, pool settings | DB connection |
| Auth | `CLERK_*`, `JWKS_*` | JWT verification |
| API | `API_VERSION_PREFIX`, `CORS_*`, `ALLOWED_HOSTS` | HTTP config |
| Security | `HMAC_SECRET`, `INTERNAL_ADMIN_TOKEN` | Tokens & keys |
| Providers | Email/SMS/Storage config | External services |

## Constants File

`config/constants.py` holds domain constants — never hardcode strings in services:

```python
from pathlib import Path

ABAC_POLICIES_FILEPATH = str(Path(__file__).parent / "policies.json")
DEFAULT_TIMEZONE = "UTC"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
```

## Error Configuration

Three parallel classes in `config/errors.py`:

```python
class ErrorCodes:
    # Common: 4000-4099
    RESOURCE_NOT_FOUND = 4001
    VALIDATION_ERROR = 4002
    # Domain: 4100-4199 (assign per domain)
    ORDER_NOT_FOUND = 4100

class ErrorHttpStatus:
    RESOURCE_NOT_FOUND = HTTPStatus.NOT_FOUND
    VALIDATION_ERROR = HTTPStatus.UNPROCESSABLE_ENTITY
    ORDER_NOT_FOUND = HTTPStatus.NOT_FOUND

class ErrorMessages:
    RESOURCE_NOT_FOUND = "Resource not found"
    VALIDATION_ERROR = "Validation failed"
    ORDER_NOT_FOUND = "Order not found"
```

Domain exceptions reference these: `BaseServiceException(ErrorCodes.ORDER_NOT_FOUND, ErrorMessages.ORDER_NOT_FOUND, ErrorHttpStatus.ORDER_NOT_FOUND)`.

## .env File Pattern

```bash
# .env.example (committed) — template with empty values
ENVIRONMENT="local"
POSTGRES_CONNECTION_STRING=
CLERK_SECRET_KEY=

# .env (gitignored) — actual values
# .env.test (gitignored) — test environment values
# .env.dev, .env.staging — environment-specific (optional, committed)
```

## Logger

Uses structlog for structured JSON logging:

```python
import structlog

def configure_json_logging(settings):
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if settings.ENVIRONMENT == "local":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(processors=processors)

def get_logger(name: str = __name__):
    return structlog.get_logger(name)
```

Always use: `from app.core.common.logger import get_logger`
