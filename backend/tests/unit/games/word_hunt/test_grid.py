"""Word Hunt grid unit tests."""

import pytest

from leap.games.word_hunt.grid import (
    direction_of,
    validate_seeded_word,
    validate_trace,
    walk_cells,
)

SAMPLE_GRID = [
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


def test_direction_of_horizontal() -> None:
    assert direction_of(0, 0, 0, 5) == (0, 1)


def test_direction_of_vertical() -> None:
    assert direction_of(0, 9, 4, 9) == (1, 0)


def test_direction_of_diagonal() -> None:
    assert direction_of(2, 0, 2, 5) == (0, 1)


def test_validate_trace_accepts_horizontal_word() -> None:
    assert validate_trace(10, 10, 0, 0, 0, 5) is True


def test_validate_trace_accepts_vertical_word() -> None:
    assert validate_trace(10, 10, 0, 9, 4, 9) is True


def test_validate_trace_rejects_out_of_bounds() -> None:
    assert validate_trace(10, 10, 0, 0, 0, 10) is False


def test_validate_trace_rejects_non_linear() -> None:
    assert validate_trace(10, 10, 0, 0, 1, 2) is False


def test_validate_trace_rejects_zero_length() -> None:
    assert validate_trace(10, 10, 0, 0, 0, 0) is False


def test_walk_cells_horizontal() -> None:
    assert walk_cells(SAMPLE_GRID, 0, 0, 0, 5) == "DEVOPS"


def test_walk_cells_vertical() -> None:
    assert walk_cells(SAMPLE_GRID, 0, 9, 4, 9) == "CLOUD"


def test_walk_cells_reverse_horizontal() -> None:
    assert walk_cells(SAMPLE_GRID, 0, 5, 0, 0) == "SPOVED"


def test_validate_seeded_word_accepts_matching_word() -> None:
    assert validate_seeded_word(SAMPLE_GRID, "DEVOPS", 0, 0, 0, 5) is True


def test_validate_seeded_word_rejects_mismatch() -> None:
    assert validate_seeded_word(SAMPLE_GRID, "DOCKER", 0, 0, 0, 5) is False


def test_validate_seeded_word_normalises_case() -> None:
    assert validate_seeded_word(SAMPLE_GRID, "devops", 0, 0, 0, 5) is True


def test_walk_cells_raises_on_invalid_trace() -> None:
    with pytest.raises(ValueError):
        walk_cells(SAMPLE_GRID, 0, 0, 1, 2)
