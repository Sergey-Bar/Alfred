"""
Alfred Error Management & Standardized Response Framework

[ARCHITECTURAL ROLE]
This module provides the global exception handling infrastructure for the Alfred
platform. It ensures that all errors—whether predicted (custom exceptions) or
unhandled (runtime crashes)—are transformed into a standardized, observable,
and machine-readable JSON format compatible with enterprise API standards.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This module centralizes all error handling, custom exceptions, and error response schemas. It ensures all errors are logged, observable, and returned in a consistent JSON format with request IDs.
# Why: Standardized error handling improves debuggability, compliance, and user experience.
# Root Cause: Without a unified error layer, APIs leak stack traces or return inconsistent error payloads.
# Context: All exceptions in the platform should be routed through these handlers. Future: consider error code registry or i18n error messages.
# Model Suitability: For error handling patterns, GPT-4.1 is sufficient; for advanced observability, a more advanced model may be preferred.
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Base class for all business-logic exceptions, ensures custom error codes and details are available for handlers.
    # Why: Enables fine-grained error handling and observability.
    # Root Cause: Python's built-in exceptions lack structured metadata for APIs.
    # Context: All custom exceptions should inherit from this class.
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Raised when quota/credit limits are exceeded, includes approval workflow details.
    # Why: Allows API to communicate quota status and next steps to clients.
    # Root Cause: Quota enforcement is a core business rule.
    # Context: Used by quota manager and governance logic.
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Raised for failed authentication (API key, SSO, etc).
    # Why: Ensures 401 responses are standardized.
    # Root Cause: Authentication failures must be clearly communicated.
    # Context: Used by auth middleware and routers.
    """Identity Verification Failure (Invalid API Key or SSO Token)."""

    def __init__(self, message: str = "Identity Verification Required"):
        super().__init__(message=message, code="authentication_required", status_code=401)


class AuthorizationException(AlfredException):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Raised for RBAC/permission failures.
    # Why: Ensures 403 responses are standardized.
    # Root Cause: Authorization failures must be clearly communicated.
    # Context: Used by RBAC and governance logic.
    """RBAC Violation (User exists but lacks required permissions)."""

    def __init__(self, message: str = "Access Denied: Insufficient Permissions"):
        super().__init__(message=message, code="permission_denied", status_code=403)


class ResourceNotFoundException(AlfredException):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Raised when a requested entity (user, team, etc) is not found.
    # Why: Ensures 404 responses are standardized.
    # Root Cause: Entity lookup failures are common in APIs.
    # Context: Used by all resource lookup logic.
    """Entity Lookup Failure (Missing User, Team, or TeamLink)."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            code="not_found",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ValidationException(AlfredException):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Raised for input validation errors (malformed fields, etc).
    # Why: Ensures 400 responses are standardized.
    # Root Cause: Input validation is a core API concern.
    # Context: Used by schema and business logic validation.
    """Input Sanity Check Failure (Malformed email, etc)."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code="validation_error",
            status_code=400,
            details={"field": field} if field else {},
        )


class RateLimitException(AlfredException):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Raised when rate limiting is triggered.
    # Why: Ensures 429 responses are standardized.
    # Root Cause: Rate limiting is critical for abuse prevention.
    # Context: Used by traffic control middleware.
    """Traffic Control Intervention."""

    def __init__(self, retry_after: int):
        super().__init__(
            message=f"Traffic Control: Rate limit exceeded. Retry in {retry_after}s.",
            code="rate_limit_exceeded",
            status_code=429,
            details={"retry_after": retry_after},
        )


class LLMProviderException(AlfredException):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Raised for upstream LLM provider errors (OpenAI, Anthropic, etc).
    # Why: Ensures 502 responses are standardized.
    # Root Cause: Upstream failures must be surfaced to clients.
    # Context: Used by proxy and provider logic.
    """Upstream Vendor Failure (OpenAI/Anthropic/AWS/Azure 5xx)."""

    def __init__(self, provider: str, message: str, original_error: Optional[str] = None):
        super().__init__(
            message=f"Upstream Provider Error [{provider}]: {message}",
            code="llm_provider_error",
            status_code=502,
            details={"provider": provider, "original_error": original_error},
        )


class ConfigurationException(AlfredException):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Raised for platform misconfiguration (missing env, etc).
    # Why: Ensures 500 responses are standardized.
    # Root Cause: Misconfiguration is a common deployment issue.
    # Context: Used by startup and config logic.
    """Platform Misconfiguration (Missing Vault ENV, etc)."""

    def __init__(self, message: str):
        super().__init__(message=message, code="configuration_error", status_code=500)


# -------------------------------------------------------------------
# Unified Response Models
# -------------------------------------------------------------------


class ErrorResponse(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Standardized error response schema for all non-2xx API responses.
    # Why: Ensures clients can reliably parse and correlate errors.
    # Root Cause: Inconsistent error payloads make debugging and automation difficult.
    # Context: Used by all exception handlers.
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Handles all custom business-logic exceptions, logs details, returns standardized error response.
    # Why: Ensures all business errors are observable and machine-readable.
    # Root Cause: Unhandled exceptions would leak stack traces or return 500s.
    # Context: Registered globally in setup_exception_handlers().
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Handles FastAPI's built-in HTTPException, normalizes error codes, logs, and returns standard error response.
    # Why: Ensures framework errors are observable and consistent.
    # Root Cause: FastAPI's default handler returns inconsistent payloads.
    # Context: Registered globally in setup_exception_handlers().
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Handles Pydantic schema validation errors, flattens error list, logs, and returns standard error response.
    # Why: Ensures validation errors are user-friendly and observable.
    # Root Cause: Pydantic's default error format is not user-friendly.
    # Context: Registered globally in setup_exception_handlers().
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Catch-all handler for unexpected exceptions, logs stack trace, returns generic error message.
    # Why: Prevents leaking internal details and ensures all errors are observable.
    # Root Cause: Unhandled exceptions would expose stack traces or crash the app.
    # Context: Registered globally in setup_exception_handlers().
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Registers all global exception handlers with the FastAPI app instance.
    # Why: Ensures all errors are routed through standardized handlers.
    # Root Cause: FastAPI requires explicit registration of handlers.
    # Context: Call once at app startup.
    app.add_exception_handler(AlfredException, alfred_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
