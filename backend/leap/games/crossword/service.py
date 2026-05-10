from leap.core.context_manager import ContextManager


class CrosswordService:
    """Handles Crossword game sessions and submissions."""

    def __init__(self, context_manager: ContextManager) -> None:
        self._context_manager = context_manager
        # TODO: inject CrosswordContentDAO once implemented
