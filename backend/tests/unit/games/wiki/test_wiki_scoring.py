"""Unit tests for WikiScoring."""

import pytest

from leap.games.wiki.scoring import (
    aggregate_total_score,
    compute_puzzle_score,
    compute_steps_score,
    compute_time_bonus,
)


def test_steps_score_optimal_path_full_125() -> None:
    assert compute_steps_score(3, 3) == 125
    assert compute_steps_score(2, 3) == 125
    assert compute_steps_score(1, 3) == 125


def test_steps_score_small_over_optimal_light_penalty() -> None:
    # 4 vs optimal 3: 125 - 2*1^2 = 123
    assert compute_steps_score(4, 3) == 123
    # 5 vs 3: 125 - 2*4 = 117
    assert compute_steps_score(5, 3) == 117


def test_steps_score_hits_floor_at_12() -> None:
    # large excess drives toward floor
    assert compute_steps_score(100, 3) == 12
    # 10 vs optimal 3: excess 7 -> 125 - 2*49 = 27 (still above floor)
    assert compute_steps_score(10, 3) == 27


def test_time_bonus_max_at_zero_elapsed() -> None:
    assert compute_time_bonus(0, 180_000) == 75


def test_time_bonus_zero_at_or_after_limit() -> None:
    assert compute_time_bonus(180_000, 180_000) == 0
    assert compute_time_bonus(200_000, 180_000) == 0


def test_time_bonus_midway() -> None:
    # half elapsed => 75 * 0.5 floored = 37
    assert compute_time_bonus(90_000, 180_000) == 37


def test_puzzle_score_timeout_zero() -> None:
    assert (
        compute_puzzle_score(
            clicks_taken=3,
            optimal_click_count=3,
            time_ms=1,
            time_limit_ms=180_000,
            timed_out=True,
        )
        == 0
    )


def test_puzzle_score_full_run() -> None:
    score = compute_puzzle_score(
        clicks_taken=3,
        optimal_click_count=3,
        time_ms=0,
        time_limit_ms=180_000,
        timed_out=False,
    )
    assert score == 125 + 75


def test_aggregate_total_score_five_puzzles() -> None:
    assert aggregate_total_score([200, 200, 200, 200, 200]) == 1000


@pytest.mark.parametrize(
    ("steps", "expected"),
    [
        (4, 123),
        (6, 107),
    ],
)
def test_steps_score_examples(steps: int, expected: int) -> None:
    assert compute_steps_score(steps, 3) == expected
