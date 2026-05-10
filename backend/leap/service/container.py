from leap.core.context_manager import ContextManager
from leap.dao.game_session_dao import GameSessionDAO
from leap.dao.player_dao import PlayerDAO
from leap.games.rapid_fire.service import RapidFireService
from leap.service.auth_service import AuthService
from leap.service.lobby_service import LobbyService


class ServiceContainer:
    """Wires up and exposes application services.

    Created once at startup and stored on app.state.
    """

    def __init__(self, context_manager: ContextManager) -> None:
        self.context_manager = context_manager

        player_dao = PlayerDAO()
        game_session_dao = GameSessionDAO()

        self.auth = AuthService(context_manager, player_dao)
        self.lobby = LobbyService(context_manager, game_session_dao)
        self.rapid_fire = RapidFireService(context_manager)
        # TODO: wire leaderboard service when stubbed
