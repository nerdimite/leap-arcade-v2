"""DAO for wiki rounds (seeded puzzle definitions)."""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO
from leap.dao.models.wiki_round import WikiRound
from leap.types.wiki import WikiRoundDTO


class WikiRoundDAO(BaseReadPgDAO[WikiRound]):
    """Read wiki rounds from the database."""

    def __init__(self) -> None:
        super().__init__(model_class=WikiRound)

    def _to_dto(self, orm: WikiRound) -> WikiRoundDTO:
        return WikiRoundDTO.model_validate(orm)

    async def get_all_ordered(self, session: AsyncSession) -> List[WikiRoundDTO]:
        rows = await self._get_all(session, order_by=WikiRound.sequence_index)
        return [self._to_dto(r) for r in rows]
