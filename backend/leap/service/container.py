from sqlalchemy.ext.asyncio import AsyncSession

from leap.config.settings import get_settings
from leap.core.context_manager import ContextManager
from leap.dao.game_session_dao import GameSessionDAO
from leap.dao.player_dao import PlayerDAO
from leap.dao.rapid_fire_answer_dao import RapidFireAnswerDAO
from leap.dao.rapid_fire_question_dao import RapidFireQuestionDAO
from leap.dao.four_pics_question_attempt_dao import FourPicsQuestionAttemptDAO
from leap.dao.four_pics_question_dao import FourPicsQuestionDAO
from leap.dao.pinpoint_puzzle_attempt_dao import PinpointPuzzleAttemptDAO
from leap.dao.pinpoint_puzzle_dao import PinpointPuzzleDAO
from leap.dao.crossword_puzzle_dao import CrosswordPuzzleDAO
from leap.dao.crossword_solve_dao import CrosswordSolveDAO
from leap.dao.word_hunt_find_dao import WordHuntFindDAO
from leap.dao.word_hunt_puzzle_dao import WordHuntPuzzleDAO
from leap.dao.picture_puzzle_attempt_dao import PicturePuzzleAttemptDAO
from leap.dao.picture_puzzle_dao import PicturePuzzleDAO
from leap.dao.wiki_puzzle_attempt_dao import WikiPuzzleAttemptDAO
from leap.dao.wiki_round_dao import WikiRoundDAO
from leap.games.four_pics.service import FourPicsService
from leap.games.pinpoint.service import PinpointService
from leap.games.crossword.service import CrosswordService
from leap.games.word_hunt.service import WordHuntService
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
        four_pics_question_dao = FourPicsQuestionDAO()
        four_pics_attempt_dao = FourPicsQuestionAttemptDAO()
        pinpoint_puzzle_dao = PinpointPuzzleDAO()
        pinpoint_attempt_dao = PinpointPuzzleAttemptDAO()
        word_hunt_puzzle_dao = WordHuntPuzzleDAO()
        word_hunt_find_dao = WordHuntFindDAO()
        crossword_puzzle_dao = CrosswordPuzzleDAO()
        crossword_solve_dao = CrosswordSolveDAO()

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
        self.four_pics = FourPicsService(
            context_manager,
            game_session_dao,
            four_pics_attempt_dao,
            four_pics_question_dao,
        )
        self.pinpoint = PinpointService(
            context_manager,
            game_session_dao,
            pinpoint_puzzle_dao,
            pinpoint_attempt_dao,
        )
        self.word_hunt = WordHuntService(
            context_manager,
            game_session_dao,
            word_hunt_puzzle_dao,
            word_hunt_find_dao,
        )
        self.crossword = CrosswordService(
            context_manager,
            game_session_dao,
            crossword_puzzle_dao,
            crossword_solve_dao,
        )
        self.leaderboard = LeaderboardService(context_manager, game_session_dao)

    async def warm_caches(self, session: AsyncSession) -> None:
        """(Re)load every game service's in-memory content cache from the database.

        Each ``initialize`` is an idempotent full-replace, so this is safe to call at
        startup, after an admin reset, or in response to a cross-worker
        cache-invalidation NOTIFY.
        """
        await self.rapid_fire.initialize(session)
        await self.wiki_speed_run.initialize(session)
        await self.picture.initialize(session)
        await self.four_pics.initialize(session)
        await self.pinpoint.initialize(session)
        await self.word_hunt.initialize(session)
        await self.crossword.initialize(session)
