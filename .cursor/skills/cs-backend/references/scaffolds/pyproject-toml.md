# pyproject.toml Scaffold

```toml
[project]
name = "my-service"
version = "0.1.0"
description = "My FastAPI backend service"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.128.0",
    "uvicorn>=0.40.0",
    "gunicorn>=23.0.0",
    "pydantic>=2.12.0",
    "pydantic-settings>=2.12.0",
    "sqlalchemy>=2.0.45",
    "asyncpg>=0.31.0",
    "alembic>=1.18.0",
    "psycopg2-binary>=2.9.11",
    "structlog>=25.5.0",
    "rich>=14.0.0",
    "httpx>=0.28.0",
    "pyjwt[crypto]>=2.10.0",
    "cachetools>=6.2.0",
]

[dependency-groups]
dev = [
    "pyright>=1.1.400",
    "pytest>=9.0.0",
    "pytest-asyncio>=1.3.0",
    "python-dotenv>=1.2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
package = true

[tool.hatch.build.targets.wheel]
packages = ["app", "tests"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
markers = ["e2e: End-to-end API tests against a live server"]
filterwarnings = ["ignore::pytest.PytestCollectionWarning"]

[project.scripts]
dev          = "app.main:dev"
start        = "app.main:start"
e2e-teardown = "tests.e2e.teardown:main"
```

## Notes

- Replace `"app"` in `packages` with your actual package name
- Replace `"my-service"` with your project name
- Add/remove dependencies based on setup answers (see setup.md)
- The `[tool.uv] package = true` tells uv to treat this as an installable package
- `[tool.hatch.build.targets.wheel] packages` includes `tests` so test utilities are importable
