"""Tests for Pinpoint pure scoring helpers."""

import pytest

from leap.games.pinpoint.scoring import (
    base_score_for_clues,
    compute_time_bonus,
    match_answer,
    normalize_answer,
)


class TestNormalizeAnswer:
    def test_strips_and_lowercases(self) -> None:
        assert normalize_answer("  Cloud Computing  ") == "cloud computing"

    def test_idempotent(self) -> None:
        once = normalize_answer("  LLM  ")
        assert normalize_answer(once) == once


class TestMatchAnswer:
    def test_matches_canonical(self) -> None:
        assert match_answer("Cloud Computing", "Cloud Computing", ["cloud"]) is True

    def test_matches_alias(self) -> None:
        assert match_answer("the cloud", "Cloud Computing", ["cloud", "the cloud"]) is True

    def test_rejects_wrong_guess(self) -> None:
        assert match_answer("blockchain", "Cloud Computing", ["cloud"]) is False

    def test_handles_whitespace_and_case(self) -> None:
        assert match_answer("  CLOUD  ", "Cloud Computing", ["cloud"]) is True

    def test_empty_alias_list_still_matches_canonical(self) -> None:
        assert match_answer("Blockchain", "Blockchain", []) is True
        assert match_answer("wrong", "Blockchain", []) is False


class TestBaseScoreForClues:
    @pytest.mark.parametrize(
        ("clues_revealed", "expected"),
        [(1, 500), (2, 400), (3, 300), (4, 200), (5, 100)],
    )
    def test_returns_expected_score(self, clues_revealed: int, expected: int) -> None:
        assert base_score_for_clues(clues_revealed) == expected

    def test_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            base_score_for_clues(0)
        with pytest.raises(ValueError):
            base_score_for_clues(6)


class TestComputeTimeBonus:
    @pytest.mark.parametrize(
        ("elapsed_ms", "expected"),
        [(0, 100), (45_000, 50), (90_000, 0), (120_000, 0)],
    )
    def test_decay_and_clamp(self, elapsed_ms: int, expected: int) -> None:
        assert compute_time_bonus(elapsed_ms) == expected
