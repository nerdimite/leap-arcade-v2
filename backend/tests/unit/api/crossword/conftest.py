"""Fixtures for Crossword subcutaneous HTTP tests."""

import asyncio
from typing import Callable, Generator, List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes.games import crossword as crossword_routes
from leap.games.crossword.service import CrosswordService
from leap.types.crossword import CrosswordEntryDTO, CrosswordPuzzleDTO
from leap.types.player import CurrentPlayer, PlayerDTO
from tests.fakes import (
    FakeContextManager,
    FakeCrosswordPuzzleDAO,
    FakeCrosswordSolveDAO,
    FakeGameSessionDAO,
    FakePlayerDAO,
)
from tests.unit.api.rapid_fire.conftest import register_service_exception_handler

PUZZLE_ID = "22222222-2222-2222-2222-222222222222"
GRID = [
    ["M", "I", "C", "R", "O", "S", "E", "R", "V", "I", "C", "E"],
    ["O", None, None, None, None, None, None, None, None, None, None, "V"],
    ["C", None, None, None, None, "D", None, None, None, None, None, "E"],
    ["K", "U", "B", "E", "R", "N", "E", "T", "E", "S", None, "N"],
    [None, None, None, None, None, "S", None, None, None, None, None, "T"],
    ["C", None, None, None, "G", None, None, None, None, None, None, "D"],
    ["A", "T", "O", "M", "I", "C", "I", "T", "Y", None, None, "R"],
    ["C", None, None, None, "T", None, None, None, None, "D", None, "I"],
    ["H", None, None, None, "O", None, None, None, None, "R", None, "V"],
    ["I", None, None, None, "P", "I", "P", "E", "L", "I", "N", "E"],
    ["N", None, None, None, "S", None, None, None, None, "F", None, "N"],
    ["G", None, None, None, None, None, None, None, None, "T", None, None],
]

ENTRIES = [
    CrosswordEntryDTO(
        id="e1",
        puzzle_id=PUZZLE_ID,
        number=1,
        direction="across",
        start_row=0,
        start_col=0,
        answer="MICROSERVICE",
        clue="Small, independently deployable unit (12)",
    ),
    CrosswordEntryDTO(
        id="e2",
        puzzle_id=PUZZLE_ID,
        number=1,
        direction="down",
        start_row=0,
        start_col=0,
        answer="MOCK",
        clue="Simulated object (4)",
    ),
    CrosswordEntryDTO(
        id="e3",
        puzzle_id=PUZZLE_ID,
        number=2,
        direction="down",
        start_row=0,
        start_col=11,
        answer="EVENTDRIVEN",
        clue="Communication style (11)",
    ),
    CrosswordEntryDTO(
        id="e4",
        puzzle_id=PUZZLE_ID,
        number=3,
        direction="down",
        start_row=2,
        start_col=5,
        answer="DNS",
        clue="Protocol (3)",
    ),
    CrosswordEntryDTO(
        id="e5",
        puzzle_id=PUZZLE_ID,
        number=4,
        direction="across",
        start_row=3,
        start_col=0,
        answer="KUBERNETES",
        clue="Container orchestration platform (10)",
    ),
    CrosswordEntryDTO(
        id="e6",
        puzzle_id=PUZZLE_ID,
        number=5,
        direction="down",
        start_row=5,
        start_col=4,
        answer="GITOPS",
        clue="Philosophy of treating infrastructure (6)",
    ),
    CrosswordEntryDTO(
        id="e7",
        puzzle_id=PUZZLE_ID,
        number=6,
        direction="down",
        start_row=5,
        start_col=0,
        answer="CACHING",
        clue="Technique (7)",
    ),
    CrosswordEntryDTO(
        id="e8",
        puzzle_id=PUZZLE_ID,
        number=7,
        direction="across",
        start_row=6,
        start_col=0,
        answer="ATOMICITY",
        clue="ACID property (10)",
    ),
    CrosswordEntryDTO(
        id="e9",
        puzzle_id=PUZZLE_ID,
        number=8,
        direction="down",
        start_row=7,
        start_col=9,
        answer="DRIFT",
        clue="When model degrades (5)",
    ),
    CrosswordEntryDTO(
        id="e10",
        puzzle_id=PUZZLE_ID,
        number=9,
        direction="across",
        start_row=9,
        start_col=4,
        answer="PIPELINE",
        clue="Automated workflow (8)",
    ),
]


def sample_puzzles() -> List[CrosswordPuzzleDTO]:
    return [
        CrosswordPuzzleDTO(
            id=PUZZLE_ID,
            rows=12,
            cols=12,
            grid=GRID,
            entries=ENTRIES,
        )
    ]


class CrosswordTestContainer:
    """Minimal container exposing only Crossword for route tests."""

    def __init__(self, puzzles: List[CrosswordPuzzleDTO]) -> None:
        self.context_manager = FakeContextManager()
        self.player_dao = FakePlayerDAO()
        self.game_session_dao = FakeGameSessionDAO(player_dao=self.player_dao)
        self.crossword = CrosswordService(
            self.context_manager,
            self.game_session_dao,
            FakeCrosswordPuzzleDAO(puzzles),
            FakeCrosswordSolveDAO(),
        )


async def warm_crossword_cache(container: CrosswordTestContainer) -> None:
    async with container.context_manager.session() as session:
        await container.crossword.initialize(session)


@pytest.fixture
def crossword_client(
    auth_player: CurrentPlayer,
    auth_override: Callable[[FastAPI], None],
) -> Generator[TestClient, None, None]:
    container = CrosswordTestContainer(sample_puzzles())
    container.player_dao._players[auth_player.id] = PlayerDTO(
        id=auth_player.id,
        display_name=auth_player.display_name,
    )
    asyncio.run(warm_crossword_cache(container))
    app = FastAPI()
    register_service_exception_handler(app)
    app.state.container = container
    app.include_router(crossword_routes.router, prefix="/games/crossword")
    auth_override(app)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
