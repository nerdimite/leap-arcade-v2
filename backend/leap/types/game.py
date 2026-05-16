"""Game session domain types."""

from datetime import datetime
from enum import Enum
from typing import Optional

from leap.types import BaseLeapModel


class GameSessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class GameSessionDTO(BaseLeapModel):
    """Persisted game session record as returned by GameSessionDAO."""

    id: str
    player_id: str
    game_id: str
    status: GameSessionStatus
    score: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class LeaderboardEntryDTO(BaseLeapModel):
    """Aggregated leaderboard row from GameSessionDAO.get_leaderboard (DAO layer).

    ``first_completion`` is used for server-side ordering only; API schemas omit it.
    """

    player_id: str
    display_name: str
    total_score: int
    games_completed: int
    first_completion: Optional[datetime] = None


class GameStatusDTO(BaseLeapModel):
    """Per-game status for the lobby view — one row per game in the response."""

    game_id: str
    display_name: str
    has_played: bool
    score: Optional[int] = None
