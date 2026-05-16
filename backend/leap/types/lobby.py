"""Lobby domain types."""

from typing import List

from leap.types import BaseLeapModel
from leap.types.game import GameStatusDTO


class LobbyDTO(BaseLeapModel):
    player_display_name: str
    games: List[GameStatusDTO]
