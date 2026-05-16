"""DAO for the ``game_sessions`` table."""

import uuid
from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from leap.dao.base_pg_dao import BaseReadPgDAO, BaseWritePgDAO
from leap.dao.models.game_session import GameSession
from leap.types.game import GameSessionDTO, GameSessionStatus, LeaderboardEntryDTO


class GameSessionDAO(BaseReadPgDAO[GameSession], BaseWritePgDAO[GameSession]):
    """Manages player game sessions."""

    def __init__(self) -> None:
        super().__init__(model_class=GameSession)

    def _to_dto(self, orm: GameSession) -> GameSessionDTO:
        """Convert a GameSession ORM row to a GameSessionDTO."""
        return GameSessionDTO.model_validate(orm)

    async def get_all_for_player(
        self, session: AsyncSession, player_id: str
    ) -> List[GameSessionDTO]:
        """Return all game sessions for the given player (any status)."""
        result = await session.execute(
            select(GameSession).where(GameSession.player_id == player_id)
        )
        return [self._to_dto(row) for row in result.scalars().all()]

    async def get_by_player_and_game(
        self, session: AsyncSession, player_id: str, game_id: str
    ) -> Optional[GameSessionDTO]:
        """Return the session for this player+game combination, or None."""
        result = await session.execute(
            select(GameSession).where(
                GameSession.player_id == player_id,
                GameSession.game_id == game_id,
            )
        )
        orm = result.scalar_one_or_none()
        return self._to_dto(orm) if orm is not None else None

    async def create(
        self, session: AsyncSession, player_id: str, game_id: str
    ) -> GameSessionDTO:
        """Insert a new active game session and return it."""
        orm = GameSession(
            id=str(uuid.uuid4()),
            player_id=player_id,
            game_id=game_id,
            status=GameSessionStatus.ACTIVE,
        )
        await self._create(session, orm)
        return self._to_dto(orm)

    async def update_status(
        self,
        session: AsyncSession,
        game_session_id: str,
        status: GameSessionStatus,
        score: Optional[int] = None,
    ) -> GameSessionDTO:
        """Update status (and optionally score) for the given session."""
        from leap.core.common.time import utc_now

        orm = await session.get(GameSession, game_session_id)
        if orm is None:
            raise KeyError(f"GameSession not found: {game_session_id}")
        orm.status = status.value
        if score is not None:
            orm.score = score
        if status in (GameSessionStatus.COMPLETED, GameSessionStatus.ABANDONED):
            orm.completed_at = utc_now()
        await session.flush()
        await session.refresh(orm)
        return self._to_dto(orm)

    async def get_leaderboard(self, session: AsyncSession) -> List[LeaderboardEntryDTO]:
        """Aggregate scores per player; order matches ``LeaderboardService`` tie-break rules."""
        sql = text(
            """
            SELECT
                p.id AS player_id,
                p.display_name,
                COALESCE(SUM(gs.score), 0)::bigint AS total_score,
                COUNT(*) FILTER (WHERE gs.status = 'completed')::integer AS games_completed,
                MIN(gs.completed_at) FILTER (WHERE gs.status = 'completed') AS first_completion
            FROM players p
            LEFT JOIN game_sessions gs
                ON gs.player_id = p.id AND gs.status IN ('completed', 'abandoned')
            GROUP BY p.id, p.display_name
            ORDER BY
                total_score DESC,
                games_completed DESC,
                first_completion ASC NULLS LAST,
                p.display_name ASC
            """
        )
        result = await session.execute(sql)
        return [
            LeaderboardEntryDTO(
                player_id=str(m["player_id"]),
                display_name=str(m["display_name"]),
                total_score=int(m["total_score"]),
                games_completed=int(m["games_completed"]),
                first_completion=m["first_completion"],
            )
            for m in result.mappings().all()
        ]
