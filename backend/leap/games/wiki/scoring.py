"""Pure Wikipedia Speed Run scoring (steps + time bonus)."""

import math
from typing import List


def compute_steps_score(clicks_taken: int, optimal_click_count: int) -> int:
    """Steps component: max 125, floor 12 when over optimal (PRD formula)."""
    if clicks_taken <= optimal_click_count:
        return 125
    excess = clicks_taken - optimal_click_count
    return max(125 - 2 * (excess**2), 12)


def compute_time_bonus(time_ms: int, time_limit_ms: int) -> int:
    """Time bonus in 0..75 from server elapsed time and limit."""
    if time_limit_ms <= 0:
        return 0
    raw = math.floor(75 * (1 - time_ms / time_limit_ms))
    return max(0, min(75, raw))


def compute_puzzle_score(
    *,
    clicks_taken: int,
    optimal_click_count: int,
    time_ms: int,
    time_limit_ms: int,
    timed_out: bool,
) -> int:
    """Full puzzle score; timeout always 0."""
    if timed_out:
        return 0
    return compute_steps_score(clicks_taken, optimal_click_count) + compute_time_bonus(
        time_ms, time_limit_ms
    )


def aggregate_total_score(puzzle_scores: List[int]) -> int:
    """Sum of per-puzzle scores (used for tests / total ledger)."""
    return sum(puzzle_scores)
