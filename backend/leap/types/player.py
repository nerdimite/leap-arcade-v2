"""Player domain types."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from leap.types import BaseLeapModel


class PlayerDTO(BaseLeapModel):
    """Persisted player record as returned by PlayerDAO."""

    id: str  # normalised corp_id (lowercase)
    display_name: str
    created_at: Optional[datetime] = None


class CurrentPlayer(BaseModel):
    """Authenticated player identity derived from JWT claims.

    Constructed from token claims — never fetched from DB per request.
    """

    id: str
    display_name: str
