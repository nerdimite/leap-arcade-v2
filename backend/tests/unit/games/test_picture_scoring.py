"""Unit tests for picture illustration scoring primitives."""

from datetime import datetime, timedelta

import pytz

from leap.config.constants import PICTURE_TIME_LIMIT_MS
from leap.games.picture.scoring import (
    compute_time_bonus,
    compute_total_score,
    normalize_answer,
    score_per_puzzle,
)


def test_picture_time_limit_constant() -> None:
    assert PICTURE_TIME_LIMIT_MS == 300_000


def test_normalize_answer_lowercase_and_trim() -> None:
    assert normalize_answer("  Hugging Face  ") == "hugging face"


def test_normalize_answer_removes_hyphens_and_dots() -> None:
    assert normalize_answer("Hugging-Face") == "huggingface"
    assert normalize_answer("Large.Language.Model") == "largelanguagemodel"


def test_normalize_answer_keeps_spaces_between_words_and_collapses_extra_whitespace() -> None:
    assert normalize_answer("Large   Language\n\rModel\t") == "large language model"


def test_normalize_answer_preserves_spaces_only_when_word_separators() -> None:
    assert normalize_answer("  n---l!!!p@@@") == "nlp"


def test_normalize_answer_handles_mixed_punctuation() -> None:
    assert (
        normalize_answer("-- Natural - Language (Processing) !!!") == "natural language processing"
    )


def test_score_per_puzzle_attempt_counts_map_to_pts() -> None:
    assert score_per_puzzle(1) == 200
    assert score_per_puzzle(2) == 150
    assert score_per_puzzle(3) == 100
    assert score_per_puzzle(4) == 50
    assert score_per_puzzle(5) == 50


def test_compute_time_bonus_full_budget_remaining() -> None:
    start = datetime(2020, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
    end = start
    assert compute_time_bonus(start, end, 300_000) == 300


def test_compute_time_bonus_zero_seconds_remaining() -> None:
    start = datetime(2020, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
    end = start + timedelta(milliseconds=300_000)
    assert compute_time_bonus(start, end, 300_000) == 0


def test_compute_time_bonus_over_budget_clamped_to_zero() -> None:
    start = datetime(2020, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
    end = start + timedelta(milliseconds=300_500)
    assert compute_time_bonus(start, end, 300_000) == 0


def test_compute_total_score_accuracy_plus_time_bonus() -> None:
    assert compute_total_score(500, 0) == 500
    assert compute_total_score(400, 30) == 430
