"""Leaderboard API response shapes."""

from typing import List

from pydantic import BaseModel


class LeaderboardEntrySchema(BaseModel):
    rank: int
    player_id: str
    display_name: str
    total_score: int
    games_completed: int


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntrySchema]
    total_players: int
