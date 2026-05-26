"""Unit tests for Four Pics scoring pure functions."""

import pytest

from leap.games.four_pics.scoring import (
    FOUR_PICS_BASE_SCORE,
    compute_question_score,
    compute_time_bonus,
)


class TestComputeTimeBonus:
    @pytest.mark.parametrize(
        ("elapsed_ms", "expected"),
        [
            (0, 50),
            (15_000, 25),
            (30_000, 0),
            (45_000, 0),
        ],
    )
    def test_time_bonus_decay_and_clamp(self, elapsed_ms: int, expected: int) -> None:
        assert compute_time_bonus(elapsed_ms) == expected


class TestComputeQuestionScore:
    def test_correct_at_mid_elapsed(self) -> None:
        score, time_bonus = compute_question_score(correct=True, elapsed_ms=15_000)
        assert score == 125
        assert time_bonus == 25

    def test_wrong_at_zero_elapsed(self) -> None:
        score, time_bonus = compute_question_score(correct=False, elapsed_ms=0)
        assert score == 0
        assert time_bonus == 0

    def test_correct_instant_tap(self) -> None:
        score, time_bonus = compute_question_score(correct=True, elapsed_ms=0)
        assert score == FOUR_PICS_BASE_SCORE + 50
        assert time_bonus == 50
