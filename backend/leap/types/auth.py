"""Authentication domain types."""

from leap.types import BaseLeapModel
from leap.types.player import PlayerDTO


class LoginDTO(BaseLeapModel):
    access_token: str
    token_type: str = "bearer"
    player: PlayerDTO
