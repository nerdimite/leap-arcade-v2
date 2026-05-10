"""Domain exceptions raised by the service layer.

All extend ``BaseServiceException``. The global handler in ``leap/api/main.py`` converts
them to JSON responses. Routes never raise ``HTTPException`` — services raise these instead.

Add new codes to ``leap/config/errors.py`` first, then add the subclass here.
"""

from http import HTTPStatus
from typing import Any, Dict, Optional

from leap.config.errors import ErrorCodes, ErrorHttpStatus, ErrorMessages


class BaseServiceException(Exception):
    """Base for all service-layer exceptions."""

    def __init__(
        self,
        error_code: int,
        message: str,
        http_status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.error_code = error_code
        self.message = message
        self.http_status = http_status
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": False,
            "message": self.message,
            "code": self.error_code,
            "http_status": self.http_status.value,
            "error": self.details,
        }


class PlayerNotFoundException(BaseServiceException):
    def __init__(self, corp_id: str) -> None:
        super().__init__(
            error_code=ErrorCodes.PLAYER_NOT_FOUND,
            message=f"{ErrorMessages.PLAYER_NOT_FOUND}: {corp_id}",
            http_status=ErrorHttpStatus.PLAYER_NOT_FOUND,
            details={"corp_id": corp_id},
        )


class InvalidEventCodeException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(
            error_code=ErrorCodes.INVALID_EVENT_CODE,
            message=ErrorMessages.INVALID_EVENT_CODE,
            http_status=ErrorHttpStatus.INVALID_EVENT_CODE,
        )


class InvalidTokenException(BaseServiceException):
    def __init__(self, reason: Optional[str] = None) -> None:
        super().__init__(
            error_code=ErrorCodes.INVALID_TOKEN,
            message=reason or ErrorMessages.INVALID_TOKEN,
            http_status=ErrorHttpStatus.INVALID_TOKEN,
        )


class SessionAlreadyExistsException(BaseServiceException):
    def __init__(self, player_id: str, game_id: str) -> None:
        super().__init__(
            error_code=ErrorCodes.SESSION_ALREADY_EXISTS,
            message=ErrorMessages.SESSION_ALREADY_EXISTS,
            http_status=ErrorHttpStatus.SESSION_ALREADY_EXISTS,
            details={"player_id": player_id, "game_id": game_id},
        )


class SessionNotFoundException(BaseServiceException):
    def __init__(self, player_id: str, game_id: str) -> None:
        super().__init__(
            error_code=ErrorCodes.SESSION_NOT_FOUND,
            message=ErrorMessages.SESSION_NOT_FOUND,
            http_status=ErrorHttpStatus.SESSION_NOT_FOUND,
            details={"player_id": player_id, "game_id": game_id},
        )


class SessionAlreadyCompletedException(BaseServiceException):
    def __init__(self, game_session_id: str, status: str) -> None:
        super().__init__(
            error_code=ErrorCodes.SESSION_ALREADY_COMPLETED,
            message=ErrorMessages.SESSION_ALREADY_COMPLETED,
            http_status=ErrorHttpStatus.SESSION_ALREADY_COMPLETED,
            details={"game_session_id": game_session_id, "status": status},
        )


class QuestionAlreadyAnsweredException(BaseServiceException):
    def __init__(self, question_id: str) -> None:
        super().__init__(
            error_code=ErrorCodes.QUESTION_ALREADY_ANSWERED,
            message=ErrorMessages.QUESTION_ALREADY_ANSWERED,
            http_status=ErrorHttpStatus.QUESTION_ALREADY_ANSWERED,
            details={"question_id": question_id},
        )


class NoQuestionsAvailableException(BaseServiceException):
    def __init__(self) -> None:
        super().__init__(
            error_code=ErrorCodes.NO_QUESTIONS_AVAILABLE,
            message=ErrorMessages.NO_QUESTIONS_AVAILABLE,
            http_status=ErrorHttpStatus.NO_QUESTIONS_AVAILABLE,
        )
