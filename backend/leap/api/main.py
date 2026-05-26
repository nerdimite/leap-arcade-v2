"""FastAPI application factory + lifespan + global exception handlers.

Route registration slice: auth, lobby, players, leaderboard, rapid_fire, wiki, picture,
health — other game routes ship with their vertical slices.
"""

import logging
import traceback
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from leap.api.routes import auth, health, leaderboard, lobby, players
from leap.api.routes.games import picture, rapid_fire, wiki
from leap.config.settings import get_settings
from leap.core.common.logger import configure_json_logging, get_logger
from leap.core.context_manager import ContextManager
from leap.service.container import ServiceContainer
from leap.service.exceptions import BaseServiceException


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    configure_json_logging(settings.LOG_LEVEL, settings.ENVIRONMENT)
    logger = get_logger(__name__)

    logger.info("Starting LEAP backend", environment=settings.ENVIRONMENT)

    context_manager = ContextManager(settings)
    await context_manager.initialize()

    if settings.SEED_ON_STARTUP:
        from leap.seeds.loader import seed_all

        async with context_manager.session() as session:
            await seed_all(session)

    app.state.context_manager = context_manager
    app.state.container = ServiceContainer(context_manager)

    async with context_manager.session() as session:
        await app.state.container.rapid_fire.initialize(session)
        await app.state.container.wiki_speed_run.initialize(session)
        await app.state.container.picture.initialize(session)

    logger.info("LEAP backend ready")

    yield

    logger.info("Shutting down LEAP backend")
    await context_manager.close()


app = FastAPI(
    title="LEAP Tournament Platform API",
    description="Tournament platform for the Fidelity LEAP onboarding programme",
    version="0.1.0",
    lifespan=lifespan,
)


# Reduce noise from chatty libraries
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


@app.exception_handler(BaseServiceException)
async def service_exception_handler(request: Request, exc: BaseServiceException):
    """Convert domain exceptions raised by services into JSON responses."""
    return JSONResponse(status_code=exc.http_status.value, content=exc.to_dict())


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "code": exc.status_code,
            "http_status": exc.status_code,
            "error": {"type": exc.__class__.__name__, "message": exc.detail},
        },
    )


@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "code": exc.status_code,
            "http_status": exc.status_code,
            "error": {"type": exc.__class__.__name__, "message": exc.detail},
        },
    )


def _sanitize_validation_errors(errors: list) -> list:
    """Strip non-serializable exception objects from ``ctx`` fields."""
    sanitized: list = []
    for error in errors:
        sanitized_error = error.copy()
        if "ctx" in sanitized_error and isinstance(sanitized_error["ctx"], dict):
            ctx = sanitized_error["ctx"].copy()
            if "error" in ctx and isinstance(ctx["error"], Exception):
                ctx["error"] = str(ctx["error"])
            sanitized_error["ctx"] = ctx
        sanitized.append(sanitized_error)
    return sanitized


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    sanitized_errors = _sanitize_validation_errors(list(exc.errors()))
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Request validation failed",
            "code": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "http_status": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "error": {
                "type": "RequestValidationError",
                "message": "Request validation failed",
                "errors": sanitized_errors,
            },
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger = get_logger(__name__)
    logger.error("Unhandled exception", error=str(exc), path=request.url.path, method=request.method, exc_info=True)
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
            "http_status": HTTPStatus.INTERNAL_SERVER_ERROR.value,
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "traceback": traceback.format_exception(exc),
            },
        },
    )


app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(lobby.router, prefix="/lobby", tags=["Lobby"])
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(rapid_fire.router, prefix="/games/rapid-fire", tags=["Rapid Fire"])
app.include_router(wiki.router, prefix="/games/wiki", tags=["Wikipedia Speed Run"])
app.include_router(picture.router, prefix="/games/picture", tags=["Picture Illustration"])
