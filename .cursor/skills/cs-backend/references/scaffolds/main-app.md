# FastAPI Application Scaffold

## app/main.py

```python
import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.routes import api_router
from app.config.settings import Settings, get_settings
from app.core.common.logger import configure_json_logging, get_logger
from app.core.context.app_context import (
    cleanup_shared_resources,
    get_app_context,
    initialize_shared_resources,
)
from app.service.exceptions import BaseServiceException

settings = get_settings()
configure_json_logging(settings)
app_context = get_app_context()
logger = get_logger(__name__)

logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("sqlalchemy").setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("starting_application", environment=settings.ENVIRONMENT)
    await initialize_shared_resources(app_context)
    yield
    logger.info("shutting_down_application")
    await cleanup_shared_resources(app_context)


app = FastAPI(
    title="My Service",
    description="Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openurl="/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)

# -- Middleware --
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)


# -- Exception Handlers --

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
        content={
            "success": False,
            "message": "Validation error",
            "code": 4002,
            "http_status": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "error": {"details": exc.errors()},
        },
    )


@app.exception_handler(BaseServiceException)
async def service_exception_handler(request: Request, exc: BaseServiceException):
    return JSONResponse(
        status_code=exc.http_status.value,
        content=exc.to_dict(),
    )


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    return JSONResponse(
        status_code=HTTPStatus.FORBIDDEN.value,
        content={
            "success": False,
            "message": str(exc) or "Access denied",
            "code": 4004,
            "http_status": HTTPStatus.FORBIDDEN.value,
            "error": {},
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "code": exc.status_code,
            "http_status": exc.status_code,
            "error": {},
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        content={
            "success": False,
            "message": "Internal server error",
            "code": 4005,
            "http_status": HTTPStatus.INTERNAL_SERVER_ERROR.value,
            "error": {},
        },
    )


# -- Routes --
app.include_router(api_router, prefix=settings.API_VERSION_PREFIX)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


def dev():
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        reload_dirs=["app"],
    )


def start():
    import subprocess
    subprocess.run([
        "gunicorn", "app.main:app",
        "--bind", "0.0.0.0:8080",
        "--workers", "4",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--timeout", "120",
    ])
```

## app/core/context/app_context.py

```python
from typing import Any, Optional

from app.config.settings import get_settings
from app.core.common.logger import get_logger


class AppContext:
    _instance: Optional["AppContext"] = None
    _state: dict[str, Any]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._state = {}
        return cls._instance

    @property
    def logger(self):
        return get_logger("app")

    @property
    def settings(self):
        return get_settings()


def get_app_context() -> AppContext:
    return AppContext()


async def initialize_shared_resources(ctx: AppContext):
    from app.core.context.context_manager import ContextManager
    ctx._state["context_manager"] = ContextManager()
    # Initialize JWKS client if using JWT auth:
    # from jwt import PyJWKClient
    # ctx._state["jwks_client"] = PyJWKClient(ctx.settings.JWKS_URL, cache_jwk_set=True)


async def cleanup_shared_resources(ctx: AppContext):
    cm = ctx._state.get("context_manager")
    if cm:
        await cm.cleanup()


def get_context_manager():
    """FastAPI dependency to get the ContextManager singleton."""
    ctx = get_app_context()
    return ctx._state["context_manager"]
```

## app/core/context/context_manager.py

```python
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from app.config.settings import get_settings
from app.core.database.postgres_provider import PostgresProvider


class ContextManager:
    def __init__(self):
        self._postgres: Optional[PostgresProvider] = None
        self._pg_lock = asyncio.Lock()
        self._settings = get_settings()

    async def get_postgres_provider(self) -> PostgresProvider:
        if self._postgres is None:
            async with self._pg_lock:
                if self._postgres is None:
                    self._postgres = PostgresProvider(
                        connection_string=self._settings.POSTGRES_CONNECTION_STRING,
                        pool_size=self._settings.POSTGRES_POOL_SIZE,
                        max_overflow=self._settings.POSTGRES_MAX_OVERFLOW,
                    )
        return self._postgres

    @asynccontextmanager
    async def session(self, context):
        provider = await self.get_postgres_provider()
        async with await provider.get_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def cleanup(self):
        if self._postgres:
            await self._postgres.close()
```
