"""Crossword scoring — pure functions, no I/O."""

import math

CROSSWORD_BASE_PER_ENTRY = 100
CROSSWORD_TIME_BONUS_MAX = 500
CROSSWORD_TIME_DECAY_MS = 600_000


def compute_base_score(solved_count: int) -> int:
    """Return the running session score while active (no time bonus until termination)."""
    return solved_count * CROSSWORD_BASE_PER_ENTRY


def compute_time_bonus(elapsed_ms: int) -> int:
    """Linear decay from ``CROSSWORD_TIME_BONUS_MAX`` to 0 over ``CROSSWORD_TIME_DECAY_MS``."""
    if elapsed_ms < 0:
        elapsed_ms = 0
    ratio = 1.0 - (elapsed_ms / CROSSWORD_TIME_DECAY_MS)
    return max(0, math.floor(CROSSWORD_TIME_BONUS_MAX * ratio))


def compute_final_score(solved_count: int, elapsed_ms: int) -> int:
    """Return base score plus time bonus at session termination."""
    return compute_base_score(solved_count) + compute_time_bonus(elapsed_ms)
