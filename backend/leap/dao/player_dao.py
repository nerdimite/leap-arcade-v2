"""DAO for the ``players`` table."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.player import Player
from leap.types.player import PlayerDTO


class PlayerDAO(BaseReadPgDAO[Player]):
    """Read-only access to the players table.

    Players are pre-seeded before the event. No insert/update at runtime.
    """

    def __init__(self) -> None:
        super().__init__(model_class=Player)

    def _to_dto(self, orm: Player) -> PlayerDTO:
        """Convert a Player ORM row to a PlayerDTO."""
        return PlayerDTO.model_validate(orm)

    async def get_by_id(self, session: AsyncSession, corp_id: str) -> Optional[PlayerDTO]:
        """Return the PlayerDTO for the given corp_id, or None if not found."""
        orm = await self._get_by_id(session, corp_id)
        return self._to_dto(orm) if orm is not None else None
