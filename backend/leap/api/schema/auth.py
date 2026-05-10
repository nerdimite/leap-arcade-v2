"""Auth request / response DTOs."""

from pydantic import BaseModel

from leap.types.player import PlayerDTO


class LoginRequest(BaseModel):
    corp_id: str
    event_code: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player: PlayerDTO
