"""DAO for word hunt find rows."""

from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.core.common.time import utc_now
from leap.dao.base_pg_dao import BaseReadPgDAO, BaseWritePgDAO
from leap.dao.models.word_hunt import WordHuntFind
from leap.types.word_hunt import WordHuntFindDTO


class WordHuntFindDAO(BaseReadPgDAO[WordHuntFind], BaseWritePgDAO[WordHuntFind]):
    """Writes and reads persisted word hunt finds."""

    def __init__(self) -> None:
        super().__init__(model_class=WordHuntFind)

    def _to_dto(self, orm: WordHuntFind) -> WordHuntFindDTO:
        return WordHuntFindDTO(
            id=orm.id,
            session_id=orm.game_session_id,
            word_id=orm.word_id,
            start_row=orm.start_row,
            start_col=orm.start_col,
            end_row=orm.end_row,
            end_col=orm.end_col,
            found_at=orm.found_at,
        )

    async def create(
        self,
        session: AsyncSession,
        session_id: str,
        word_id: str,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int,
    ) -> WordHuntFindDTO:
        orm = WordHuntFind(
            game_session_id=session_id,
            word_id=word_id,
            start_row=start_row,
            start_col=start_col,
            end_row=end_row,
            end_col=end_col,
            found_at=utc_now(),
        )
        await self._create(session, orm)
        return self._to_dto(orm)

    async def get_for_session(
        self,
        session: AsyncSession,
        session_id: str,
    ) -> List[WordHuntFindDTO]:
        stmt = (
            select(WordHuntFind)
            .where(WordHuntFind.game_session_id == session_id)
            .order_by(WordHuntFind.found_at.asc())
        )
        result = await session.execute(stmt)
        return [self._to_dto(row) for row in result.scalars().all()]

    async def count_for_session(
        self,
        session: AsyncSession,
        session_id: str,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(WordHuntFind)
            .where(WordHuntFind.game_session_id == session_id)
        )
        result = await session.execute(stmt)
        return int(result.scalar_one())
