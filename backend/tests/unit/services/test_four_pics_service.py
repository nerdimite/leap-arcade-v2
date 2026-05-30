"""Four Pics service acceptance tests."""

from datetime import datetime, timedelta, timezone
from typing import List
from unittest.mock import patch

import pytest

from leap.games.four_pics.service import FourPicsService
from leap.service.exceptions import (
    InvalidQuestionIdException,
    QuestionAlreadyAnsweredException,
    SessionAlreadyCompletedException,
    SessionNotFoundException,
)
from leap.types.four_pics import FourPicsQuestionDTO
from leap.types.game import GameSessionStatus
from tests.fakes import (
    FakeContextManager,
    FakeFourPicsQuestionAttemptDAO,
    FakeFourPicsQuestionDAO,
    FakeGameSessionDAO,
)


def _questions() -> List[FourPicsQuestionDTO]:
    return [
        FourPicsQuestionDTO(
            id="fp-q1",
            image_paths=["/a/1.png", "/a/2.png", "/a/3.png", "/a/4.png"],
            odd_one_out_index=2,
        ),
        FourPicsQuestionDTO(
            id="fp-q2",
            image_paths=["/b/1.png", "/b/2.png", "/b/3.png", "/b/4.png"],
            odd_one_out_index=0,
        ),
        FourPicsQuestionDTO(
            id="fp-q3",
            image_paths=["/c/1.png", "/c/2.png", "/c/3.png", "/c/4.png"],
            odd_one_out_index=1,
        ),
    ]


def _svc(
    questions: List[FourPicsQuestionDTO],
    *,
    clock: List[datetime] | None = None,
) -> FourPicsService:
    times = list(clock) if clock is not None else []
    if not times:
        times = [datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)]

    def _clock() -> datetime:
        if len(times) == 1:
            return times[0]
        return times.pop(0)

    return FourPicsService(
        FakeContextManager(),
        FakeGameSessionDAO(),
        FakeFourPicsQuestionAttemptDAO(),
        FakeFourPicsQuestionDAO(questions),
        clock=_clock,
    )


async def _init(svc: FourPicsService) -> None:
    async with svc.ctx.session() as session:
        await svc.initialize(session)


_CHOICE_PATCH = patch(
    "leap.games.four_pics.service.random.choice",
    lambda seq: sorted(seq, key=lambda q: q.id)[0],
)


@pytest.mark.asyncio
async def test_play_creates_session_and_first_question() -> None:
    svc = _svc(_questions())
    await _init(svc)
    with _CHOICE_PATCH:
        out = await svc.play("emp001")

    assert out.session_status == GameSessionStatus.ACTIVE.value
    assert out.session_score == 0
    assert out.question is not None
    assert out.question.question_id == "fp-q1"
    assert out.question.question_number == 1
    assert out.question.total_questions == 3
    assert out.result is None


@pytest.mark.asyncio
async def test_play_is_idempotent_for_active_attempt() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    svc = _svc(_questions(), clock=[base, base, base])
    await _init(svc)
    with _CHOICE_PATCH:
        first = await svc.play("emp001")
        second = await svc.play("emp001")

    assert first.question is not None
    assert second.question is not None
    assert second.question.question_id == first.question.question_id
    assert second.question.started_at == first.question.started_at


@pytest.mark.asyncio
async def test_submit_correct_advances_with_score() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    answer_at = base + timedelta(seconds=15)
    svc = _svc(_questions(), clock=[base, answer_at, answer_at])
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")
        assert play.question is not None
        out = await svc.submit_answer("emp001", play.question.question_id, 2, 15_000)

    assert out.correct is True
    assert out.score == 125
    assert out.time_bonus == 25
    assert out.session_status == GameSessionStatus.ACTIVE.value
    assert out.session_score == 125
    assert out.question is not None
    assert out.question.question_id == "fp-q2"
    assert out.result is None


@pytest.mark.asyncio
async def test_submit_wrong_advances_with_zero_score() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    answer_at = base + timedelta(seconds=1)
    svc = _svc(_questions(), clock=[base, answer_at, answer_at])
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")
        assert play.question is not None
        out = await svc.submit_answer("emp001", play.question.question_id, 0, 500)

    assert out.correct is False
    assert out.score == 0
    assert out.time_bonus == 0
    assert out.question is not None
    assert out.question.question_id == "fp-q2"


