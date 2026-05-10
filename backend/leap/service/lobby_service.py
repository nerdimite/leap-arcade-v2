"""Lobby service — player's cross-game status view."""

from typing import TYPE_CHECKING, List

from leap.api.schema.lobby import LobbyResponse
from leap.types.player import CurrentPlayer
from leap.config.constants import GAMES
from leap.core.context_manager import ContextManager
from leap.types.game import GameSessionStatus, GameStatusDTO

if TYPE_CHECKING:
    from leap.dao.game_session_dao import GameSessionDAO


class LobbyService:
    """Returns the player's play status across all registered games.

    Merges the static GAMES registry with any completed sessions from the DB.
    Only COMPLETED sessions count as 'played' — active or abandoned do not.
    """

    def __init__(
        self, context_manager: ContextManager, game_session_dao: "GameSessionDAO"
    ) -> None:
        self.ctx = context_manager
        self.game_session_dao = game_session_dao

    async def get_lobby(self, player: CurrentPlayer) -> LobbyResponse:
        """Return per-game status for the authenticated player."""
        async with self.ctx.session() as session:
            sessions = await self.game_session_dao.get_all_for_player(session, player.id)

        completed = {
            s.game_id: s
            for s in sessions
            if s.status == GameSessionStatus.COMPLETED
        }

        games: List[GameStatusDTO] = [
            GameStatusDTO(
                game_id=game["id"],
                display_name=game["display_name"],
                has_played=game["id"] in completed,
                score=completed[game["id"]].score if game["id"] in completed else None,
            )
            for game in GAMES
        ]

        return LobbyResponse(player_display_name=player.display_name, games=games)
