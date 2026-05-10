from dataclasses import dataclass
from enum import Enum


class GameId(str, Enum):
    WIKI = "wiki"
    PICTURE = "picture"
    RAPID_FIRE = "rapid_fire"
    FOUR_PICS = "four_pics"
    CROSSWORD = "crossword"


@dataclass
class ScoringResult:
    """Result returned by every game's scoring logic."""

    game_id: GameId
    score: int
    time_taken_seconds: float
    breakdown: dict  # game-specific detail (hints used, streak bonus, etc.)
    is_correct: bool
