from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from leap.api.routes import auth, health, leaderboard, sessions
from leap.api.routes.games import crossword, four_pics, picture, rapid_fire, wiki
from leap.config.settings import get_settings
from leap.core.common.logger import configure_json_logging
from leap.core.context_manager import ContextManager
from leap.service.container import ServiceContainer
from leap.service.exceptions import BaseServiceException


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_json_logging(settings.LOG_LEVEL, settings.ENVIRONMENT)

    context_manager = ContextManager(settings)
    await context_manager.initialize()

    if settings.SEED_ON_STARTUP:
        async with context_manager.session() as session:
            from leap.seeds.loader import seed_all

            await seed_all(session)

    app.state.context_manager = context_manager
    app.state.container = ServiceContainer(context_manager)

    yield

    await context_manager.close()


app = FastAPI(title="LEAP Tournament Platform API", lifespan=lifespan)


@app.exception_handler(BaseServiceException)
async def service_exception_handler(request: Request, exc: BaseServiceException):
    return JSONResponse(
        status_code=exc.http_status.value,
        content=exc.to_dict(),
    )


app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(wiki.router, prefix="/games/wiki", tags=["Wiki"])
app.include_router(picture.router, prefix="/games/picture", tags=["Picture"])
app.include_router(rapid_fire.router, prefix="/games/rapid-fire", tags=["Rapid Fire"])
app.include_router(four_pics.router, prefix="/games/four-pics", tags=["Four Pics"])
app.include_router(crossword.router, prefix="/games/crossword", tags=["Crossword"])
