"""
Alfred Custom Exceptions and Error Handlers
Provides consistent error responses across the API.
"""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from .logging_config import get_logger, request_id_var

logger = get_logger(__name__)


# -------------------------------------------------------------------
# Custom Exceptions
# -------------------------------------------------------------------

class AlfredException(Exception):
    """Base exception for all Alfred errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "internal_error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class QuotaExceededException(AlfredException):
    """Raised when user quota is exceeded."""
    
    def __init__(
        self,
        message: str = "Quota exceeded",
        quota_remaining: float = 0,
        approval_instructions: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="quota_exceeded",
            status_code=403,
            details={
                "quota_remaining": quota_remaining,
                "approval_process": approval_instructions
            }
        )


class AuthenticationException(AlfredException):
    """Raised for authentication failures."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="authentication_required",
            status_code=401
        )


class AuthorizationException(AlfredException):
    """Raised for authorization failures."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            code="permission_denied",
            status_code=403
        )


class ResourceNotFoundException(AlfredException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            code="not_found",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ValidationException(AlfredException):
    """Raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code="validation_error",
            status_code=400,
            details={"field": field} if field else {}
        )


class RateLimitException(AlfredException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int):
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            code="rate_limit_exceeded",
            status_code=429,
            details={"retry_after": retry_after}
        )


class LLMProviderException(AlfredException):
    """Raised for LLM provider errors."""
    
    def __init__(self, provider: str, message: str, original_error: Optional[str] = None):
        super().__init__(
            message=f"LLM provider error ({provider}): {message}",
            code="llm_provider_error",
            status_code=502,
            details={
                "provider": provider,
                "original_error": original_error
            }
        )


class ConfigurationException(AlfredException):
    """Raised for configuration errors."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="configuration_error",
            status_code=500
        )


# -------------------------------------------------------------------
# Error Response Models
# -------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    code: str
    message: str
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# -------------------------------------------------------------------
# Exception Handlers
# -------------------------------------------------------------------

async def alfred_exception_handler(
    request: Request,
    exc: AlfredException
) -> JSONResponse:
    """Handle custom Alfred exceptions."""
    request_id = request_id_var.get()
    
    logger.error(
        f"AlfredException: {exc.message}",
        extra_data={
            "code": exc.code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.code,
            code=exc.code,
            message=exc.message,
            request_id=request_id,
            details=exc.details if exc.details else None
        ).model_dump(exclude_none=True)
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Handle FastAPI HTTPExceptions."""
    request_id = request_id_var.get()
    
    # Map common status codes to error codes
    code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "unprocessable_entity",
        429: "rate_limit_exceeded",
        500: "internal_error",
        502: "bad_gateway",
        503: "service_unavailable",
    }
    
    code = code_map.get(exc.status_code, "error")
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    
    logger.warning(
        f"HTTPException: {message}",
        extra_data={
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=code,
            code=code,
            message=message,
            request_id=request_id
        ).model_dump(exclude_none=True)
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    request_id = request_id_var.get()
    
    # Extract validation errors
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {len(errors)} errors",
        extra_data={
            "errors": errors,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="validation_error",
            code="validation_error",
            message="Request validation failed",
            request_id=request_id,
            details={"errors": errors}
        ).model_dump(exclude_none=True)
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = request_id_var.get()
    
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra_data={
            "exception_type": type(exc).__name__,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_error",
            code="internal_error",
            message="An unexpected error occurred. Please try again later.",
            request_id=request_id
        ).model_dump(exclude_none=True)
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(AlfredException, alfred_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
