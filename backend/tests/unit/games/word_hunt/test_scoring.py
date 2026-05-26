"""Word Hunt scoring unit tests."""

import pytest

from leap.games.word_hunt.scoring import (
    WORD_HUNT_BASE_PER_WORD,
    WORD_HUNT_TIME_BONUS_MAX,
    WORD_HUNT_TIME_DECAY_MS,
    compute_base_score,
    compute_final_score,
    compute_time_bonus,
)


def test_compute_base_score_zero_found() -> None:
    assert compute_base_score(0) == 0


def test_compute_base_score_one_found() -> None:
    assert compute_base_score(1) == 100


def test_compute_base_score_multiple_found() -> None:
    assert compute_base_score(5) == 500


def test_base_per_word_constant() -> None:
    assert WORD_HUNT_BASE_PER_WORD == 100


def test_time_bonus_constants() -> None:
    assert WORD_HUNT_TIME_BONUS_MAX == 500
    assert WORD_HUNT_TIME_DECAY_MS == 600_000


@pytest.mark.parametrize(
    ("elapsed_ms", "expected"),
    [
        (0, 500),
        (300_000, 250),
        (600_000, 0),
        (900_000, 0),
    ],
)
def test_compute_time_bonus_boundaries(elapsed_ms: int, expected: int) -> None:
    assert compute_time_bonus(elapsed_ms) == expected


def test_compute_time_bonus_never_negative() -> None:
    assert compute_time_bonus(-1) == 500


@pytest.mark.parametrize(
    ("found_count", "elapsed_ms", "expected"),
    [
        (0, 0, 500),
        (1, 0, 600),
        (5, 300_000, 750),
        (3, 600_000, 300),
    ],
)
def test_compute_final_score(found_count: int, elapsed_ms: int, expected: int) -> None:
    assert compute_final_score(found_count, elapsed_ms) == expected
