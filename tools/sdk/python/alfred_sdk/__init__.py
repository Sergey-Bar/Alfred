"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Python SDK for Alfred AI Credit Governance Platform.
             Provides typed client for all Alfred API endpoints.
Root Cause:  Sprint task T184 — Python SDK for developers.
Context:     Drop-in replacement for direct API calls with
             automatic retries, rate limiting, and type hints.
Suitability: L2 — Standard SDK pattern with HTTP client.
──────────────────────────────────────────────────────────────
"""

from .client import AlfredClient
from .models import (
    User,
    Team,
    Wallet,
    Transaction,
    Transfer,
    APIKey,
    Provider,
    Policy,
    Experiment,
    UsageReport,
    CostBreakdown,
)
from .exceptions import (
    AlfredError,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    ValidationError,
    NotFoundError,
)

__version__ = "1.0.0"
__all__ = [
    "AlfredClient",
    "User",
    "Team",
    "Wallet",
    "Transaction",
    "Transfer",
    "APIKey",
    "Provider",
    "Policy",
    "Experiment",
    "UsageReport",
    "CostBreakdown",
    "AlfredError",
    "AuthenticationError",
    "QuotaExceededError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
]
