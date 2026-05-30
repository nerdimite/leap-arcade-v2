"""Crossword service happy-path acceptance tests."""

from datetime import datetime, timedelta, timezone

import pytest

from leap.games.crossword.service import CrosswordService
from leap.service.exceptions import CrosswordSessionAlreadyCompletedException
from leap.types.crossword import CrosswordCheckInput, CrosswordEntryDTO, CrosswordPuzzleDTO
from leap.types.game import GameSessionStatus
from tests.fakes import (
    FakeAsyncSession,
    FakeContextManager,
    FakeCrosswordPuzzleDAO,
    FakeCrosswordSolveDAO,
    FakeGameSessionDAO,
)

PUZZLE_ID = "22222222-2222-2222-2222-222222222222"

GRID = [
    ["M", "I", "C", "R", "O"],
    ["O", None, None, None, "S"],
    ["C", None, None, None, "E"],
    ["K", "U", "B", "E", "R"],
]

ENTRIES = [
    CrosswordEntryDTO(
        id="e1",
        puzzle_id=PUZZLE_ID,
        number=1,
        direction="across",
        start_row=0,
        start_col=0,
        answer="MICRO",
        clue="clue micro",
    ),
    CrosswordEntryDTO(
        id="e2",
        puzzle_id=PUZZLE_ID,
        number=1,
        direction="down",
        start_row=0,
        start_col=0,
        answer="MOCK",
        clue="clue mock",
    ),
    CrosswordEntryDTO(
        id="e3",
        puzzle_id=PUZZLE_ID,
        number=4,
        direction="across",
        start_row=3,
        start_col=0,
        answer="KUBER",
        clue="clue kuber",
    ),
    CrosswordEntryDTO(
        id="e4",
        puzzle_id=PUZZLE_ID,
        number=2,
        direction="down",
        start_row=0,
        start_col=4,
        answer="OSER",
        clue="clue oser",
    ),
]


def _puzzle() -> CrosswordPuzzleDTO:
    return CrosswordPuzzleDTO(
        id=PUZZLE_ID,
        rows=5,
        cols=5,
        grid=GRID,
        entries=ENTRIES,
    )


def _svc(
    puzzle: CrosswordPuzzleDTO | None = None,
    *,
    clock: list[datetime] | None = None,
) -> CrosswordService:
    p = puzzle if puzzle is not None else _puzzle()
    times = list(clock) if clock is not None else []
    if not times:
        times = [datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)]

    def _clock() -> datetime:
        if len(times) == 1:
            return times[0]
        return times.pop(0)

    return CrosswordService(
        FakeContextManager(),
        FakeGameSessionDAO(clock=_clock),
        FakeCrosswordPuzzleDAO([p]),
        FakeCrosswordSolveDAO(),
        clock=_clock,
    )


async def _init(svc: CrosswordService) -> None:
    async with svc.ctx.session() as session:
        await svc.initialize(session)


def _check(svc: CrosswordService, player_id: str, entry_id: str, letters: str):
    return svc.submit_check(
        player_id,
        CrosswordCheckInput(entry_id=entry_id, letters=letters),
    )


def _unsolved_answers(payload_json: str) -> int:
    answers = {"MICRO", "MOCK", "KUBER", "OSER"}
    return sum(1 for answer in answers if answer in payload_json)


@pytest.mark.asyncio
async def test_play_creates_session_with_no_letters_or_answers() -> None:
    svc = _svc()
    await _init(svc)

    out = await svc.play("emp001")

    assert out.session_status == GameSessionStatus.ACTIVE.value
    assert out.session_score == 0
    assert out.puzzle is not None
    assert out.puzzle.solved_count == 0
    assert out.puzzle.total_entries == 4
    assert out.puzzle.started_at is not None
    assert all(not clue.solved for clue in out.puzzle.clues)
    assert all(clue.answer is None for clue in out.puzzle.clues)
    payload = out.model_dump_json()
    assert _unsolved_answers(payload) == 0
    assert all(
        cell is None or cell.letter is None
        for row in out.puzzle.cells
        for cell in row
    )


@pytest.mark.asyncio
async def test_play_resumes_with_solved_entries_hydrated() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await _check(svc, "emp001", "e1", "MICRO")

    out = await svc.play("emp001")

    assert out.puzzle is not None
    assert out.puzzle.solved_count == 1
    assert out.session_score == 100
    solved = next(c for c in out.puzzle.clues if c.entry_id == "e1")
    assert solved.solved is True
    assert solved.answer == "MICRO"
    unsolved = next(c for c in out.puzzle.clues if c.entry_id == "e2")
    assert unsolved.solved is False
    assert unsolved.answer is None


