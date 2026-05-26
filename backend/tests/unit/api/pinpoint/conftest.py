"""Fixtures for Pinpoint subcutaneous HTTP tests."""

import asyncio
from typing import Callable, Generator, List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes.games import pinpoint as pinpoint_routes
from leap.games.pinpoint.service import PinpointService
from leap.types.pinpoint import PinpointPuzzleDTO
from leap.types.player import CurrentPlayer, PlayerDTO
from tests.fakes import (
    FakeContextManager,
    FakeGameSessionDAO,
    FakePinpointPuzzleAttemptDAO,
    FakePinpointPuzzleDAO,
    FakePlayerDAO,
)
from tests.unit.api.rapid_fire.conftest import register_service_exception_handler


def sample_puzzles() -> List[PinpointPuzzleDTO]:
    return [
        PinpointPuzzleDTO(
            id="aaaaaaaa-aaaa-aaaa-aaaa-0000000000aa",
            answer="Alpha",
            answer_aliases=["alpha"],
            clue1="a1",
            clue2="a2",
            clue3="a3",
            clue4="a4",
            clue5="a5",
        ),
        PinpointPuzzleDTO(
            id="bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb",
            answer="Beta",
            answer_aliases=["beta"],
            clue1="b1",
            clue2="b2",
            clue3="b3",
            clue4="b4",
            clue5="b5",
        ),
    ]


class PinpointTestContainer:
    """Minimal container exposing only Pinpoint for route tests."""

    def __init__(self, puzzles: List[PinpointPuzzleDTO]) -> None:
        self.context_manager = FakeContextManager()
        self.player_dao = FakePlayerDAO()
        self.game_session_dao = FakeGameSessionDAO(player_dao=self.player_dao)
        self.pinpoint = PinpointService(
            self.context_manager,
            self.game_session_dao,
            FakePinpointPuzzleDAO(puzzles),
            FakePinpointPuzzleAttemptDAO(),
        )


async def warm_pinpoint_cache(container: PinpointTestContainer) -> None:
    async with container.context_manager.session() as session:
        await container.pinpoint.initialize(session)


@pytest.fixture
def pinpoint_client(
    auth_player: CurrentPlayer,
    auth_override: Callable[[FastAPI], None],
) -> Generator[TestClient, None, None]:
    container = PinpointTestContainer(sample_puzzles())
    container.player_dao._players[auth_player.id] = PlayerDTO(
        id=auth_player.id,
        display_name=auth_player.display_name,
    )
    asyncio.run(warm_pinpoint_cache(container))
    app = FastAPI()
    register_service_exception_handler(app)
    app.state.container = container
    app.include_router(pinpoint_routes.router, prefix="/games/pinpoint")
    auth_override(app)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
