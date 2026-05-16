"""Tests for ``compute_rapid_fire_score``."""

from datetime import datetime, timezone
from typing import Optional

import pytest

from leap.games.rapid_fire.scoring import compute_rapid_fire_score
from leap.types.rapid_fire import RapidFireAnswerDTO, RapidFireQuestionDTO


def _q(qid: str, limit_ms: int = 15000) -> RapidFireQuestionDTO:
    return RapidFireQuestionDTO(
        id=qid,
        question="x",
        options=["a", "b", "c", "d"],
        correct_option_index=1,
        time_limit_ms=limit_ms,
    )


def _answered(
    *,
    qid: str,
    correct: bool,
    skipped: bool,
    time_ms: int,
    selected: Optional[int],
) -> RapidFireAnswerDTO:
    return RapidFireAnswerDTO(
        id="a1",
        game_session_id="s1",
        question_id=qid,
        correct=correct,
        skipped=skipped,
        selected_option=selected,
        time_ms=time_ms,
        answered_at=datetime.now(tz=timezone.utc),
    )


class TestComputeRapidFireScore:
    def test_correct_at_time_floor_yields_full_points(self) -> None:
        """Anti-cheat floor 500 ms still scores as fastest (100 points at 15000 limit)."""
        questions = {"q1": _q("q1")}
        answers = [
            _answered(qid="q1", correct=True, skipped=False, time_ms=500, selected=1),
        ]
        assert compute_rapid_fire_score(answers, questions) == 100

    def test_correct_at_full_time_limit_yields_floor_points(self) -> None:
        questions = {"q1": _q("q1", limit_ms=15000)}
        answers = [
            _answered(qid="q1", correct=True, skipped=False, time_ms=15000, selected=1),
        ]
        assert compute_rapid_fire_score(answers, questions) == 50

    def test_correct_at_half_duration_yields_mid_points(self) -> None:
        questions = {"q1": _q("q1", limit_ms=15000)}
        answers = [
            _answered(qid="q1", correct=True, skipped=False, time_ms=7750, selected=1),
        ]
        assert compute_rapid_fire_score(answers, questions) == 75

    def test_wrong_answer_zero(self) -> None:
        questions = {"q1": _q("q1")}
        answers = [
            _answered(qid="q1", correct=False, skipped=False, time_ms=500, selected=2),
        ]
        assert compute_rapid_fire_score(answers, questions) == 0

    def test_skipped_zero(self) -> None:
        questions = {"q1": _q("q1")}
        answers = [
            _answered(qid="q1", correct=False, skipped=True, time_ms=500, selected=None),
        ]
        assert compute_rapid_fire_score(answers, questions) == 0

    def test_fifteen_perfect_scores_to_1500(self) -> None:
        questions = {f"q{i}": _q(f"q{i}") for i in range(15)}
        answers = [
            _answered(qid=f"q{i}", correct=True, skipped=False, time_ms=500, selected=1)
            for i in range(15)
        ]
        assert compute_rapid_fire_score(answers, questions) == 1500

    def test_empty_answers_returns_zero(self) -> None:
        questions = {"q1": _q("q1")}
        assert compute_rapid_fire_score([], questions) == 0

    def test_time_ms_zero_clamped_to_floor_scoring(self) -> None:
        questions = {"q1": _q("q1")}
        answers = [
            _answered(qid="q1", correct=True, skipped=False, time_ms=0, selected=1),
        ]
        assert compute_rapid_fire_score(answers, questions) == 100

    def test_keyerror_on_unknown_question_id(self) -> None:
        questions = {"q1": _q("q1")}
        answers = [
            _answered(qid="missing", correct=True, skipped=False, time_ms=500, selected=1),
        ]
        with pytest.raises(KeyError):
            compute_rapid_fire_score(answers, questions)
