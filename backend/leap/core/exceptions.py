"""Core exception types shared across infrastructure and service layers."""

from http import HTTPStatus
from typing import Any, Dict, Optional

from leap.config.errors import ERRORS


class BaseServiceException(Exception):
    """Base exception rendered by the global FastAPI exception handler."""

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


class InvalidTokenException(BaseServiceException):
    def __init__(self, reason: Optional[str] = None) -> None:
        error = ERRORS["INVALID_TOKEN"]
        super().__init__(
            error_code=error.code,
            message=reason or error.message,
            http_status=error.http_status,
        )
