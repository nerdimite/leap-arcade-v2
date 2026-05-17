"""DAO for per-player wiki puzzle attempts."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO, BaseWritePgDAO
from leap.dao.models.wiki_puzzle_attempt import WikiPuzzleAttempt
from leap.types.wiki import WikiPuzzleAttemptDTO, WikiPuzzleAttemptStatus


class WikiPuzzleAttemptDAO(BaseReadPgDAO[WikiPuzzleAttempt], BaseWritePgDAO[WikiPuzzleAttempt]):
    def __init__(self) -> None:
        super().__init__(model_class=WikiPuzzleAttempt)

    def _to_dto(self, orm: WikiPuzzleAttempt) -> WikiPuzzleAttemptDTO:
        return WikiPuzzleAttemptDTO.model_validate(orm)

    async def get_by_game_session_and_round(
        self, session: AsyncSession, game_session_id: str, round_id: str
    ) -> Optional[WikiPuzzleAttemptDTO]:
        q = select(WikiPuzzleAttempt).where(
            WikiPuzzleAttempt.game_session_id == game_session_id,
            WikiPuzzleAttempt.round_id == round_id,
        )
        result = await session.execute(q)
        orm = result.scalar_one_or_none()
        return self._to_dto(orm) if orm is not None else None

    async def create_for_round(
        self,
        session: AsyncSession,
        game_session_id: str,
        round_id: str,
        start_title: str,
    ) -> WikiPuzzleAttemptDTO:
        orm = WikiPuzzleAttempt(
            id=str(uuid.uuid4()),
            game_session_id=game_session_id,
            round_id=round_id,
            status=WikiPuzzleAttemptStatus.ACTIVE.value,
            current_title=start_title,
            click_path=[],
            steps_taken=0,
        )
        await self._create(session, orm)
        return self._to_dto(orm)

    async def record_forward_navigation(
        self,
        session: AsyncSession,
        attempt_id: str,
        landed_canonical_title: str,
    ) -> WikiPuzzleAttemptDTO:
        orm = await session.get(WikiPuzzleAttempt, attempt_id)
        if orm is None:
            raise KeyError(f"WikiPuzzleAttempt not found: {attempt_id}")
        orm.steps_taken = orm.steps_taken + 1
        path = list(orm.click_path or [])
        path.append(landed_canonical_title)
        orm.click_path = path
        orm.current_title = landed_canonical_title
        await session.flush()
        await session.refresh(orm)
        return self._to_dto(orm)

    async def record_back_navigation(
        self,
        session: AsyncSession,
        attempt_id: str,
        previous_title: str,
    ) -> WikiPuzzleAttemptDTO:
        orm = await session.get(WikiPuzzleAttempt, attempt_id)
        if orm is None:
            raise KeyError(f"WikiPuzzleAttempt not found: {attempt_id}")
        orm.steps_taken = orm.steps_taken + 1
        path = list(orm.click_path or [])
        path.append(previous_title)
        orm.click_path = path
        orm.current_title = previous_title
        await session.flush()
        await session.refresh(orm)
        return self._to_dto(orm)

    async def mark_timed_out(
        self,
        session: AsyncSession,
        attempt_id: str,
        *,
        time_ms: int,
        completed_at: datetime,
    ) -> WikiPuzzleAttemptDTO:
        orm = await session.get(WikiPuzzleAttempt, attempt_id)
        if orm is None:
            raise KeyError(f"WikiPuzzleAttempt not found: {attempt_id}")
        orm.status = WikiPuzzleAttemptStatus.TIMED_OUT.value
        orm.score = 0
        orm.time_ms = time_ms
        orm.completed_at = completed_at
        await session.flush()
        await session.refresh(orm)
        return self._to_dto(orm)

    async def complete_attempt(
        self,
        session: AsyncSession,
        attempt_id: str,
        *,
        score: int,
        time_ms: int,
        completed_at: datetime,
    ) -> WikiPuzzleAttemptDTO:
        orm = await session.get(WikiPuzzleAttempt, attempt_id)
        if orm is None:
            raise KeyError(f"WikiPuzzleAttempt not found: {attempt_id}")
        orm.status = WikiPuzzleAttemptStatus.COMPLETED.value
        orm.score = score
        orm.time_ms = time_ms
        orm.completed_at = completed_at
        await session.flush()
        await session.refresh(orm)
        return self._to_dto(orm)
