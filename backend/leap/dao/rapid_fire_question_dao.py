"""DAO for loading all rapid-fire questions into the startup cache."""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.rapid_fire_question import RapidFireQuestion
from leap.types.rapid_fire import RapidFireQuestionDTO


class RapidFireQuestionDAO(BaseReadPgDAO[RapidFireQuestion]):
    """Read-only DAO used once at startup to populate the in-memory question cache."""

    def __init__(self) -> None:
        super().__init__(model_class=RapidFireQuestion)

    def _to_dto(self, orm: RapidFireQuestion) -> RapidFireQuestionDTO:
        return RapidFireQuestionDTO.model_validate(orm)

    async def get_all(self, session: AsyncSession) -> List[RapidFireQuestionDTO]:
        """Return every question ordered by primary key."""
        rows = await self._get_all(
            session,
            order_by=RapidFireQuestion.id,
        )
        return [self._to_dto(row) for row in rows]
