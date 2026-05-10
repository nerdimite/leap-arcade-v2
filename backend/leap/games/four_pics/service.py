from leap.core.context_manager import ContextManager


class FourPicsService:
    """Handles Four Pics One Lie game sessions and submissions."""

    def __init__(self, context_manager: ContextManager) -> None:
        self._context_manager = context_manager
        # TODO: inject FourPicsContentDAO once implemented
