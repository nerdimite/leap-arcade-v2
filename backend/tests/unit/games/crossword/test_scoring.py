from leap.games.crossword.scoring import (
    compute_base_score,
    compute_time_bonus,
    compute_final_score,
)


def test_compute_base_score() -> None:
    assert compute_base_score(0) == 0
    assert compute_base_score(1) == 100
    assert compute_base_score(10) == 1000


def test_compute_time_bonus() -> None:
    # 0ms elapsed -> max bonus (500)
    assert compute_time_bonus(0) == 500
    # 300_000ms elapsed -> half bonus (250)
    assert compute_time_bonus(300_000) == 250
    # 600_000ms elapsed -> 0
    assert compute_time_bonus(600_000) == 0
    # >600_000ms elapsed -> 0 (clamped)
    assert compute_time_bonus(900_000) == 0
    # negative elapsed -> max bonus (500)
    assert compute_time_bonus(-1000) == 500


def test_compute_final_score() -> None:
    assert compute_final_score(5, 300_000) == 500 + 250
    assert compute_final_score(0, 0) == 500
    assert compute_final_score(10, 600_000) == 1000
