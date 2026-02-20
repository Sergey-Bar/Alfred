"""
Alfred Error Management & Standardized Response Framework

[ARCHITECTURAL ROLE]
This module provides the global exception handling infrastructure for the Alfred
platform. It ensures that all errors—whether predicted (custom exceptions) or
unhandled (runtime crashes)—are transformed into a standardized, observable,
and machine-readable JSON format compatible with enterprise API standards.

"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .logging_config import get_logger, request_id_var

logger = get_logger(__name__)


# -------------------------------------------------------------------
# Core Exception Hierarchy
# -------------------------------------------------------------------


class AlfredException(Exception):
    """
    Primary Platform Exception.

    All business-logic exceptions should inherit from this class to ensure
    they are correctly intercepted by the 'alfred_exception_handler'.
    """

    def __init__(
        self,
        message: str,
        code: str = "internal_error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class QuotaExceededException(AlfredException):
    """
    Financial Guardrail Violation.

    Raised when the QuotaManager determines the user has insufficient
    credits for a requested operation. Includes JIT instructions for
    the approval workflow.
    """

    def __init__(
        self,
        message: str = "Org-Quota Exceeded: Insufficient credits available.",
        quota_remaining: float = 0,
        approval_instructions: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="quota_exceeded",
            status_code=403,
            details={"quota_remaining": quota_remaining, "approval_process": approval_instructions},
        )


class AuthenticationException(AlfredException):
    """Identity Verification Failure (Invalid API Key or SSO Token)."""

    def __init__(self, message: str = "Identity Verification Required"):
        super().__init__(message=message, code="authentication_required", status_code=401)


class AuthorizationException(AlfredException):
    """RBAC Violation (User exists but lacks required permissions)."""

    def __init__(self, message: str = "Access Denied: Insufficient Permissions"):
        super().__init__(message=message, code="permission_denied", status_code=403)


class ResourceNotFoundException(AlfredException):
    """Entity Lookup Failure (Missing User, Team, or TeamLink)."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            code="not_found",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ValidationException(AlfredException):
    """Input Sanity Check Failure (Malformed email, etc)."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code="validation_error",
            status_code=400,
            details={"field": field} if field else {},
        )


class RateLimitException(AlfredException):
    """Traffic Control Intervention."""

    def __init__(self, retry_after: int):
        super().__init__(
            message=f"Traffic Control: Rate limit exceeded. Retry in {retry_after}s.",
            code="rate_limit_exceeded",
            status_code=429,
            details={"retry_after": retry_after},
        )


class LLMProviderException(AlfredException):
    """Upstream Vendor Failure (OpenAI/Anthropic/AWS/Azure 5xx)."""

    def __init__(self, provider: str, message: str, original_error: Optional[str] = None):
        super().__init__(
            message=f"Upstream Provider Error [{provider}]: {message}",
            code="llm_provider_error",
            status_code=502,
            details={"provider": provider, "original_error": original_error},
        )


class ConfigurationException(AlfredException):
    """Platform Misconfiguration (Missing Vault ENV, etc)."""

    def __init__(self, message: str):
        super().__init__(message=message, code="configuration_error", status_code=500)


# -------------------------------------------------------------------
# Unified Response Models
# -------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """
    Standardized Error Payload.

    This schema is guaranteed for all non-2xx responses.
    The 'request_id' is critical for cross-referencing logs in production.
    """

    error: str
    code: str
    message: str
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# -------------------------------------------------------------------
# Global Middleware Interceptors
# -------------------------------------------------------------------


async def alfred_exception_handler(request: Request, exc: AlfredException) -> JSONResponse:
    """Interceptor for platform-aware business logic errors."""
    request_id = request_id_var.get()

    logger.error(
        f"Domain-Logic Error: {exc.message}",
        extra_data={
            "app_code": exc.code,
            "status": exc.status_code,
            "details": exc.details,
            "endpoint": request.url.path,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.code,
            code=exc.code,
            message=exc.message,
            request_id=request_id,
            details=exc.details if exc.details else None,
        ).model_dump(exclude_none=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Interceptor for FastAPI native HTTP exceptions."""
    request_id = request_id_var.get()

    # Normalize standard HTTP codes to platform-specific error keys
    code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        422: "unprocessable_entity",
        429: "rate_limit_exceeded",
        500: "internal_error",
        502: "bad_gateway",
    }

    code = code_map.get(exc.status_code, "unknown_error")
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    logger.warning(
        f"Framework HTTP Exception: {message}",
        extra_data={"status": exc.status_code, "path": request.url.path},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=code, code=code, message=message, request_id=request_id
        ).model_dump(exclude_none=True),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Interceptor for Pydantic schema validation failures."""
    request_id = request_id_var.get()

    # Transform internal Pydantic error list into a flattened, user-friendly format
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "msg": e["msg"], "type": e["type"]}
        for e in exc.errors()
    ]

    logger.warning(
        "Schema Validation Failed",
        extra_data={"validation_errors": errors, "path": request.url.path},
    )

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="validation_error",
            code="validation_error",
            message="The request payload contained invalid data.",
            request_id=request_id,
            details={"errors": errors},
        ).model_dump(exclude_none=True),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Standard Catch-All Handler (Safety Net).

    Ensures that unexpected Python crashes do not expose internal
    logic or secrets in the response body.
    """
    request_id = request_id_var.get()

    logger.error(
        f"Unhandled Platform Crash: {str(exc)}",
        exc_info=True,  # Critical: Captures the stack trace for Sentry/CloudWatch
        extra_data={"err_type": type(exc).__name__, "path": request.url.path},
    )

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            code="internal_error",
            message="An unexpected platform error occurred. Our engineering team has been notified.",
            request_id=request_id,
        ).model_dump(exclude_none=True),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AlfredException, alfred_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
