"""Domain exceptions raised by the service layer.

Routes never raise ``HTTPException`` — services raise these instead.
"""

from leap.config.errors import ERRORS
from leap.core.exceptions import BaseServiceException, InvalidTokenException


class PlayerNotFoundException(BaseServiceException):
    def __init__(self, corp_id: str) -> None:
        error = ERRORS["PLAYER_NOT_FOUND"]
        super().__init__(
            error_code=error.code,
            message=f"{error.message}: {corp_id}",
            http_status=error.http_status,
            details={"corp_id": corp_id},
        )


class InvalidEventCodeException(BaseServiceException):
    def __init__(self) -> None:
        error = ERRORS["INVALID_EVENT_CODE"]
        super().__init__(
            error_code=error.code,
            message=error.message,
            http_status=error.http_status,
        )


class SessionAlreadyExistsException(BaseServiceException):
    def __init__(self, player_id: str, game_id: str) -> None:
        error = ERRORS["SESSION_ALREADY_EXISTS"]
        super().__init__(
            error_code=error.code,
            message=error.message,
            http_status=error.http_status,
            details={"player_id": player_id, "game_id": game_id},
        )


class SessionNotFoundException(BaseServiceException):
    def __init__(self, player_id: str, game_id: str) -> None:
        error = ERRORS["SESSION_NOT_FOUND"]
        super().__init__(
            error_code=error.code,
            message=error.message,
            http_status=error.http_status,
            details={"player_id": player_id, "game_id": game_id},
        )


class SessionAlreadyCompletedException(BaseServiceException):
    def __init__(self, game_session_id: str, status: str) -> None:
        error = ERRORS["SESSION_ALREADY_COMPLETED"]
        super().__init__(
            error_code=error.code,
            message=error.message,
            http_status=error.http_status,
            details={"game_session_id": game_session_id, "status": status},
        )


class QuestionAlreadyAnsweredException(BaseServiceException):
    def __init__(self, question_id: str) -> None:
        error = ERRORS["QUESTION_ALREADY_ANSWERED"]
        super().__init__(
            error_code=error.code,
            message=error.message,
            http_status=error.http_status,
            details={"question_id": question_id},
        )


class NoQuestionsAvailableException(BaseServiceException):
    def __init__(self) -> None:
        error = ERRORS["NO_QUESTIONS_AVAILABLE"]
        super().__init__(
            error_code=error.code,
            message=error.message,
            http_status=error.http_status,
        )


class InvalidQuestionIdException(BaseServiceException):
    def __init__(self, question_id: str) -> None:
        error = ERRORS["INVALID_QUESTION_ID"]
        super().__init__(
            error_code=error.code,
            message=error.message,
            http_status=error.http_status,
            details={"question_id": question_id},
        )
