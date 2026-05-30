"""Picture Illustration service acceptance tests."""

import uuid
from datetime import timedelta
from typing import Iterable
from unittest.mock import patch

import pytest

from leap.config.constants import PICTURE_TIME_LIMIT_MS
from leap.core.common import time as leap_time
from leap.games.picture.scoring import compute_time_bonus as real_compute_time_bonus
from leap.games.picture.service import PictureService
from leap.service.exceptions import (
    AlreadyResolvedException,
    SessionAlreadyCompletedException,
    SessionNotFoundException,
)
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.picture import PicturePuzzleDTO
from tests.fakes import (
    FakeAsyncSession,
    FakeContextManager,
    FakeGameSessionDAO,
    FakePicturePuzzleAttemptDAO,
    FakePicturePuzzleDAO,
)


def _svc(puzzles: list[PicturePuzzleDTO]) -> PictureService:
    return PictureService(
        FakeContextManager(),
        FakeGameSessionDAO(),
        FakePicturePuzzleDAO(puzzles),
        FakePicturePuzzleAttemptDAO(),
    )


@pytest.fixture()
def puzzles() -> list[PicturePuzzleDTO]:
    return [
        PicturePuzzleDTO(
            id="aaaaaaaa-aaaa-aaaa-aaaa-0000000000aa",
            image_filename="p_a.png",
            canonical_answer="Alpha",
            accepted_answers=["alpha"],
        ),
        PicturePuzzleDTO(
            id="bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb",
            image_filename="p_b.png",
            canonical_answer="Beta",
            accepted_answers=["beta"],
        ),
    ]


async def _init(svc: PictureService) -> None:
    async with svc.ctx.session() as session:
        await svc.initialize(session)


_CHOICE_PATCH = patch(
    "leap.games.picture.service.random.choice",
    lambda seq: sorted(seq, key=lambda p: p.id)[0],
)


@pytest.fixture(autouse=True)
def zero_picture_time_bonus() -> Iterable[None]:
    """Sub-3 time bonus — isolate Sub-2 tests to accuracy-only totals."""
    with patch("leap.games.picture.service.compute_time_bonus", lambda *_a, **_k: 0):
        yield


