"""Fixtures for Four Pics subcutaneous HTTP tests."""

import asyncio
from typing import Callable, Generator, List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes.games import four_pics as four_pics_routes
from leap.types.four_pics import FourPicsQuestionDTO
from leap.types.player import CurrentPlayer, PlayerDTO
from tests.fakes import FakeServiceContainer, make_fake_container
from tests.unit.api.rapid_fire.conftest import register_service_exception_handler


def sample_questions() -> List[FourPicsQuestionDTO]:
    return [
        FourPicsQuestionDTO(
            id="fp-q1",
            image_paths=[
                "/images/four-pics/a/1.png",
                "/images/four-pics/a/2.png",
                "/images/four-pics/a/3.png",
                "/images/four-pics/a/4.png",
            ],
            odd_one_out_index=2,
        ),
        FourPicsQuestionDTO(
            id="fp-q2",
            image_paths=[
                "/images/four-pics/b/1.png",
                "/images/four-pics/b/2.png",
                "/images/four-pics/b/3.png",
                "/images/four-pics/b/4.png",
            ],
            odd_one_out_index=0,
        ),
        FourPicsQuestionDTO(
            id="fp-q3",
            image_paths=[
                "/images/four-pics/c/1.png",
                "/images/four-pics/c/2.png",
                "/images/four-pics/c/3.png",
                "/images/four-pics/c/4.png",
            ],
            odd_one_out_index=1,
        ),
    ]


async def warm_four_pics_cache(container: FakeServiceContainer) -> None:
    async with container.context_manager.session() as session:
        await container.four_pics.initialize(session)


@pytest.fixture
def four_pics_client(
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
        four_pics_questions=sample_questions(),
    )
    asyncio.run(warm_four_pics_cache(container))
    app = FastAPI()
    register_service_exception_handler(app)
    app.state.container = container
    app.include_router(four_pics_routes.router, prefix="/games/four-pics")
    auth_override(app)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
