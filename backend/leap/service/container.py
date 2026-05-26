from leap.config.settings import get_settings
from leap.core.context_manager import ContextManager
from leap.dao.game_session_dao import GameSessionDAO
from leap.dao.player_dao import PlayerDAO
from leap.dao.rapid_fire_answer_dao import RapidFireAnswerDAO
from leap.dao.rapid_fire_question_dao import RapidFireQuestionDAO
from leap.dao.picture_puzzle_attempt_dao import PicturePuzzleAttemptDAO
from leap.dao.picture_puzzle_dao import PicturePuzzleDAO
from leap.dao.wiki_puzzle_attempt_dao import WikiPuzzleAttemptDAO
from leap.dao.wiki_round_dao import WikiRoundDAO
from leap.games.picture.service import PictureService
from leap.games.rapid_fire.service import RapidFireService
from leap.games.wiki.html_rewriter import WikiHtmlRewriter
from leap.games.wiki.service import WikiSpeedRunService
from leap.games.wiki.wikipedia_client import WikipediaClient
from leap.service.auth_service import AuthService
from leap.service.leaderboard_service import LeaderboardService
from leap.service.lobby_service import LobbyService
from leap.service.player_session_service import PlayerSessionService


class ServiceContainer:
    """Wires up and exposes application services.

    Created once at startup and stored on app.state.
    """

    def __init__(self, context_manager: ContextManager) -> None:
        self.context_manager = context_manager

        player_dao = PlayerDAO()
        game_session_dao = GameSessionDAO()
        rapid_fire_answer_dao = RapidFireAnswerDAO()
        rapid_fire_question_dao = RapidFireQuestionDAO()
        wiki_round_dao = WikiRoundDAO()
        wiki_puzzle_attempt_dao = WikiPuzzleAttemptDAO()
        picture_puzzle_dao = PicturePuzzleDAO()
        picture_attempt_dao = PicturePuzzleAttemptDAO()

        self.wikipedia_client = WikipediaClient()
        self.wiki_html_rewriter = WikiHtmlRewriter()

        self.auth = AuthService(context_manager, player_dao)
        self.lobby = LobbyService(context_manager, game_session_dao)
        self.player_sessions = PlayerSessionService(context_manager, game_session_dao)
        self.rapid_fire = RapidFireService(
            context_manager,
            game_session_dao,
            rapid_fire_answer_dao,
            rapid_fire_question_dao,
        )
        self.wiki_speed_run = WikiSpeedRunService(
            context_manager,
            game_session_dao,
            wiki_round_dao,
            wiki_puzzle_attempt_dao,
            self.wikipedia_client,
            self.wiki_html_rewriter,
            back_button_enabled=get_settings().WIKI_BACK_BUTTON_ENABLED,
        )
        self.picture = PictureService(
            context_manager,
            game_session_dao,
            picture_puzzle_dao,
            picture_attempt_dao,
        )
        self.leaderboard = LeaderboardService(context_manager, game_session_dao)
