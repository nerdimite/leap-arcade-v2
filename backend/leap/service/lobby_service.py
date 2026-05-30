"""Lobby service — player's cross-game status view."""

from typing import TYPE_CHECKING, List

from leap.config.constants import GAMES
from leap.core.context_manager import ContextManager
from leap.types.game import GameSessionStatus, GameStatusDTO
from leap.types.lobby import LobbyDTO
from leap.types.player import CurrentPlayer

if TYPE_CHECKING:
    from leap.dao.game_session_dao import GameSessionDAO


class LobbyService:
    """Returns the player's play status across all registered games.

    Merges the static GAMES registry with session rows from the DB.
    Completed or abandoned sessions lock the tile (``has_played``) and expose
    the persisted score; active sessions do not count as played yet.
    """

    def __init__(self, context_manager: ContextManager, game_session_dao: "GameSessionDAO") -> None:
        self.ctx = context_manager
        self.game_session_dao = game_session_dao

    async def get_lobby(self, player: CurrentPlayer) -> LobbyDTO:
        """Return per-game status for the authenticated player."""
        async with self.ctx.session() as session:
            sessions = await self.game_session_dao.get_all_for_player(session, player.id)

        locked = {
            s.game_id: s
            for s in sessions
            if s.status in (GameSessionStatus.COMPLETED, GameSessionStatus.ABANDONED)
        }

        games: List[GameStatusDTO] = [
            GameStatusDTO(
                game_id=game["id"],
                display_name=game["display_name"],
                has_played=game["id"] in locked,
                score=locked[game["id"]].score if game["id"] in locked else None,
            )
            for game in GAMES
        ]

        return LobbyDTO(player_display_name=player.display_name, games=games)