@pytest.mark.asyncio
async def test_submit_check_correct_entry_scores() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")

    out = await _check(svc, "emp001", "e3", "KUBER")

    assert out.correct is True
    assert out.entry is not None
    assert out.entry.answer == "KUBER"
    assert out.session_score == 100
    assert out.session_status == GameSessionStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_submit_check_wrong_letters_is_miss() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")

    out = await _check(svc, "emp001", "e3", "WRONG")

    assert out.correct is False
    assert out.session_score == 0


@pytest.mark.asyncio
async def test_submit_check_wrong_length_is_miss() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")

    out = await _check(svc, "emp001", "e3", "KU")

    assert out.correct is False


@pytest.mark.asyncio
async def test_submit_check_unknown_entry_id_is_miss() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")

    out = await _check(svc, "emp001", "missing", "MICRO")

    assert out.correct is False


@pytest.mark.asyncio
async def test_submit_check_already_solved_is_miss() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await _check(svc, "emp001", "e1", "MICRO")

    out = await _check(svc, "emp001", "e1", "MICRO")

    assert out.correct is False
    assert out.session_score == 100


@pytest.mark.asyncio
async def test_submit_check_final_entry_auto_completes() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await _check(svc, "emp001", "e1", "MICRO")
    await _check(svc, "emp001", "e2", "MOCK")
    await _check(svc, "emp001", "e3", "KUBER")
    out = await _check(svc, "emp001", "e4", "OSER")

    assert out.correct is True
    assert out.session_status == GameSessionStatus.COMPLETED.value
    assert out.session_score == 900
    assert out.result is not None
    assert out.result.solved_count == 4
    assert out.result.base_score == 400
    assert out.result.time_bonus == 500
    assert out.result.time_elapsed_ms == 0


@pytest.mark.asyncio
async def test_submit_completes_active_session() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await _check(svc, "emp001", "e1", "MICRO")

    result = await svc.submit("emp001")

    assert result.score == 600
    assert result.base_score == 100
    assert result.time_bonus == 500
    assert result.time_elapsed_ms == 0
    assert result.solved_count == 1


@pytest.mark.asyncio
async def test_submit_on_completed_session_raises() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await svc.submit("emp001")

    with pytest.raises(CrosswordSessionAlreadyCompletedException):
        await svc.submit("emp001")


@pytest.mark.asyncio
async def test_play_on_completed_session_returns_result() -> None:
    svc = _svc()
    await _init(svc)
    await svc.play("emp001")
    await svc.submit("emp001")

    out = await svc.play("emp001")

    assert out.puzzle is None
    assert out.result is not None
    assert out.result.base_score == 0
    assert out.result.time_bonus == 500
    assert out.session_status == GameSessionStatus.COMPLETED.value


@pytest.mark.asyncio
async def test_play_on_completed_session_uses_completed_at_for_elapsed() -> None:
    """Replay after completion must not recompute elapsed from wall clock."""
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    submit_at = base + timedelta(milliseconds=300_000)
    replay_at = base + timedelta(milliseconds=900_000)
    svc = _svc(clock=[base, submit_at, submit_at, replay_at])
    await _init(svc)
    await svc.play("emp001")
    await svc.submit("emp001")

    out = await svc.play("emp001")

    assert out.result is not None
    assert out.result.time_elapsed_ms == 300_000


@pytest.mark.asyncio
async def test_play_is_idempotent() -> None:
    svc = _svc()
    await _init(svc)

    first = await svc.play("emp001")
    second = await svc.play("emp001")

    assert first.puzzle is not None
    assert second.puzzle is not None
    assert second.puzzle.started_at == first.puzzle.started_at


@pytest.mark.asyncio
async def test_submit_check_final_entry_auto_completes_with_time_bonus() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    complete_at = base + timedelta(milliseconds=300_000)
    svc = _svc(clock=[base, complete_at, complete_at])
    await _init(svc)
    await svc.play("emp001")

    await _check(svc, "emp001", "e1", "MICRO")
    await _check(svc, "emp001", "e2", "MOCK")
    await _check(svc, "emp001", "e3", "KUBER")
    out = await _check(svc, "emp001", "e4", "OSER")

    assert out.session_status == GameSessionStatus.COMPLETED.value
    assert out.session_score == 650
    assert out.result is not None
    assert out.result.base_score == 400
    assert out.result.time_bonus == 250
    assert out.result.time_elapsed_ms == 300_000


@pytest.mark.asyncio
async def test_submit_completes_with_time_bonus() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    submit_at = base + timedelta(milliseconds=300_000)
    svc = _svc(clock=[base, submit_at, submit_at])
    await _init(svc)
    await svc.play("emp001")
    await _check(svc, "emp001", "e1", "MICRO")

    result = await svc.submit("emp001")

    assert result.score == 350
    assert result.base_score == 100
    assert result.time_bonus == 250
    assert result.time_elapsed_ms == 300_000

    session = await svc.game_session_dao.get_by_player_and_game(
        FakeAsyncSession(),
        "emp001",
        "crossword",
    )
    assert session is not None
    assert session.score == 350
