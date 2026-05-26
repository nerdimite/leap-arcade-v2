"""Word Hunt scoring — pure functions, no I/O."""

import math

WORD_HUNT_BASE_PER_WORD = 100
WORD_HUNT_TIME_BONUS_MAX = 500
WORD_HUNT_TIME_DECAY_MS = 600_000


def compute_base_score(found_count: int) -> int:
    """Return the running session score while active (no time bonus until termination)."""
    return found_count * WORD_HUNT_BASE_PER_WORD


def compute_time_bonus(elapsed_ms: int) -> int:
    """Linear decay from ``WORD_HUNT_TIME_BONUS_MAX`` to 0 over ``WORD_HUNT_TIME_DECAY_MS``."""
    if elapsed_ms < 0:
        elapsed_ms = 0
    ratio = 1.0 - (elapsed_ms / WORD_HUNT_TIME_DECAY_MS)
    return max(0, math.floor(WORD_HUNT_TIME_BONUS_MAX * ratio))


def compute_final_score(found_count: int, elapsed_ms: int) -> int:
    """Return base score plus time bonus at session termination."""
    return compute_base_score(found_count) + compute_time_bonus(elapsed_ms)
