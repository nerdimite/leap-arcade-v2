from http import HTTPStatus
from typing import Any


class BaseServiceException(Exception):
    """Base exception for all service layer errors.

    Converted to a JSON error response by the FastAPI exception handler.
    Never raise HTTPException from a service — raise a subclass of this instead.
    """

    def __init__(
        self,
        message: str,
        error_code: int,
        http_status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": False,
            "message": self.message,
            "code": self.error_code,
            "http_status": self.http_status.value,
            "error": self.details,
        }


class JobNotFoundException(BaseServiceException):
    def __init__(self, job_id: str) -> None:
        super().__init__(
            message=f"Job not found: {job_id}",
            error_code=4001,
            http_status=HTTPStatus.NOT_FOUND,
            details={"job_id": job_id},
        )


class JobNotCancellableException(BaseServiceException):
    def __init__(self, job_id: str, current_status: str) -> None:
        super().__init__(
            message=f"Job {job_id} cannot be cancelled in status: {current_status}",
            error_code=4002,
            http_status=HTTPStatus.CONFLICT,
            details={"job_id": job_id, "current_status": current_status},
        )


class ExtractionFailedException(BaseServiceException):
    def __init__(self, job_id: str, reason: str) -> None:
        super().__init__(
            message=f"Extraction failed for job {job_id}: {reason}",
            error_code=5001,
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            details={"job_id": job_id, "reason": reason},
        )
