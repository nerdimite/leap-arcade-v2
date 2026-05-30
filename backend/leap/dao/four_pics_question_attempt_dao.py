"""DAO for Four Pics question attempt rows."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO, BaseWritePgDAO
from leap.dao.models.four_pics_question_attempt import FourPicsQuestionAttempt
from leap.types.four_pics import FourPicsQuestionAttemptDTO


class FourPicsQuestionAttemptDAO(
    BaseReadPgDAO[FourPicsQuestionAttempt], BaseWritePgDAO[FourPicsQuestionAttempt]
):
    """Persists per-question attempt lifecycle for a Four Pics session."""

    def __init__(self) -> None:
        super().__init__(model_class=FourPicsQuestionAttempt)

    def _to_dto(self, orm: FourPicsQuestionAttempt) -> FourPicsQuestionAttemptDTO:
        return FourPicsQuestionAttemptDTO.model_validate(orm)

    async def create(
        self,
        session: AsyncSession,
        session_id: str,
        question_id: str,
        started_at: datetime,
    ) -> FourPicsQuestionAttemptDTO:
        orm = FourPicsQuestionAttempt(
            session_id=session_id,
            question_id=question_id,
            status="active",
            started_at=started_at,
        )
        await self._create(session, orm)
        return self._to_dto(orm)

    async def get_active_for_session(
        self,
        session: AsyncSession,
        session_id: str,
    ) -> Optional[FourPicsQuestionAttemptDTO]:
        stmt = (
            select(FourPicsQuestionAttempt)
            .where(
                FourPicsQuestionAttempt.session_id == session_id,
                FourPicsQuestionAttempt.status == "active",
            )
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_dto(row) if row is not None else None

    async def get_all_for_session(
        self,
        session: AsyncSession,
        session_id: str,
    ) -> List[FourPicsQuestionAttemptDTO]:
        stmt = (
            select(FourPicsQuestionAttempt)
            .where(FourPicsQuestionAttempt.session_id == session_id)
            .order_by(FourPicsQuestionAttempt.started_at.asc())
        )
        result = await session.execute(stmt)
        return [self._to_dto(row) for row in result.scalars().all()]

    async def update_status_and_score(
        self,
        session: AsyncSession,
        attempt_id: str,
        *,
        status: str,
        selected_index: int,
        score: int,
        time_bonus: int,
        time_ms: int,
        completed_at: datetime,
    ) -> FourPicsQuestionAttemptDTO:
        stmt = select(FourPicsQuestionAttempt).where(FourPicsQuestionAttempt.id == attempt_id)
        result = await session.execute(stmt)
        orm = result.scalar_one()
        orm.status = status
        orm.selected_index = selected_index
        orm.score = score
        orm.time_bonus = time_bonus
        orm.time_ms = time_ms
        orm.completed_at = completed_at
        await session.flush()
        return self._to_dto(orm)

    async def close_active_on_abandon(
        self,
        session: AsyncSession,
        attempt_id: str,
        *,
        completed_at: datetime,
    ) -> FourPicsQuestionAttemptDTO:
        stmt = select(FourPicsQuestionAttempt).where(FourPicsQuestionAttempt.id == attempt_id)
        result = await session.execute(stmt)
        orm = result.scalar_one()
        orm.status = "wrong"
        orm.selected_index = None
        orm.score = 0
        orm.time_bonus = 0
        orm.time_ms = None
        orm.completed_at = completed_at
        await session.flush()
        return self._to_dto(orm)
