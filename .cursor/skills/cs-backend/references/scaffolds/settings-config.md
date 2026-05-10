# Settings & Config Scaffold

## app/config/settings.py

```python
import os
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
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

    # Auth (Clerk)
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: str = ""
    JWKS_URL: str = ""
    JWKS_ALGORITHM: str = "RS256"

    # API
    API_VERSION_PREFIX: str = "/api/v1"
    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_ALLOWED_METHODS: list[str] = ["*"]
    CORS_ALLOWED_HEADERS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    ALLOWED_HOSTS: list[str] = ["*"]

    # Security
    HMAC_SECRET: str = "change-me-in-production"
    INTERNAL_ADMIN_TOKEN: str = ""

    @field_validator(
        "CORS_ALLOWED_ORIGINS",
        "CORS_ALLOWED_METHODS",
        "CORS_ALLOWED_HEADERS",
        "ALLOWED_HOSTS",
        mode="before",
    )
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


def reload_settings() -> Settings:
    global _settings
    _settings = Settings()
    return _settings
```

## app/config/constants.py

```python
from pathlib import Path

# ABAC
ABAC_POLICIES_FILEPATH = str(Path(__file__).parent / "policies.json")

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Timezone
DEFAULT_TIMEZONE = "UTC"

# Add domain-specific constants below
```

## app/config/errors.py

```python
from http import HTTPStatus


class ErrorCodes:
    # Common: 4000-4099
    RESOURCE_NOT_FOUND = 4001
    VALIDATION_ERROR = 4002
    UNAUTHORIZED = 4003
    FORBIDDEN = 4004
    INTERNAL_ERROR = 4005

    # Auth: 4200-4299
    INVALID_TOKEN = 4200
    EXPIRED_TOKEN = 4201
    MISSING_TOKEN = 4202


class ErrorHttpStatus:
    RESOURCE_NOT_FOUND = HTTPStatus.NOT_FOUND
    VALIDATION_ERROR = HTTPStatus.UNPROCESSABLE_ENTITY
    UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
    FORBIDDEN = HTTPStatus.FORBIDDEN
    INTERNAL_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR
    INVALID_TOKEN = HTTPStatus.UNAUTHORIZED
    EXPIRED_TOKEN = HTTPStatus.UNAUTHORIZED
    MISSING_TOKEN = HTTPStatus.UNAUTHORIZED


class ErrorMessages:
    RESOURCE_NOT_FOUND = "Resource not found"
    VALIDATION_ERROR = "Validation failed"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Access denied"
    INTERNAL_ERROR = "Internal server error"
    INVALID_TOKEN = "Invalid authentication token"
    EXPIRED_TOKEN = "Authentication token has expired"
    MISSING_TOKEN = "Authentication token is required"
```

## .env.example

```bash
# Environment
ENVIRONMENT="local"
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# Database
POSTGRES_CONNECTION_STRING=

# Auth (Clerk)
CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
JWKS_URL=
JWKS_ALGORITHM=RS256

# API
API_VERSION_PREFIX=/api/v1
CORS_ALLOWED_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=*

# Security
HMAC_SECRET=change-me-in-production
INTERNAL_ADMIN_TOKEN=
```
