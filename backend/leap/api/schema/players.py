"""API schemas for player routes."""

from typing import Optional

from pydantic import BaseModel, Field


class PlayerSessionItem(BaseModel):
    game_id: str
    status: str
    score: Optional[int] = Field(default=None)