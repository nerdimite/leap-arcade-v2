"""Lobby response DTOs."""

from typing import List

from pydantic import BaseModel

from leap.types.game import GameStatusDTO


class LobbyResponse(BaseModel):
    player_display_name: str
    games: List[GameStatusDTO]
