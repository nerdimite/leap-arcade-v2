# Dockerfile Scaffold

Production-ready Dockerfile for a uv-managed FastAPI app.

## Dockerfile

```dockerfile
FROM python:3.13-slim

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies (add/remove as needed)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock README.md ./

# Install production dependencies only
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

EXPOSE 8080

# Use the uv-managed start script (gunicorn)
CMD ["uv", "run", "start"]
```

## .dockerignore

```
.venv/
.git/
.gitignore
.env
.env.*
!.env.example
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.logs/
.cursor/
docs/
tests/
scratchpad/
*.egg-info/
dist/
build/
```

## Build & Run

```bash
# Build
docker build -t my-service .

# Run (pass env vars)
docker run -p 8080:8080 --env-file .env my-service

# Run with build arg for environment
docker build --build-arg ENVIRONMENT=staging -t my-service .
```

## With Build Args

If you need the environment at build time (e.g., conditional installs):

```dockerfile
ARG ENVIRONMENT=production
ENV ENVIRONMENT=${ENVIRONMENT}
```

## Key Points

- `COPY --from=ghcr.io/astral-sh/uv:latest` pulls `uv` without adding it to the build context
- `uv sync --frozen --no-dev` installs only production deps from the lockfile
- Dependency files are copied before app code for Docker layer caching — deps only reinstall when `pyproject.toml` or `uv.lock` change
- `CMD ["uv", "run", "start"]` uses the custom script that launches Gunicorn with Uvicorn workers
