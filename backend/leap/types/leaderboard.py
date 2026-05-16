"""Leaderboard domain types."""

from typing import List

from leap.types import BaseLeapModel


class RankedLeaderboardEntryDTO(BaseLeapModel):
    rank: int
    player_id: str
    display_name: str
    total_score: int
    games_completed: int


class LeaderboardDTO(BaseLeapModel):
    entries: List[RankedLeaderboardEntryDTO]
    total_players: int
