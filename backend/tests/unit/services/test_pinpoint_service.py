"""Pinpoint service happy-path acceptance tests."""

from datetime import datetime, timedelta, timezone
from typing import Iterable
from unittest.mock import patch

import pytest

from leap.games.pinpoint.service import PinpointService
from leap.service.exceptions import (
    InvalidPuzzleIdException,
    SessionAlreadyCompletedException,
    SessionNotFoundException,
)
from leap.types.game import GameSessionStatus
from leap.types.pinpoint import PinpointPuzzleDTO
from tests.fakes import (
    FakeAsyncSession,
    FakeContextManager,
    FakeGameSessionDAO,
    FakePinpointPuzzleAttemptDAO,
    FakePinpointPuzzleDAO,
)


def _puzzle(
    pid: str,
    *,
    answer: str,
    aliases: list[str],
    clues: tuple[str, str, str, str, str],
) -> PinpointPuzzleDTO:
    return PinpointPuzzleDTO(
        id=pid,
        answer=answer,
        answer_aliases=aliases,
        clue1=clues[0],
        clue2=clues[1],
        clue3=clues[2],
        clue4=clues[3],
        clue5=clues[4],
    )


@pytest.fixture()
def puzzles() -> list[PinpointPuzzleDTO]:
    return [
        _puzzle(
            "aaaaaaaa-aaaa-aaaa-aaaa-0000000000aa",
            answer="Alpha",
            aliases=["alpha"],
            clues=("a1", "a2", "a3", "a4", "a5"),
        ),
        _puzzle(
            "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb",
            answer="Beta",
            aliases=["beta"],
            clues=("b1", "b2", "b3", "b4", "b5"),
        ),
    ]


def _svc(
    puzzles: list[PinpointPuzzleDTO],
    *,
    clock: list[datetime] | None = None,
) -> PinpointService:
    times = list(clock) if clock is not None else []
    if not times:
        times = [datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)]

    def _clock() -> datetime:
        if len(times) == 1:
            return times[0]
        return times.pop(0)

    return PinpointService(
        FakeContextManager(),
        FakeGameSessionDAO(),
        FakePinpointPuzzleDAO(puzzles),
        FakePinpointPuzzleAttemptDAO(),
        clock=_clock,
    )


async def _init(svc: PinpointService) -> None:
    async with svc.ctx.session() as session:
        await svc.initialize(session)


_CHOICE_PATCH = patch(
    "leap.games.pinpoint.service.random.choice",
    lambda seq: sorted(seq, key=lambda p: p.id)[0],
)


@pytest.fixture(autouse=True)
def deterministic_choice() -> Iterable[None]:
    with _CHOICE_PATCH:
        yield


