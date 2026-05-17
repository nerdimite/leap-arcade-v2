"""Fixtures for Wikipedia Speed Run HTTP tests."""

import asyncio
from typing import Callable, Generator, List

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from leap.api.routes.games import wiki as wiki_routes
from leap.service.exceptions import BaseServiceException
from leap.types.player import CurrentPlayer, PlayerDTO
from leap.types.wiki import WikiRoundDTO
from tests.fakes import FakeServiceContainer, FakeWikipediaClient, make_fake_container


def register_service_exception_handler(app: FastAPI) -> None:
    async def _handler(request: Request, exc: BaseServiceException) -> JSONResponse:
        return JSONResponse(status_code=exc.http_status.value, content=exc.to_dict())

    app.add_exception_handler(BaseServiceException, _handler)


def sample_wiki_rounds() -> List[WikiRoundDTO]:
    return [
        WikiRoundDTO(
            id="wiki-r1",
            sequence_index=1,
            start_title="TestStart",
            start_url="https://en.wikipedia.org/wiki/TestStart",
            target_title="End",
            target_url="https://en.wikipedia.org/wiki/End",
            clue="API clue line",
            optimal_click_count=2,
            solution_path=["TestStart", "End"],
            time_limit_ms=90_000,
        )
    ]


async def warm_wiki_cache(container: FakeServiceContainer) -> None:
    async with container.context_manager.session() as session:
        await container.wiki_speed_run.initialize(session)


@pytest.fixture
def wiki_client(
    auth_player: CurrentPlayer,
    auth_override: Callable[[FastAPI], None],
) -> Generator[TestClient, None, None]:
    container = make_fake_container(
        players={
            auth_player.id: PlayerDTO(
                id=auth_player.id,
                display_name=auth_player.display_name,
            )
        },
        wiki_rounds=sample_wiki_rounds(),
        wikipedia_client=FakeWikipediaClient(
            {
                "TestStart": "<section><p>TestStart open</p></section>",
                "Mid": "<section><p>mid page</p></section>",
            }
        ),
    )
    asyncio.run(warm_wiki_cache(container))
    app = FastAPI()
    register_service_exception_handler(app)
    app.state.container = container
    app.include_router(wiki_routes.router, prefix="/games/wiki")
    auth_override(app)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