@pytest.mark.asyncio
async def test_play_creates_active_session_first_puzzle(puzzles: list[PicturePuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        out = await svc.play("emp001")

    assert out.status == GameSessionStatus.ACTIVE.value
    assert out.game_session_id is not None
    assert out.puzzles_answered == 0
    assert out.puzzles_total == 2
    assert out.puzzle is not None
    assert out.puzzle.id == "aaaaaaaa-aaaa-aaaa-aaaa-0000000000aa"


@pytest.mark.asyncio
async def test_submit_wrong_records_attempt_and_keeps_same_puzzle(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")

    gid = play.game_session_id
    assert gid is not None
    puzzle_id = play.puzzle.id if play.puzzle is not None else ""

    wrong = await svc.submit_answer("emp001", puzzle_id, "garbage")

    assert wrong.correct is False
    assert wrong.score_earned == 0
    assert wrong.next_puzzle is None
    assert wrong.puzzles_solved == 0
    assert wrong.puzzles_remaining == 2

    attempts = svc.attempt_dao._attempts  # noqa: SLF001
    assert len(attempts) == 1
    assert attempts[0].correct is False


@pytest.mark.asyncio
async def test_submit_correct_second_attempt_scores_150_and_advances(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")

    puzzle_id_one = play.puzzle.id if play.puzzle is not None else ""

    await svc.submit_answer("emp001", puzzle_id_one, "nope")
    second = await svc.submit_answer("emp001", puzzle_id_one, "alpha")

    assert second.correct is True
    assert second.score_earned == 150
    assert second.puzzles_solved == 1
    assert second.puzzles_remaining == 1
    assert second.next_puzzle is not None
    assert second.next_puzzle.id == "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb"
    assert second.current_score == 150


@pytest.mark.asyncio
async def test_play_active_includes_timer_fields(puzzles: list[PicturePuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        out = await svc.play("emp001")

    assert out.session_started_at is not None
    assert out.time_limit_ms == PICTURE_TIME_LIMIT_MS


@pytest.mark.asyncio
async def test_play_expired_active_session_completes_with_zero_time_bonus(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    sid = str(uuid.uuid4())
    old_started = leap_time.utc_now() - timedelta(seconds=PICTURE_TIME_LIMIT_MS // 1000 + 5)
    session_row = GameSessionDTO(
        id=sid,
        player_id="emp_expired_play",
        game_id="picture",
        status=GameSessionStatus.ACTIVE,
        score=None,
        started_at=old_started,
        completed_at=None,
    )
    svc = PictureService(
        FakeContextManager(),
        FakeGameSessionDAO(sessions=[session_row]),
        FakePicturePuzzleDAO(puzzles),
        FakePicturePuzzleAttemptDAO(),
    )
    await _init(svc)
    out = await svc.play("emp_expired_play")

    assert out.status == GameSessionStatus.COMPLETED.value
    assert out.result is not None
    assert out.result.time_bonus == 0
    assert out.result.score == 0
    assert out.result.accuracy_score == 0


@pytest.mark.asyncio
async def test_last_correct_completes_session_adds_time_bonus(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")

    first_id = play.puzzle.id if play.puzzle is not None else ""
    await svc.submit_answer("emp001", first_id, "alpha")

    sess_after = await svc.game_session_dao.get_by_player_and_game(
        FakeAsyncSession(), "emp001", "picture"
    )
    assert sess_after is not None
    bonus_anchor = sess_after.started_at + timedelta(seconds=50)
    time_bonus = (PICTURE_TIME_LIMIT_MS - 50_000) // 1000

    with (
        _CHOICE_PATCH,
        patch("leap.games.picture.service.utc_now", return_value=bonus_anchor),
        patch("leap.games.picture.service.compute_time_bonus", real_compute_time_bonus),
    ):
        finishing = await svc.submit_answer(
            "emp001",
            "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb",
            "beta",
        )

    assert finishing.result is not None
    assert finishing.result.accuracy_score == 400
    assert finishing.result.time_bonus == time_bonus
    assert finishing.result.score == 400 + time_bonus
    assert finishing.next_puzzle is None

    sess = await svc.game_session_dao.get_by_player_and_game(
        FakeAsyncSession(), "emp001", "picture"
    )

    assert sess is not None
    assert sess.status == GameSessionStatus.COMPLETED
    assert sess.score == 400 + time_bonus


@pytest.mark.asyncio
async def test_submit_after_time_limit_closes_with_zero_time_bonus(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    sid = str(uuid.uuid4())
    old_started = leap_time.utc_now() - timedelta(seconds=PICTURE_TIME_LIMIT_MS // 1000 + 5)
    session_row = GameSessionDTO(
        id=sid,
        player_id="emp_late",
        game_id="picture",
        status=GameSessionStatus.ACTIVE,
        score=None,
        started_at=old_started,
        completed_at=None,
    )
    svc = PictureService(
        FakeContextManager(),
        FakeGameSessionDAO(sessions=[session_row]),
        FakePicturePuzzleDAO(puzzles),
        FakePicturePuzzleAttemptDAO(),
    )
    await _init(svc)
    puzzle_id = puzzles[0].id
    out = await svc.submit_answer("emp_late", puzzle_id, "alpha")

    assert out.result is not None
    assert out.result.time_bonus == 0
    assert out.correct is True
    assert out.result.accuracy_score == 200
    assert out.result.score == 200

    sess = await svc.game_session_dao.get_by_player_and_game(
        FakeAsyncSession(), "emp_late", "picture"
    )
    assert sess is not None
    assert sess.status == GameSessionStatus.COMPLETED


@pytest.mark.asyncio
async def test_abandon_active_session_returns_result(puzzles: list[PicturePuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        await svc.play("emp_abandon")

    res = await svc.abandon("emp_abandon")

    assert res.time_bonus == 0
    assert res.accuracy_score == 0
    assert res.score == 0
    not_reached = [p for p in res.puzzles if p.status == "not_reached"]
    assert len(not_reached) == 2

    sess = await svc.game_session_dao.get_by_player_and_game(
        FakeAsyncSession(), "emp_abandon", "picture"
    )
    assert sess is not None
    assert sess.status == GameSessionStatus.COMPLETED


@pytest.mark.asyncio
async def test_abandon_completed_session_raises(puzzles: list[PicturePuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp_abandon2")

    gid = play.game_session_id
    first_id = play.puzzle.id if play.puzzle is not None else ""
    await svc.submit_answer("emp_abandon2", first_id, "alpha")
    with (
        _CHOICE_PATCH,
        patch("leap.games.picture.service.utc_now", return_value=leap_time.utc_now()),
    ):
        await svc.submit_answer("emp_abandon2", "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb", "beta")

    with pytest.raises(SessionAlreadyCompletedException) as exc:
        await svc.abandon("emp_abandon2")

    assert exc.value.details["game_session_id"] == gid


@pytest.mark.asyncio
async def test_abandon_missing_session_raises() -> None:
    svc = _svc([])
    await _init(svc)
    with pytest.raises(SessionNotFoundException):
        await svc.abandon("emp_no_sess")


@pytest.mark.asyncio
async def test_submit_after_resolved_raises_conflict(puzzles: list[PicturePuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp002")

    first_id = play.puzzle.id if play.puzzle is not None else ""
    await svc.submit_answer("emp002", first_id, "alpha")

    with pytest.raises(AlreadyResolvedException):
        await svc.submit_answer("emp002", first_id, "alpha again")


@pytest.mark.asyncio
async def test_skip_first_puzzle_advances_to_next(puzzles: list[PicturePuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp010")

    first_id = play.puzzle.id if play.puzzle is not None else ""
    out = await svc.submit_answer("emp010", first_id, None)

    assert out.correct is False
    assert out.score_earned == 0
    assert out.current_score == 0
    assert out.next_puzzle is not None
    assert out.next_puzzle.id == "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb"
    assert out.result is None

    attempts = svc.attempt_dao._attempts  # noqa: SLF001
    assert len(attempts) == 1
    assert attempts[0].skipped is True
    assert attempts[0].correct is False
    assert attempts[0].submitted_answer is None


@pytest.mark.asyncio
async def test_skip_final_puzzle_completes_and_returns_inline_result(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp011")

    first_id = play.puzzle.id if play.puzzle is not None else ""
    await svc.submit_answer("emp011", first_id, "alpha")

    second_id = "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb"
    out = await svc.submit_answer("emp011", second_id, None)

    assert out.result is not None
    assert out.result.score == 200
    assert out.next_puzzle is None
    assert out.correct is False
    assert out.score_earned == 0
    assert out.current_score == 200

    skipped_line = next(p for p in out.result.puzzles if p.puzzle_id == second_id)
    assert skipped_line.status == "skipped"
    assert skipped_line.score_earned == 0

    sess = await svc.game_session_dao.get_by_player_and_game(
        FakeAsyncSession(), "emp011", "picture"
    )
    assert sess is not None
    assert sess.status == GameSessionStatus.COMPLETED
    assert sess.score == 200


@pytest.mark.asyncio
async def test_whitespace_submitted_answer_is_not_skip_normally_wrong_attempt(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp012")

    pid = play.puzzle.id if play.puzzle is not None else ""
    out = await svc.submit_answer("emp012", pid, "   \t")

    assert out.correct is False
    assert out.next_puzzle is None
    assert out.score_earned == 0

    attempts = svc.attempt_dao._attempts  # noqa: SLF001
    assert attempts[0].skipped is False
    assert attempts[0].correct is False
    assert attempts[0].submitted_answer == "   \t"


@pytest.mark.asyncio
async def test_empty_string_submitted_answer_is_not_skip_normally_wrong_attempt(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp012b")

    pid = play.puzzle.id if play.puzzle is not None else ""
    out = await svc.submit_answer("emp012b", pid, "")

    assert out.correct is False
    assert out.next_puzzle is None

    attempts = svc.attempt_dao._attempts  # noqa: SLF001
    assert attempts[0].skipped is False
    assert attempts[0].correct is False
    assert attempts[0].submitted_answer == ""


@pytest.mark.asyncio
async def test_skip_after_skip_raises_conflict(puzzles: list[PicturePuzzleDTO]) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp013")

    first_id = play.puzzle.id if play.puzzle is not None else ""
    await svc.submit_answer("emp013", first_id, None)

    with pytest.raises(AlreadyResolvedException):
        await svc.submit_answer("emp013", first_id, None)


@pytest.mark.asyncio
async def test_resume_play_excludes_skipped_puzzle_from_pool(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp014")

    skipped_id = play.puzzle.id if play.puzzle is not None else ""
    await svc.submit_answer("emp014", skipped_id, None)

    with _CHOICE_PATCH:
        resumed = await svc.play("emp014")

    assert resumed.puzzle is not None
    assert resumed.puzzle.id != skipped_id


@pytest.mark.asyncio
async def test_submit_answer_after_completed_session_via_skips_raises(
    puzzles: list[PicturePuzzleDTO],
) -> None:
    svc = _svc(puzzles)
    await _init(svc)
    with _CHOICE_PATCH:
        await svc.play("emp015")

    await svc.submit_answer("emp015", "aaaaaaaa-aaaa-aaaa-aaaa-0000000000aa", None)
    await svc.submit_answer(
        "emp015",
        "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb",
        None,
    )

    with pytest.raises(SessionAlreadyCompletedException):
        await svc.submit_answer(
            "emp015",
            "bbbbbbbb-bbbb-bbbb-bbbb-0000000000bb",
            None,
        )
