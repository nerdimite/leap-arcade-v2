# Exception Hierarchy Scaffold

## app/service/exceptions.py

```python
from http import HTTPStatus
from typing import Any, Dict, Optional


class BaseServiceException(Exception):
    """Base exception for all service-layer errors."""

    def __init__(
        self,
        error_code: int,
        message: str,
        http_status: HTTPStatus,
        details: Optional[Dict[str, Any]] = None,
    ):
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


class AuthorizationException(BaseServiceException):
    """Raised when ABAC denies access."""

    def __init__(self, message: str = "Access denied", details: Optional[dict] = None):
        super().__init__(
            error_code=4004,
            message=message,
            http_status=HTTPStatus.FORBIDDEN,
            details=details,
        )


class PaginationError(BaseServiceException):
    """Raised for invalid pagination requests."""

    def __init__(self, page: int, total_pages: int):
        super().__init__(
            error_code=4002,
            message=f"Page {page} exceeds total pages {total_pages}",
            http_status=HTTPStatus.BAD_REQUEST,
            details={"page": page, "total_pages": total_pages},
        )
```

## Example Domain Exceptions

```python
# app/service/item/item_exceptions.py
from app.config.errors import ErrorCodes, ErrorHttpStatus, ErrorMessages
from app.service.exceptions import BaseServiceException


class ItemNotFoundException(BaseServiceException):
    def __init__(self, item_id: str):
        super().__init__(
            error_code=ErrorCodes.ITEM_NOT_FOUND,
            message=ErrorMessages.ITEM_NOT_FOUND,
            http_status=ErrorHttpStatus.ITEM_NOT_FOUND,
            details={"item_id": item_id},
        )


class ItemAlreadyExistsException(BaseServiceException):
    def __init__(self, name: str):
        super().__init__(
            error_code=ErrorCodes.ITEM_ALREADY_EXISTS,
            message=ErrorMessages.ITEM_ALREADY_EXISTS,
            http_status=ErrorHttpStatus.ITEM_ALREADY_EXISTS,
            details={"name": name},
        )


class InvalidItemOperationException(BaseServiceException):
    def __init__(self, reason: str):
        super().__init__(
            error_code=ErrorCodes.INVALID_ITEM_OPERATION,
            message=reason,
            http_status=ErrorHttpStatus.INVALID_ITEM_OPERATION,
        )
```

## Pattern

1. One exception class per distinct error condition
2. Constructor takes the identifying resource parameter(s)
3. References error codes/messages/statuses from `config/errors.py`
4. All caught by the global `BaseServiceException` handler in `main.py`
