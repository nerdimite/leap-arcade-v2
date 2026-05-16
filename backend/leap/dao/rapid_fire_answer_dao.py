"""DAO for rapid fire answer rows."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO, BaseWritePgDAO
from leap.dao.models.rapid_fire_answer import RapidFireAnswer
from leap.types.rapid_fire import RapidFireAnswerDTO


class RapidFireAnswerDAO(BaseReadPgDAO[RapidFireAnswer], BaseWritePgDAO[RapidFireAnswer]):
    """Writes and reads persisted rapid fire answers."""

    def __init__(self) -> None:
        super().__init__(model_class=RapidFireAnswer)

    def _to_dto(self, orm: RapidFireAnswer) -> RapidFireAnswerDTO:
        return RapidFireAnswerDTO.model_validate(orm)

    async def create(
        self,
        session: AsyncSession,
        game_session_id: str,
        question_id: str,
        correct: bool,
        skipped: bool,
        selected_option: Optional[int],
        time_ms: int,
    ) -> RapidFireAnswerDTO:
        """Insert an answer row; ``id`` and ``answered_at`` are server-generated."""
        orm = RapidFireAnswer(
            game_session_id=game_session_id,
            question_id=question_id,
            correct=correct,
            skipped=skipped,
            selected_option=selected_option,
            time_ms=time_ms,
        )
        await self._create(session, orm)
        return self._to_dto(orm)

    async def get_asked_question_ids(
        self,
        session: AsyncSession,
        game_session_id: str,
    ) -> List[str]:
        """Lightweight projection of answered question IDs for resume."""
        stmt = select(RapidFireAnswer.question_id).where(
            RapidFireAnswer.game_session_id == game_session_id
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_for_session(
        self,
        session: AsyncSession,
        game_session_id: str,
    ) -> List[RapidFireAnswerDTO]:
        """Ordered answers used for scoring and breakdown counts."""
        stmt = (
            select(RapidFireAnswer)
            .where(RapidFireAnswer.game_session_id == game_session_id)
            .order_by(RapidFireAnswer.answered_at.asc())
        )
        result = await session.execute(stmt)
        return [self._to_dto(row) for row in result.scalars().all()]
