"""DAO for pinpoint puzzle attempt rows."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO, BaseWritePgDAO
from leap.dao.models.pinpoint_puzzle import PinpointPuzzleAttempt
from leap.types.pinpoint import PinpointPuzzleAttemptDTO


class PinpointPuzzleAttemptDAO(
    BaseReadPgDAO[PinpointPuzzleAttempt], BaseWritePgDAO[PinpointPuzzleAttempt]
):
    """Persists per-puzzle attempt lifecycle for a Pinpoint session."""

    def __init__(self) -> None:
        super().__init__(model_class=PinpointPuzzleAttempt)

    def _to_dto(self, orm: PinpointPuzzleAttempt) -> PinpointPuzzleAttemptDTO:
        return PinpointPuzzleAttemptDTO.model_validate(orm)

    async def create(
        self,
        session: AsyncSession,
        game_session_id: str,
        puzzle_id: str,
        started_at: datetime,
    ) -> PinpointPuzzleAttemptDTO:
        orm = PinpointPuzzleAttempt(
            game_session_id=game_session_id,
            puzzle_id=puzzle_id,
            clues_revealed=1,
            guesses=[],
            status="active",
            started_at=started_at,
        )
        await self._create(session, orm)
        return self._to_dto(orm)

    async def get_for_session(
        self,
        session: AsyncSession,
        game_session_id: str,
    ) -> List[PinpointPuzzleAttemptDTO]:
        stmt = (
            select(PinpointPuzzleAttempt)
            .where(PinpointPuzzleAttempt.game_session_id == game_session_id)
            .order_by(PinpointPuzzleAttempt.started_at.asc())
        )
        result = await session.execute(stmt)
        return [self._to_dto(row) for row in result.scalars().all()]

    async def get_by_session_and_puzzle(
        self,
        session: AsyncSession,
        game_session_id: str,
        puzzle_id: str,
    ) -> Optional[PinpointPuzzleAttemptDTO]:
        stmt = select(PinpointPuzzleAttempt).where(
            PinpointPuzzleAttempt.game_session_id == game_session_id,
            PinpointPuzzleAttempt.puzzle_id == puzzle_id,
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_dto(row) if row is not None else None

    async def update_status_and_score(
        self,
        session: AsyncSession,
        attempt_id: str,
        *,
        status: str,
        score: int,
        time_bonus: Optional[int],
        completed_at: datetime,
    ) -> PinpointPuzzleAttemptDTO:
        stmt = select(PinpointPuzzleAttempt).where(PinpointPuzzleAttempt.id == attempt_id)
        result = await session.execute(stmt)
        orm = result.scalar_one()
        orm.status = status
        orm.score = score
        orm.time_bonus = time_bonus
        orm.completed_at = completed_at
        await session.flush()
        return self._to_dto(orm)

    async def append_guess_and_increment_clues(
        self,
        session: AsyncSession,
        attempt_id: str,
        guess: str,
    ) -> PinpointPuzzleAttemptDTO:
        stmt = select(PinpointPuzzleAttempt).where(PinpointPuzzleAttempt.id == attempt_id)
        result = await session.execute(stmt)
        orm = result.scalar_one()
        orm.guesses = list(orm.guesses or []) + [guess]
        orm.clues_revealed = orm.clues_revealed + 1
        await session.flush()
        return self._to_dto(orm)
