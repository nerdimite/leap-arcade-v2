from leap.core.context_manager import ContextManager
from leap.games.crossword.service import CrosswordService
from leap.games.four_pics.service import FourPicsService
from leap.games.picture.service import PictureService
from leap.games.rapid_fire.service import RapidFireService
from leap.games.wiki.service import WikiService


class ServiceContainer:
    """Wires up and exposes application services.

    Created once at startup and stored on app.state.
    """

    def __init__(self, context_manager: ContextManager) -> None:
        self._context_manager = context_manager
        self.wiki = WikiService(context_manager)
        self.picture = PictureService(context_manager)
        self.rapid_fire = RapidFireService(context_manager)
        self.four_pics = FourPicsService(context_manager)
        self.crossword = CrosswordService(context_manager)
        # TODO: register auth, session, leaderboard services when implemented
