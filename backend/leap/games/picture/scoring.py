"""Pure scoring for Picture Illustration — no DB or I/O."""

import re
from datetime import datetime


def normalize_answer(value: str) -> str:
    """Normalise a free-text answer for comparison.

    Pipeline: lowercase → strip punctuation (non-alphanumeric, non-space) →
    collapse whitespace → trim.
    """
    lowered = value.lower()
    without_punct = re.sub(r"[^a-z0-9\s]+", "", lowered)
    collapsed = re.sub(r"\s+", " ", without_punct).strip()
    return collapsed


def score_per_puzzle(attempt_count: int) -> int:
    """Points for a correct resolution given how many submits it took (including the correct one)."""
    if attempt_count <= 0:
        return 0
    if attempt_count == 1:
        return 200
    if attempt_count == 2:
        return 150
    if attempt_count == 3:
        return 100
    return 50


def compute_time_bonus(started_at: datetime, ended_at: datetime, time_limit_ms: int) -> int:
    """1 pt per whole second remaining on the session budget; 0 if already over the limit."""
    elapsed_ms = int((ended_at - started_at).total_seconds() * 1000)
    remaining_ms = time_limit_ms - elapsed_ms
    return max(0, remaining_ms // 1000)


def compute_total_score(accuracy_score: int, time_bonus: int) -> int:
    """Combine accuracy (sum of earned puzzle points) with the session time bonus."""
    return max(0, accuracy_score + time_bonus)
