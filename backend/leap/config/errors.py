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
    "PICTURE_PUZZLE_ALREADY_RESOLVED": ErrorDefinition(
        code=2009,
        http_status=HTTPStatus.CONFLICT,
        message="This puzzle is already resolved for this session",
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
    "INVALID_PICTURE_PUZZLE_ID": ErrorDefinition(
        code=3012,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message="Unknown puzzle_id for this game",
    ),
    "NO_WIKI_ROUNDS_AVAILABLE": ErrorDefinition(
        code=3003,
        http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        message="No wiki rounds are configured for this event",
    ),
    "NO_PICTURE_PUZZLES_AVAILABLE": ErrorDefinition(
        code=3013,
        http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        message="No picture puzzles are configured for this event",
    ),
    "WIKI_PUZZLE_NOT_ACTIVE": ErrorDefinition(
        code=2005,
        http_status=HTTPStatus.CONFLICT,
        message="No active wiki puzzle attempt for navigation",
    ),
    "WIKI_PUZZLE_TIMER_EXPIRED": ErrorDefinition(
        code=2006,
        http_status=HTTPStatus.CONFLICT,
        message="Wiki puzzle time limit has elapsed",
    ),
    "WIKI_BACK_BUTTON_DISABLED": ErrorDefinition(
        code=2007,
        http_status=HTTPStatus.FORBIDDEN,
        message="Wiki in-game back navigation is disabled",
    ),
    "WIKI_NO_PREVIOUS_PAGE": ErrorDefinition(
        code=2008,
        http_status=HTTPStatus.CONFLICT,
        message="There is no previous wiki page to return to",
    ),
}
