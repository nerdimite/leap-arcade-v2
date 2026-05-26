"""DAO for picture puzzle attempt rows."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO, BaseWritePgDAO
from leap.dao.models.picture_puzzle_attempt import PicturePuzzleAttempt
from leap.types.picture import PicturePuzzleAttemptDTO


class PicturePuzzleAttemptDAO(BaseReadPgDAO[PicturePuzzleAttempt], BaseWritePgDAO[PicturePuzzleAttempt]):
    """Persists and reads per-submit attempt history for a Picture session."""

    def __init__(self) -> None:
        super().__init__(model_class=PicturePuzzleAttempt)

    def _to_dto(self, orm: PicturePuzzleAttempt) -> PicturePuzzleAttemptDTO:
        data = {
            "id": orm.id,
            "game_session_id": orm.game_session_id,
            "puzzle_id": orm.puzzle_id,
            "submitted_answer": orm.submitted_answer,
            "correct": orm.correct,
            "skipped": orm.skipped,
            "created_at": orm.created_at,
        }
        return PicturePuzzleAttemptDTO.model_validate(data)

    async def create(
        self,
        session: AsyncSession,
        game_session_id: str,
        puzzle_id: str,
        submitted_answer: Optional[str],
        correct: bool,
        skipped: bool,
    ) -> PicturePuzzleAttemptDTO:
        """Insert an attempt row; ``id`` and ``created_at`` are server-generated."""
        orm = PicturePuzzleAttempt(
            game_session_id=game_session_id,
            puzzle_id=puzzle_id,
            submitted_answer=submitted_answer,
            correct=correct,
            skipped=skipped,
        )
        await self._create(session, orm)
        return self._to_dto(orm)

    async def get_all_for_session(
        self,
        session: AsyncSession,
        game_session_id: str,
    ) -> List[PicturePuzzleAttemptDTO]:
        stmt = (
            select(PicturePuzzleAttempt)
            .where(PicturePuzzleAttempt.game_session_id == game_session_id)
            .order_by(PicturePuzzleAttempt.created_at.asc())
        )
        result = await session.execute(stmt)
        return [self._to_dto(row) for row in result.scalars().all()]

    async def get_resolved_puzzle_ids(
        self,
        session: AsyncSession,
        game_session_id: str,
    ) -> List[str]:
        """Puzzle IDs that already have a terminal resolution (correct or skipped)."""
        stmt = (
            select(PicturePuzzleAttempt.puzzle_id)
            .where(
                PicturePuzzleAttempt.game_session_id == game_session_id,
                (PicturePuzzleAttempt.correct.is_(True)) | (PicturePuzzleAttempt.skipped.is_(True)),
            )
            .distinct()
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
