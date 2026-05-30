"""Player-centric views backed by game session rows."""

from typing import TYPE_CHECKING, List, Optional

from leap.core.context_manager import ContextManager
from leap.types.game import GameSessionStatus, PlayerSessionSummaryDTO
from leap.types.player import CurrentPlayer

if TYPE_CHECKING:
    from leap.dao.game_session_dao import GameSessionDAO


class PlayerSessionService:
    """Lists persisted game sessions for the authenticated player."""

    def __init__(self, context_manager: ContextManager, game_session_dao: "GameSessionDAO") -> None:
        self.ctx = context_manager
        self.game_session_dao = game_session_dao

    async def list_my_sessions(self, player: CurrentPlayer) -> List[PlayerSessionSummaryDTO]:
        """Return all game sessions for this player, sorted by ``game_id``."""
        async with self.ctx.session() as session:
            rows = await self.game_session_dao.get_all_for_player(session, player.id)

        summaries: List[PlayerSessionSummaryDTO] = []
        for row in sorted(rows, key=lambda r: r.game_id):
            score_out: Optional[int] = None
            if row.status != GameSessionStatus.ACTIVE:
                score_out = row.score
            summaries.append(
                PlayerSessionSummaryDTO(
                    game_id=row.game_id,
                    status=row.status,
                    score=score_out,
                )
            )
        return summaries
