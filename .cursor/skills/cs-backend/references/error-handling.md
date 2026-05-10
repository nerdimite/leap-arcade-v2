# Error Handling

## Architecture

Three tiers work together:

1. **`config/errors.py`** — Error codes, HTTP statuses, messages (constants)
2. **`service/exceptions.py`** — `BaseServiceException` hierarchy
3. **`main.py`** — Global exception handlers

## Error Configuration

Three parallel classes in `config/errors.py`:

```python
from http import HTTPStatus

class ErrorCodes:
    # Common: 4000-4099
    RESOURCE_NOT_FOUND = 4001
    VALIDATION_ERROR = 4002
    UNAUTHORIZED = 4003
    FORBIDDEN = 4004
    INTERNAL_ERROR = 4005

    # Auth: 4200-4299
    INVALID_TOKEN = 4200
    EXPIRED_TOKEN = 4201
    MISSING_TOKEN = 4202

    # Domain-specific: 4300+ (assign ranges per domain)
    ORDER_NOT_FOUND = 4300
    ORDER_ALREADY_CANCELLED = 4301
    INVALID_ORDER_AMOUNT = 4302

class ErrorHttpStatus:
    RESOURCE_NOT_FOUND = HTTPStatus.NOT_FOUND
    VALIDATION_ERROR = HTTPStatus.UNPROCESSABLE_ENTITY
    UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
    FORBIDDEN = HTTPStatus.FORBIDDEN
    INTERNAL_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR
    INVALID_TOKEN = HTTPStatus.UNAUTHORIZED
    EXPIRED_TOKEN = HTTPStatus.UNAUTHORIZED
    MISSING_TOKEN = HTTPStatus.UNAUTHORIZED
    ORDER_NOT_FOUND = HTTPStatus.NOT_FOUND
    ORDER_ALREADY_CANCELLED = HTTPStatus.CONFLICT
    INVALID_ORDER_AMOUNT = HTTPStatus.BAD_REQUEST

class ErrorMessages:
    RESOURCE_NOT_FOUND = "Resource not found"
    VALIDATION_ERROR = "Validation failed"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Access denied"
    INTERNAL_ERROR = "Internal server error"
    INVALID_TOKEN = "Invalid authentication token"
    EXPIRED_TOKEN = "Authentication token has expired"
    MISSING_TOKEN = "Authentication token is required"
    ORDER_NOT_FOUND = "Order not found"
    ORDER_ALREADY_CANCELLED = "Order has already been cancelled"
    INVALID_ORDER_AMOUNT = "Order amount must be positive"
```

## Base Exception

```python
class BaseServiceException(Exception):
    def __init__(self, error_code: int, message: str, http_status: HTTPStatus, details: dict = None):
        self.error_code = error_code
        self.message = message
        self.http_status = http_status
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "success": False,
            "message": self.message,
            "code": self.error_code,
            "http_status": self.http_status.value,
            "error": self.details,
        }
```

## Domain Exception Pattern

Each domain has a `<domain>_exceptions.py` file:

```python
class OrderNotFoundException(BaseServiceException):
    def __init__(self, order_id: str):
        super().__init__(
            error_code=ErrorCodes.ORDER_NOT_FOUND,
            message=ErrorMessages.ORDER_NOT_FOUND,
            http_status=ErrorHttpStatus.ORDER_NOT_FOUND,
            details={"order_id": order_id},
        )

class OrderAlreadyCancelledException(BaseServiceException):
    def __init__(self, order_id: str):
        super().__init__(
            error_code=ErrorCodes.ORDER_ALREADY_CANCELLED,
            message=ErrorMessages.ORDER_ALREADY_CANCELLED,
            http_status=ErrorHttpStatus.ORDER_ALREADY_CANCELLED,
            details={"order_id": order_id},
        )
```

**Pattern:**
1. One exception class per error condition
2. Constructor takes resource identifiers
3. References constants from `config/errors.py`
4. Caught by global `BaseServiceException` handler

## Global Exception Handlers

Registered in `main.py`:

```python
@app.exception_handler(BaseServiceException)
async def service_exception_handler(request: Request, exc: BaseServiceException):
    return JSONResponse(
        status_code=exc.http_status.value,
        content=exc.to_dict(),
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "code": ErrorCodes.VALIDATION_ERROR,
            "http_status": 422,
            "error": {"details": exc.errors()},
        },
    )

@app.exception_handler(PermissionError)
async def permission_handler(request: Request, exc: PermissionError):
    return JSONResponse(status_code=403, content={...})

@app.exception_handler(Exception)
async def general_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc))
    return JSONResponse(status_code=500, content={...})
```

## Auth Exceptions

Use classmethod factories for cleaner instantiation:

```python
class AuthenticationException(BaseServiceException):
    @classmethod
    def unauthorized(cls):
        return cls(ErrorCodes.UNAUTHORIZED, ErrorMessages.UNAUTHORIZED, ErrorHttpStatus.UNAUTHORIZED)

    @classmethod
    def expired_token(cls):
        return cls(ErrorCodes.EXPIRED_TOKEN, ErrorMessages.EXPIRED_TOKEN, ErrorHttpStatus.EXPIRED_TOKEN)
```

## Adding Errors for a New Domain

1. Add error codes to `ErrorCodes` (assign a range, e.g., 4400-4499)
2. Add matching HTTP statuses to `ErrorHttpStatus`
3. Add matching messages to `ErrorMessages`
4. Create `<domain>_exceptions.py` with one class per error
5. Raise exceptions from the service layer
