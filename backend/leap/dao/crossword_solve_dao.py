"""DAO for crossword solve rows."""

from typing import Any, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.core.common.time import utc_now
from leap.dao.base_pg_dao import BaseReadPgDAO, BaseWritePgDAO
from leap.dao.models.crossword import CrosswordSolve
from leap.types.crossword import CrosswordSolveDTO


class CrosswordSolveDAO(BaseReadPgDAO[CrosswordSolve], BaseWritePgDAO[CrosswordSolve]):
    """Writes and reads persisted crossword solves."""

    def __init__(self) -> None:
        super().__init__(model_class=CrosswordSolve)

    def _apply_filters(self, query: Any, filters: dict) -> Any:
        return query

    def _to_dto(self, orm: CrosswordSolve) -> CrosswordSolveDTO:
        return CrosswordSolveDTO(
            id=orm.id,
            session_id=orm.game_session_id,
            entry_id=orm.entry_id,
            solved_at=orm.solved_at,
        )

    async def create(
        self,
        session: AsyncSession,
        session_id: str,
        entry_id: str,
    ) -> CrosswordSolveDTO:
        orm = CrosswordSolve(
            game_session_id=session_id,
            entry_id=entry_id,
            solved_at=utc_now(),
        )
        await self._create(session, orm)
        return self._to_dto(orm)

    async def get_for_session(
        self,
        session: AsyncSession,
        session_id: str,
    ) -> List[CrosswordSolveDTO]:
        stmt = (
            select(CrosswordSolve)
            .where(CrosswordSolve.game_session_id == session_id)
            .order_by(CrosswordSolve.solved_at.asc())
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
            .select_from(CrosswordSolve)
            .where(CrosswordSolve.game_session_id == session_id)
        )
        result = await session.execute(stmt)
        return int(result.scalar_one())
