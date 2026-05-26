"""Word Hunt service happy-path acceptance tests."""

from datetime import datetime, timedelta, timezone

import pytest

from leap.games.word_hunt.service import WordHuntService
from leap.service.exceptions import WordHuntSessionAlreadyCompletedException
from leap.types.game import GameSessionStatus
from leap.types.word_hunt import WordHuntPuzzleDTO, WordHuntWordDTO
from tests.fakes import (
    FakeAsyncSession,
    FakeContextManager,
    FakeGameSessionDAO,
    FakeWordHuntFindDAO,
    FakeWordHuntPuzzleDAO,
)

PUZZLE_ID = "11111111-1111-1111-1111-111111111111"
GRID = [
    ["D", "E", "V", "O", "P", "S", "W", "I", "K", "C"],
    ["Q", "M", "T", "B", "Y", "F", "H", "J", "N", "L"],
    ["S", "P", "R", "I", "N", "G", "A", "B", "O", "O"],
    ["Z", "X", "C", "V", "B", "N", "M", "Q", "U", "U"],
    ["A", "N", "G", "U", "L", "A", "R", "E", "S", "D"],
    ["F", "G", "H", "J", "K", "L", "P", "Q", "R", "S"],
    ["A", "G", "E", "N", "T", "S", "T", "U", "V", "W"],
    ["I", "J", "K", "L", "M", "N", "O", "P", "Q", "R"],
    ["S", "T", "U", "V", "W", "X", "Y", "Z", "A", "B"],
    ["C", "D", "E", "F", "G", "H", "I", "J", "K", "L"],
]


def _word(
    word_id: str,
    word: str,
    clue: str,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
) -> WordHuntWordDTO:
    return WordHuntWordDTO(
        id=word_id,
        puzzle_id=PUZZLE_ID,
        word=word,
        clue=clue,
        start_row=start_row,
        start_col=start_col,
        end_row=end_row,
        end_col=end_col,
    )


def _puzzle() -> WordHuntPuzzleDTO:
    return WordHuntPuzzleDTO(
        id=PUZZLE_ID,
        rows=10,
        cols=10,
        grid=GRID,
        words=[
            _word("w1", "DEVOPS", "clue devops", 0, 0, 0, 5),
            _word("w2", "SPRING", "clue spring", 2, 0, 2, 5),
            _word("w3", "ANGULAR", "clue angular", 4, 0, 4, 6),
            _word("w4", "AGENTS", "clue agents", 6, 0, 6, 5),
            _word("w5", "CLOUD", "clue cloud", 0, 9, 4, 9),
        ],
    )


def _svc(
    puzzle: WordHuntPuzzleDTO | None = None,
    *,
    clock: list[datetime] | None = None,
) -> WordHuntService:
    p = puzzle if puzzle is not None else _puzzle()
    times = list(clock) if clock is not None else []
    if not times:
        times = [datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)]

    def _clock() -> datetime:
        if len(times) == 1:
            return times[0]
        return times.pop(0)

    return WordHuntService(
        FakeContextManager(),
        FakeGameSessionDAO(clock=_clock),
        FakeWordHuntPuzzleDAO([p]),
        FakeWordHuntFindDAO(),
        clock=_clock,
    )


async def _init(svc: WordHuntService) -> None:
    async with svc.ctx.session() as session:
        await svc.initialize(session)


@pytest.mark.asyncio
async def test_play_creates_session_with_hidden_words() -> None:
    svc = _svc()
    await _init(svc)

    out = await svc.play("emp001")

    assert out.session_status == GameSessionStatus.ACTIVE.value
    assert out.session_score == 0
    assert out.puzzle is not None
    assert out.puzzle.found_count == 0
    assert out.puzzle.total_words == 5
    assert out.puzzle.started_at is not None
    assert all(not clue.found for clue in out.puzzle.clues)
    assert all(clue.word is None for clue in out.puzzle.clues)


@pytest.mark.asyncio
async def test_play_is_idempotent() -> None:
    svc = _svc()
    await _init(svc)

    first = await svc.play("emp001")
    second = await svc.play("emp001")

    assert first.puzzle is not None
    assert second.puzzle is not None
    assert second.puzzle.found_count == first.puzzle.found_count
    assert second.puzzle.started_at == first.puzzle.started_at


