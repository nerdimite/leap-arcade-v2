"""Application error registry: numeric codes, HTTP status, and default messages.

Every name on ``ErrorCodes`` must exist on ``ErrorHttpStatus`` and ``ErrorMessages``
with the same attribute name (triple parity). Add new codes here first, then add
the matching exception subclass in ``leap/service/exceptions.py``.

Code ranges:
- 1xxx — Auth
- 2xxx — Game flow / sessions
- 3xxx — Content / configuration
"""

from http import HTTPStatus


class ErrorCodes:
    # Auth (1xxx)
    PLAYER_NOT_FOUND = 1001
    INVALID_EVENT_CODE = 1002
    INVALID_TOKEN = 1003

    # Game flow (2xxx)
    SESSION_ALREADY_EXISTS = 2001
    SESSION_NOT_FOUND = 2002
    SESSION_ALREADY_COMPLETED = 2003
    QUESTION_ALREADY_ANSWERED = 2004

    # Content / configuration (3xxx)
    NO_QUESTIONS_AVAILABLE = 3001


class ErrorHttpStatus:
    # Auth
    PLAYER_NOT_FOUND = HTTPStatus.NOT_FOUND
    INVALID_EVENT_CODE = HTTPStatus.UNAUTHORIZED
    INVALID_TOKEN = HTTPStatus.UNAUTHORIZED

    # Game flow
    SESSION_ALREADY_EXISTS = HTTPStatus.CONFLICT
    SESSION_NOT_FOUND = HTTPStatus.NOT_FOUND
    SESSION_ALREADY_COMPLETED = HTTPStatus.CONFLICT
    QUESTION_ALREADY_ANSWERED = HTTPStatus.CONFLICT

    # Content / configuration
    NO_QUESTIONS_AVAILABLE = HTTPStatus.SERVICE_UNAVAILABLE


class ErrorMessages:
    # Auth
    PLAYER_NOT_FOUND = "Player not found"
    INVALID_EVENT_CODE = "Invalid event code"
    INVALID_TOKEN = "Invalid or expired token"

    # Game flow
    SESSION_ALREADY_EXISTS = "A session already exists for this game"
    SESSION_NOT_FOUND = "No active session found for this game"
    SESSION_ALREADY_COMPLETED = "Session is already completed or abandoned"
    QUESTION_ALREADY_ANSWERED = "This question has already been answered in the current session"

    # Content / configuration
    NO_QUESTIONS_AVAILABLE = "No unanswered questions are available"
