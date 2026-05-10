from leap.core.context_manager import ContextManager
from leap.core.common.logger import get_logger


class BaseService:
    """Base class for all application services.

    Provides access to the database session factory via context_manager
    and a structured logger bound to the subclass module name.
    Subclasses instantiate their DAOs in __init__.
    """

    def __init__(self, context_manager: ContextManager) -> None:
        self.context_manager = context_manager
        self.logger = get_logger(self.__class__.__module__)
