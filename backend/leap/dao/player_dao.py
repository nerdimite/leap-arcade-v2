"""DAO for the ``players`` table."""

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BasePgDAO
from leap.dao.models.player import Player
from leap.types.player import PlayerDTO


class PlayerDAO(BasePgDAO[Player]):
    """Read-only access to the players table.

    Players are pre-seeded before the event. No insert/update at runtime.
    """

    def __init__(self) -> None:
        super().__init__(model_class=Player)

    def _to_orm(self, data: Dict[str, Any]) -> Player:
        raise NotImplementedError("PlayerDAO is read-only; use seed loader for inserts")

    def _to_dto(self, orm: Player) -> PlayerDTO:
        """Convert a Player ORM row to a PlayerDTO."""
        return PlayerDTO.model_validate(orm)

    def _apply_filters(self, query: Any, filters: Dict[str, Any]) -> Any:
        raise NotImplementedError("PlayerDAO does not support list filtering")

    async def get_by_id(self, session: AsyncSession, corp_id: str) -> Optional[PlayerDTO]:
        """Return the PlayerDTO for the given corp_id, or None if not found."""
        result = await session.execute(
            select(Player).where(Player.id == corp_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_dto(orm) if orm is not None else None
