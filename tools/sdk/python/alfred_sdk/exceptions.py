"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Alfred SDK exception classes.
Root Cause:  Sprint task T184 — Python SDK.
Context:     Typed exceptions for API error handling.
Suitability: L2 — Standard exception hierarchy.
──────────────────────────────────────────────────────────────
"""

from typing import Optional, Dict, Any


class AlfredError(Exception):
    """Base exception for all Alfred SDK errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(AlfredError):
    """Raised when API authentication fails (401)."""
    pass


class AuthorizationError(AlfredError):
    """Raised when access is denied (403)."""
    pass


class NotFoundError(AlfredError):
    """Raised when a resource is not found (404)."""
    pass


class ValidationError(AlfredError):
    """Raised when request validation fails (422)."""
    
    def __init__(
        self,
        message: str,
        errors: Optional[list] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.errors = errors or []


class QuotaExceededError(AlfredError):
    """Raised when AI credit quota is exceeded (429 or custom)."""
    
    def __init__(
        self,
        message: str,
        current_balance: Optional[float] = None,
        required: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.current_balance = current_balance
        self.required = required


class RateLimitError(AlfredError):
    """Raised when rate limit is hit (429)."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ProviderError(AlfredError):
    """Raised when an LLM provider returns an error."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.provider = provider


class CircuitBreakerError(AlfredError):
    """Raised when circuit breaker is open."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        recovery_time: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.provider = provider
        self.recovery_time = recovery_time


class PolicyViolationError(AlfredError):
    """Raised when a request violates a governance policy."""
    
    def __init__(
        self,
        message: str,
        policy_id: Optional[str] = None,
        policy_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.policy_id = policy_id
        self.policy_name = policy_name
