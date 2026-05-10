from leap.core.context_manager import ContextManager


class WikiService:
    """Handles Wikipedia Speed Run game sessions and submissions."""

    def __init__(self, context_manager: ContextManager) -> None:
        self._context_manager = context_manager
        # TODO: inject WikiContentDAO once implemented
