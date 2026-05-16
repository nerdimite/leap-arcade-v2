"""Application error registry.

Each error concept is defined once with its numeric code, HTTP status, and default
message so exception subclasses cannot drift across parallel registries.
"""

from dataclasses import dataclass
from http import HTTPStatus
from typing import Dict


@dataclass(frozen=True)
class ErrorDefinition:
    code: int
    http_status: HTTPStatus
    message: str


ERRORS: Dict[str, ErrorDefinition] = {
    # Auth (1xxx)
    "PLAYER_NOT_FOUND": ErrorDefinition(
        code=1001,
        http_status=HTTPStatus.NOT_FOUND,
        message="Player not found",
    ),
    "INVALID_EVENT_CODE": ErrorDefinition(
        code=1002,
        http_status=HTTPStatus.UNAUTHORIZED,
        message="Invalid event code",
    ),
    "INVALID_TOKEN": ErrorDefinition(
        code=1003,
        http_status=HTTPStatus.UNAUTHORIZED,
        message="Invalid or expired token",
    ),
    # Game flow (2xxx)
    "SESSION_ALREADY_EXISTS": ErrorDefinition(
        code=2001,
        http_status=HTTPStatus.CONFLICT,
        message="A session already exists for this game",
    ),
    "SESSION_NOT_FOUND": ErrorDefinition(
        code=2002,
        http_status=HTTPStatus.NOT_FOUND,
        message="No active session found for this game",
    ),
    "SESSION_ALREADY_COMPLETED": ErrorDefinition(
        code=2003,
        http_status=HTTPStatus.CONFLICT,
        message="Session is already completed or abandoned",
    ),
    "QUESTION_ALREADY_ANSWERED": ErrorDefinition(
        code=2004,
        http_status=HTTPStatus.CONFLICT,
        message="This question has already been answered in the current session",
    ),
    # Content / configuration (3xxx)
    "NO_QUESTIONS_AVAILABLE": ErrorDefinition(
        code=3001,
        http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        message="No unanswered questions are available",
    ),
    "INVALID_QUESTION_ID": ErrorDefinition(
        code=3002,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message="Unknown question_id for this game",
    ),
}