@pytest.mark.asyncio
async def test_play_creates_session_and_first_puzzle(puzzles: list[PinpointPuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)

    out = await svc.play("emp001")

    assert out.session_status == GameSessionStatus.ACTIVE.value
    assert out.session_score == 0
    assert out.puzzle is not None
    assert out.puzzle.puzzle_id == "aaaaaaaa-aaaa-aaaa-aaaa-0000000000aa"
    assert out.puzzle.clues_revealed == 1
    assert out.puzzle.clues == ["a1"]
    assert out.puzzle.status == "active"
    assert out.result is None


@pytest.mark.asyncio
async def test_play_is_idempotent_for_active_puzzle(puzzles: list[PinpointPuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)

    first = await svc.play("emp001")
    second = await svc.play("emp001")

    assert first.puzzle is not None
    assert second.puzzle is not None
    assert second.puzzle.puzzle_id == first.puzzle.puzzle_id
    assert second.puzzle.clues_revealed == first.puzzle.clues_revealed


@pytest.mark.asyncio
async def test_wrong_guess_reveals_next_clue(puzzles: list[PinpointPuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None

    out = await svc.submit_guess("emp001", play.puzzle.puzzle_id, "nope")

    assert out.correct is False
    assert out.puzzle.status == "active"
    assert out.puzzle.clues_revealed == 2
    assert out.puzzle.clues == ["a1", "a2"]
    assert out.session_status == GameSessionStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_correct_guess_marks_solved_and_next_play_advances(puzzles: list[PinpointPuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None
    puzzle_id = play.puzzle.puzzle_id

    solved = await svc.submit_guess("emp001", puzzle_id, "alpha")

    assert solved.correct is True
    assert solved.puzzle.status == "solved"
    assert solved.puzzle.score == 600
    assert solved.puzzle.time_bonus == 100
    assert solved.session_score == 600

    nxt = await svc.play("emp001")
    assert nxt.puzzle is not None
    assert nxt.puzzle.puzzle_id == "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb"
    assert nxt.puzzle.clues_revealed == 1


@pytest.mark.asyncio
async def test_fifth_wrong_guess_marks_failed_with_zero_score(puzzles: list[PinpointPuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None
    puzzle_id = play.puzzle.puzzle_id

    for _ in range(4):
        await svc.submit_guess("emp001", puzzle_id, "wrong")

    failed = await svc.submit_guess("emp001", puzzle_id, "still wrong")

    assert failed.correct is False
    assert failed.puzzle.status == "failed"
    assert failed.puzzle.score == 0
    assert failed.puzzle.clues_revealed == 5
    assert "answer" not in failed.puzzle.model_dump()


@pytest.mark.asyncio
async def test_submit_guess_rejects_non_active_puzzle_id(puzzles: list[PinpointPuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    await svc.play("emp001")

    with pytest.raises(InvalidPuzzleIdException):
        await svc.submit_guess("emp001", "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb", "beta")


@pytest.mark.asyncio
async def test_final_puzzle_completion_returns_result_and_persists_session_score(
    puzzles: list[PinpointPuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)

    play1 = await svc.play("emp001")
    assert play1.puzzle is not None
    await svc.submit_guess("emp001", play1.puzzle.puzzle_id, "alpha")

    play2 = await svc.play("emp001")
    assert play2.puzzle is not None
    finished = await svc.submit_guess("emp001", play2.puzzle.puzzle_id, "beta")

    assert finished.session_status == GameSessionStatus.COMPLETED.value
    assert finished.result is not None
    assert finished.result.score == 1200
    assert finished.result.puzzles_solved == 2
    assert finished.result.puzzles_failed == 0

    session = await svc.game_session_dao.get_by_player_and_game(FakeAsyncSession(), "emp001", "pinpoint")
    assert session is not None
    assert session.status == GameSessionStatus.COMPLETED
    assert session.score == 1200


@pytest.mark.asyncio
async def test_correct_guess_at_30s_elapsed_applies_time_bonus(puzzles: list[PinpointPuzzleDTO]) -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    answer_at = base + timedelta(milliseconds=30_000)
    svc = _svc(puzzles, clock=[base, answer_at, answer_at])
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None

    solved = await svc.submit_guess("emp001", play.puzzle.puzzle_id, "alpha")

    assert solved.correct is True
    assert solved.puzzle.time_bonus == 66
    assert solved.puzzle.score == 566
    assert solved.session_score == 566


@pytest.mark.asyncio
async def test_correct_guess_after_decay_still_earns_base_only(puzzles: list[PinpointPuzzleDTO]) -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    answer_at = base + timedelta(milliseconds=120_000)
    svc = _svc(puzzles, clock=[base, answer_at, answer_at])
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None

    solved = await svc.submit_guess("emp001", play.puzzle.puzzle_id, "alpha")

    assert solved.correct is True
    assert solved.puzzle.time_bonus == 0
    assert solved.puzzle.score == 500
    assert solved.session_score == 500


@pytest.mark.asyncio
async def test_failed_puzzle_has_null_time_bonus(puzzles: list[PinpointPuzzleDTO]) -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    svc = _svc(puzzles, clock=[base] + [base + timedelta(seconds=1)] * 10)
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None
    puzzle_id = play.puzzle.puzzle_id

    for _ in range(4):
        await svc.submit_guess("emp001", puzzle_id, "wrong")

    failed = await svc.submit_guess("emp001", puzzle_id, "still wrong")

    assert failed.puzzle.status == "failed"
    assert failed.puzzle.time_bonus is None
    assert failed.puzzle.score == 0
    assert failed.session_score == 0


@pytest.mark.asyncio
async def test_abandon_active_mid_puzzle_closes_attempt_and_marks_unattempted_not_reached(
    puzzles: list[PinpointPuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None
    puzzle_id = play.puzzle.puzzle_id

    result = await svc.abandon("emp001")

    assert result.score == 0
    assert result.puzzles_solved == 0
    assert result.puzzles_failed == 1
    assert result.puzzles_not_reached == 1

    session = await svc.game_session_dao.get_by_player_and_game(FakeAsyncSession(), "emp001", "pinpoint")
    assert session is not None
    assert session.status == GameSessionStatus.ABANDONED
    assert session.score == 0

    attempts = await svc.attempt_dao.get_for_session(FakeAsyncSession(), session.id)
    closed = next(a for a in attempts if a.puzzle_id == puzzle_id)
    assert closed.status == "failed"
    assert closed.score == 0
    assert closed.time_bonus is None

    not_reached = [p for p in result.puzzles if p.status == "not_reached"]
    assert len(not_reached) == 1
    assert not_reached[0].puzzle_id == "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb"
    assert not_reached[0].clues_used is None
    assert not_reached[0].score == 0
    assert not_reached[0].time_bonus == 0


@pytest.mark.asyncio
async def test_abandon_without_session_raises_not_found(puzzles: list[PinpointPuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)

    with pytest.raises(SessionNotFoundException):
        await svc.abandon("emp001")


@pytest.mark.asyncio
async def test_abandon_when_already_completed_raises(puzzles: list[PinpointPuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)

    play1 = await svc.play("emp001")
    assert play1.puzzle is not None
    await svc.submit_guess("emp001", play1.puzzle.puzzle_id, "alpha")

    play2 = await svc.play("emp001")
    assert play2.puzzle is not None
    await svc.submit_guess("emp001", play2.puzzle.puzzle_id, "beta")

    with pytest.raises(SessionAlreadyCompletedException):
        await svc.abandon("emp001")


@pytest.mark.asyncio
async def test_play_after_abandon_returns_result_not_new_puzzle(
    puzzles: list[PinpointPuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None

    await svc.abandon("emp001")

    replay = await svc.play("emp001")

    assert replay.session_status == GameSessionStatus.ABANDONED.value
    assert replay.puzzle is None
    assert replay.result is not None
    assert replay.result.puzzles_not_reached == 1
    assert replay.result.puzzles_failed == 1


@pytest.mark.asyncio
async def test_guess_after_abandon_raises_already_completed(
    puzzles: list[PinpointPuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    play = await svc.play("emp001")
    assert play.puzzle is not None
    puzzle_id = play.puzzle.puzzle_id

    await svc.abandon("emp001")

    with pytest.raises(SessionAlreadyCompletedException):
        await svc.submit_guess("emp001", puzzle_id, "alpha")
