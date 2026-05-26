"""Pure scoring for Pinpoint — no DB or I/O."""

import math
from typing import List

PINPOINT_BASE_SCORES = (500, 400, 300, 200, 100)
PINPOINT_MAX_CLUES = 5
PINPOINT_TIME_BONUS_MAX_PTS = 100
PINPOINT_TIME_BONUS_DECAY_MS = 90_000


def normalize_answer(value: str) -> str:
    """Lowercase and trim surrounding whitespace."""
    return value.strip().lower()


def match_answer(guess: str, answer: str, aliases: List[str]) -> bool:
    """Return True when the guess matches the canonical answer or any alias."""
    normalized_guess = normalize_answer(guess)
    accepted = {normalize_answer(answer)}
    accepted.update(normalize_answer(alias) for alias in aliases)
    return normalized_guess in accepted


def base_score_for_clues(clues_revealed: int) -> int:
    """Points for a solve given how many clues were visible (1..5)."""
    if clues_revealed < 1 or clues_revealed > PINPOINT_MAX_CLUES:
        raise ValueError(f"clues_revealed must be 1..{PINPOINT_MAX_CLUES}, got {clues_revealed}")
    return PINPOINT_BASE_SCORES[clues_revealed - 1]


def compute_time_bonus(elapsed_ms: int) -> int:
    """Linear decay from ``PINPOINT_TIME_BONUS_MAX_PTS`` to 0 over ``PINPOINT_TIME_BONUS_DECAY_MS``."""
    if elapsed_ms < 0:
        elapsed_ms = 0
    ratio = 1.0 - (elapsed_ms / PINPOINT_TIME_BONUS_DECAY_MS)
    return max(0, math.floor(PINPOINT_TIME_BONUS_MAX_PTS * ratio))