@pytest.mark.asyncio
async def test_find_correct_word_increments_score() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")

    out = await svc.submit_find("emp001", 0, 0, 0, 5)

    assert out.matched is True
    assert out.word is not None
    assert out.word.word == "DEVOPS"
    assert out.session_score == 100
    assert out.session_status == GameSessionStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_find_invalid_trace_is_miss() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")

    out = await svc.submit_find("emp001", 0, 0, 1, 2)

    assert out.matched is False
    assert out.word is None
    assert out.session_score == 0


@pytest.mark.asyncio
async def test_find_already_found_word_is_miss() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await svc.submit_find("emp001", 0, 0, 0, 5)

    out = await svc.submit_find("emp001", 0, 0, 0, 5)

    assert out.matched is False
    assert out.session_score == 100


@pytest.mark.asyncio
async def test_find_final_word_auto_completes_session() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    complete_at = base + timedelta(milliseconds=300_000)
    svc = _svc(clock=[base, complete_at, complete_at])
    await _init(svc)
    await svc.play("emp001")

    await svc.submit_find("emp001", 0, 0, 0, 5)
    await svc.submit_find("emp001", 2, 0, 2, 5)
    await svc.submit_find("emp001", 4, 0, 4, 6)
    await svc.submit_find("emp001", 6, 0, 6, 5)
    out = await svc.submit_find("emp001", 0, 9, 4, 9)

    assert out.matched is True
    assert out.session_status == GameSessionStatus.COMPLETED.value
    assert out.session_score == 750
    assert out.result is not None
    assert out.result.found_count == 5
    assert out.result.base_score == 500
    assert out.result.time_bonus == 250
    assert out.result.time_elapsed_ms == 300_000


@pytest.mark.asyncio
async def test_submit_completes_active_session() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    submit_at = base + timedelta(milliseconds=300_000)
    svc = _svc(clock=[base, submit_at, submit_at])
    await _init(svc)
    await svc.play("emp001")
    await svc.submit_find("emp001", 0, 0, 0, 5)

    result = await svc.submit("emp001")

    assert result.score == 350
    assert result.base_score == 100
    assert result.time_bonus == 250
    assert result.time_elapsed_ms == 300_000
    assert result.found_count == 1


@pytest.mark.asyncio
async def test_submit_on_completed_session_raises() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await svc.submit("emp001")

    with pytest.raises(WordHuntSessionAlreadyCompletedException):
        await svc.submit("emp001")


@pytest.mark.asyncio
async def test_play_after_find_shows_found_clues() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await svc.submit_find("emp001", 0, 0, 0, 5)

    out = await svc.play("emp001")

    assert out.puzzle is not None
    assert out.puzzle.found_count == 1
    devops_clue = next(c for c in out.puzzle.clues if c.word_id == "w1")
    assert devops_clue.found is True
    assert devops_clue.word == "DEVOPS"
    assert devops_clue.coordinates is not None
    unsolved = next(c for c in out.puzzle.clues if c.word_id == "w2")
    assert unsolved.found is False
    assert unsolved.word is None


@pytest.mark.asyncio
async def test_auto_complete_at_zero_elapsed_earns_full_time_bonus() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    svc = _svc(clock=[base] * 10)
    await _init(svc)
    await svc.play("emp001")

    await svc.submit_find("emp001", 0, 0, 0, 5)
    await svc.submit_find("emp001", 2, 0, 2, 5)
    await svc.submit_find("emp001", 4, 0, 4, 6)
    await svc.submit_find("emp001", 6, 0, 6, 5)
    out = await svc.submit_find("emp001", 0, 9, 4, 9)

    assert out.result is not None
    assert out.result.time_bonus == 500
    assert out.session_score == 1000

    session = await svc.game_session_dao.get_by_player_and_game(
        FakeAsyncSession(),
        "emp001",
        "word_hunt",
    )
    assert session is not None
    assert session.score == 1000
