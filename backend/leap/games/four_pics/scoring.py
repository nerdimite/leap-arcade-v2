"""Four Pics, One Lie — pure scoring functions."""

import math

FOUR_PICS_BASE_SCORE = 100
FOUR_PICS_TIME_BONUS_MAX = 50
FOUR_PICS_TIME_DECAY_MS = 30_000


def compute_time_bonus(elapsed_ms: int) -> int:
    """Linear decay from ``FOUR_PICS_TIME_BONUS_MAX`` to 0 over ``FOUR_PICS_TIME_DECAY_MS``."""
    if elapsed_ms < 0:
        elapsed_ms = 0
    ratio = 1.0 - (elapsed_ms / FOUR_PICS_TIME_DECAY_MS)
    return max(0, math.floor(FOUR_PICS_TIME_BONUS_MAX * ratio))


def compute_question_score(correct: bool, elapsed_ms: int) -> tuple[int, int]:
    """Return ``(score, time_bonus)`` for one answered question."""
    if not correct:
        return (0, 0)
    time_bonus = compute_time_bonus(elapsed_ms)
    return (FOUR_PICS_BASE_SCORE + time_bonus, time_bonus)


def clamp_elapsed_ms(client_time_ms: int, server_elapsed_ms: int) -> int:
    """Clamp client-reported elapsed time to the server-authoritative ceiling."""
    safe_client = max(0, client_time_ms)
    safe_server = max(0, server_elapsed_ms)
    return min(safe_client, safe_server)