@pytest.mark.asyncio
async def test_submit_final_question_completes_session() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    svc = _svc(_questions(), clock=[base] + [base + timedelta(seconds=1)] * 10)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")
        q1 = play.question
        assert q1 is not None
        await svc.submit_answer("emp001", q1.question_id, 2, 0)
        ans2 = await svc.submit_answer("emp001", "fp-q2", 0, 0)
        assert ans2.question is not None
        final = await svc.submit_answer("emp001", ans2.question.question_id, 1, 0)

    assert final.session_status == GameSessionStatus.COMPLETED.value
    assert final.question is None
    assert final.result is not None
    assert final.result.questions_not_reached == 0
    assert len(final.result.questions) == 3


@pytest.mark.asyncio
async def test_submit_clamps_client_time_ms() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    answer_at = base + timedelta(seconds=15)
    svc = _svc(_questions(), clock=[base, answer_at, answer_at])
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")

    assert play.question is not None
    out = await svc.submit_answer("emp001", play.question.question_id, 2, 999_999)

    assert out.correct is True
    assert out.time_bonus == 25


@pytest.mark.asyncio
async def test_submit_rejects_terminal_replay() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    svc = _svc(_questions(), clock=[base, base + timedelta(seconds=1), base + timedelta(seconds=2)])
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")

    assert play.question is not None
    qid = play.question.question_id
    await svc.submit_answer("emp001", qid, 2, 0)

    with pytest.raises(QuestionAlreadyAnsweredException):
        await svc.submit_answer("emp001", qid, 2, 0)


@pytest.mark.asyncio
async def test_submit_rejects_non_active_question_id() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    svc = _svc(_questions(), clock=[base])
    await _init(svc)
    with _CHOICE_PATCH:
        await svc.play("emp001")

    with pytest.raises(InvalidQuestionIdException):
        await svc.submit_answer("emp001", "fp-q2", 0, 0)


@pytest.mark.asyncio
async def test_abandon_active_session_closes_active_and_marks_not_reached() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    answer_at = base + timedelta(seconds=15)
    abandon_at = base + timedelta(minutes=1)
    svc = _svc(_questions(), clock=[base, answer_at, answer_at, abandon_at, abandon_at])
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")
        assert play.question is not None
        await svc.submit_answer("emp001", play.question.question_id, 2, 15_000)
        result = await svc.abandon("emp001")

    assert result.score == 125
    assert result.questions_correct == 1
    assert result.questions_wrong == 1
    assert result.questions_not_reached == 1
    assert len(result.questions) == 3

    by_id = {q.question_id: q for q in result.questions}
    assert by_id["fp-q1"].status == "correct"
    assert by_id["fp-q1"].score == 125
    assert by_id["fp-q2"].status == "wrong"
    assert by_id["fp-q2"].score == 0
    assert by_id["fp-q2"].time_bonus == 0
    assert by_id["fp-q3"].status == "not_reached"
    assert by_id["fp-q3"].score == 0

    async with svc.ctx.session() as session:
        game_session = await svc.game_session_dao.get_by_player_and_game(
            session, "emp001", "four_pics"
        )
        assert game_session is not None
        assert game_session.status == GameSessionStatus.ABANDONED
        assert game_session.score == 125

        attempts = await svc.attempt_dao.get_all_for_session(session, game_session.id)
        active = await svc.attempt_dao.get_active_for_session(session, game_session.id)
        assert active is None
        fp_q2 = next(a for a in attempts if a.question_id == "fp-q2")
        assert fp_q2.status == "wrong"
        assert fp_q2.selected_index is None
        assert fp_q2.completed_at == abandon_at


@pytest.mark.asyncio
async def test_abandon_completed_session_raises() -> None:
    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    svc = _svc(_questions(), clock=[base] + [base + timedelta(seconds=1)] * 10)
    await _init(svc)
    with _CHOICE_PATCH:
        play = await svc.play("emp001")
        assert play.question is not None
        await svc.submit_answer("emp001", play.question.question_id, 2, 0)
        await svc.submit_answer("emp001", "fp-q2", 0, 0)
        ans = await svc.submit_answer("emp001", "fp-q3", 1, 0)
        assert ans.session_status == GameSessionStatus.COMPLETED.value

    with pytest.raises(SessionAlreadyCompletedException):
        await svc.abandon("emp001")


@pytest.mark.asyncio
async def test_abandon_missing_session_raises() -> None:
    svc = _svc(_questions())
    await _init(svc)

    with pytest.raises(SessionNotFoundException):
        await svc.abandon("emp_no_session")
