# uv & Scripts

## Why uv?

`uv` is a fast Python package manager and project tool. It replaces pip, pip-tools, virtualenv, and parts of poetry/pdm.

## Essential Commands

| Command | Purpose |
|---------|---------|
| `uv init --python 3.13` | Create new project |
| `uv add <package>` | Add production dependency |
| `uv add --group dev <package>` | Add dev dependency |
| `uv remove <package>` | Remove dependency |
| `uv sync` | Install all dependencies (creates .venv) |
| `uv run <command>` | Run command in project's virtualenv |
| `uv lock` | Update lockfile |
| `uv python install 3.13` | Install Python version |

## pyproject.toml Structure

```toml
[project]
name = "my-service"
version = "0.1.0"
description = "My FastAPI backend service"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.128.0",
    "uvicorn>=0.40.0",
    "pydantic>=2.12.0",
    "pydantic-settings>=2.12.0",
    "sqlalchemy>=2.0.45",
    "asyncpg>=0.31.0",
    "alembic>=1.18.0",
    "psycopg2-binary>=2.9.11",
    "structlog>=25.5.0",
    "rich>=14.0.0",
    "gunicorn>=23.0.0",
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
packages = ["my_package", "tests"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
markers = ["e2e: End-to-end API tests"]
filterwarnings = ["ignore::pytest.PytestCollectionWarning"]
```

## Custom Scripts

Define entry points in `[project.scripts]`:

```toml
[project.scripts]
dev          = "my_package.main:dev"
start        = "my_package.main:start"
e2e-teardown = "tests.e2e.teardown:main"
```

These map to functions:

```python
# my_package/main.py

def dev():
    """Development server with hot reload."""
    import uvicorn
    uvicorn.run(
        "my_package.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        reload_dirs=["my_package"],
    )

def start():
    """Production server with Gunicorn."""
    import subprocess
    subprocess.run([
        "gunicorn", "my_package.main:app",
        "--bind", "0.0.0.0:8080",
        "--workers", "4",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--timeout", "120",
    ])
```

Usage: `uv run dev`, `uv run start`, `uv run e2e-teardown`

## Alembic via uv

```bash
uv run alembic revision --autogenerate -m "add orders table"
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic history
```

## Workflow

```bash
# Start a new project
uv init --python 3.13
uv add fastapi uvicorn pydantic pydantic-settings structlog

# Add a new dependency
uv add httpx

# Dev dependencies
uv add --group dev pytest pyright

# Install everything
uv sync

# Run dev server
uv run dev

# Run tests
uv run pytest -m e2e
```
