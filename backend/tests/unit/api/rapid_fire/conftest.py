"""Fixtures for Rapid Fire subcutaneous HTTP tests."""

import asyncio
from typing import Callable, Generator, List

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from leap.api.routes.games import rapid_fire as rapid_fire_routes
from leap.service.exceptions import BaseServiceException
from leap.types.player import CurrentPlayer, PlayerDTO
from leap.types.rapid_fire import RapidFireQuestionDTO
from tests.fakes import FakeServiceContainer, make_fake_container


def sample_questions() -> List[RapidFireQuestionDTO]:
    """Three questions — enough for mid-game resume and non-trivial pools."""
    return [
        RapidFireQuestionDTO(
            id="rf-q1",
            question="Q1?",
            options=["A", "B", "C", "D"],
            correct_option_index=1,
            time_limit_ms=10_000,
        ),
        RapidFireQuestionDTO(
            id="rf-q2",
            question="Q2?",
            options=["W", "X", "Y", "Z"],
            correct_option_index=2,
            time_limit_ms=10_000,
        ),
        RapidFireQuestionDTO(
            id="rf-q3",
            question="Q3?",
            options=["P", "Q", "R", "S"],
            correct_option_index=3,
            time_limit_ms=10_000,
        ),
    ]


def register_service_exception_handler(app: FastAPI) -> None:
    async def _handler(request: Request, exc: BaseServiceException) -> JSONResponse:
        return JSONResponse(status_code=exc.http_status.value, content=exc.to_dict())

    app.add_exception_handler(BaseServiceException, _handler)


async def warm_rapid_fire_cache(container: FakeServiceContainer) -> None:
    async with container.context_manager.session() as session:
        await container.rapid_fire.initialize(session)


@pytest.fixture
def rapid_fire_client(
    auth_player: CurrentPlayer,
    auth_override: Callable[[FastAPI], None],
) -> Generator[TestClient, None, None]:
    """Authenticated client with in-memory fakes, question cache warmed, and error mapping."""
    container = make_fake_container(
        players={
            auth_player.id: PlayerDTO(
                id=auth_player.id,
                display_name=auth_player.display_name,
            )
        },
        rapid_fire_questions=sample_questions(),
    )
    asyncio.run(warm_rapid_fire_cache(container))
    app = FastAPI()
    register_service_exception_handler(app)
    app.state.container = container
    app.include_router(rapid_fire_routes.router, prefix="/games/rapid-fire")
    auth_override(app)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
