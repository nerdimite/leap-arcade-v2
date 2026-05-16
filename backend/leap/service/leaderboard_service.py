"""Leaderboard — aggregated scores across all players and sessions."""

from typing import TYPE_CHECKING

from leap.core.context_manager import ContextManager
from leap.types.leaderboard import LeaderboardDTO, RankedLeaderboardEntryDTO

if TYPE_CHECKING:
    from leap.dao.game_session_dao import GameSessionDAO


class LeaderboardService:
    """Builds the global leaderboard from session aggregates."""

    def __init__(
        self,
        context_manager: ContextManager,
        game_session_dao: "GameSessionDAO",
    ) -> None:
        self.ctx = context_manager
        self.game_session_dao = game_session_dao

    async def get_leaderboard(self) -> LeaderboardDTO:
        """Return all players ranked by domain ordering rules."""
        async with self.ctx.session() as session:
            rows = await self.game_session_dao.get_leaderboard(session)

        entries = [
            RankedLeaderboardEntryDTO(
                rank=i,
                player_id=r.player_id,
                display_name=r.display_name,
                total_score=r.total_score,
                games_completed=r.games_completed,
            )
            for i, r in enumerate(rows, start=1)
        ]
        return LeaderboardDTO(entries=entries, total_players=len(entries))
