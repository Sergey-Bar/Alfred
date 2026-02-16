"""
Alfred - Enterprise AI Credit Governance Platform
System Constants & Operational Thresholds

[ARCHITECTURAL ROLE]
Centralizes hard-coded values and business logic boundaries. Using a centralized
constants module prevents 'Magic Number' anti-patterns and ensures consistency
across the logic, middleware, and API layers.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This module centralizes all business logic constants, enums, and system strings for quota, API, and finance.
# Why: Prevents magic numbers, improves maintainability, and enforces consistency across the codebase.
# Root Cause: Scattered constants lead to bugs and inconsistent business logic.
# Context: All hard-coded values should be defined here. Future: consider config-driven or DB-driven limits.
# Model Suitability: For constants patterns, GPT-4.1 is sufficient; for dynamic policy, a more advanced model may be preferred.
"""

from decimal import Decimal
from enum import Enum


class QuotaLimits(Enum):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Enum for all quota-related business logic thresholds (transfer, MFA, approval, vacation share).
    # Why: Ensures all quota logic uses the same boundaries.
    # Root Cause: Hard-coded values in logic are error-prone.
    # Context: Used by governance and quota modules.
    """
    Business Logic Safeguards.

    Defines the financial boundaries of the platform. These values drive the
    automated decision-making in the QuotaManager.
    """

    # Liquidity Transfer Constraints
    MAX_TRANSFER_AMOUNT = Decimal("100000.00")
    MIN_TRANSFER_AMOUNT = Decimal("1.00")

    # Risk-Based Authentication Thresholds
    # Transfers above this amount trigger multi-factor verification.
    MFA_REQUIRED_THRESHOLD = Decimal("10000.00")

    # Governance Escalation
    # Automated allocation stops at this point; human review is mandatory.
    APPROVAL_REQUIRED_THRESHOLD = Decimal("5000.00")

    # Elastic Pool Parameters
    MAX_VACATION_SHARE_PERCENTAGE = Decimal("25.00")
    DEFAULT_VACATION_SHARE_PERCENTAGE = Decimal("10.00")


class APILimits:
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Class for all API and traffic engineering limits (rate, pagination, payload, timeouts).
    # Why: Prevents resource exhaustion and enforces API contract.
    # Root Cause: Inconsistent limits cause reliability and UX issues.
    # Context: Used by routers, middleware, and dashboard.
    """
    Inbound Traffic & Performance Constraints.

    Ensures the reliability of the Gateway by preventing resource exhaustion
    and malformed payload processing.
    """

    # Traffic Engineering Defaults
    DEFAULT_RATE_LIMIT_REQUESTS = 100
    DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60

    # UI & API Pagination
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 50

    # Payload Density Limits
    MAX_MESSAGE_LENGTH = 50000
    MAX_MESSAGES_PER_REQUEST = 100

    # Lifecycle Timeouts (Seconds)
    # Prevents 'Hanging Requests' from tying up worker threads.
    LLM_REQUEST_TIMEOUT = 30
    DATABASE_QUERY_TIMEOUT = 10


class CreditConversion:
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Class for all financial conversion rates and billing floors.
    # Why: Ensures all credit/cost calculations use the same logic.
    # Root Cause: Scattered conversion logic leads to billing errors.
    # Context: Used by quota, billing, and analytics modules.
    """
    Financial Quantization Parameters.

    Defines the relationship between external vendor cost (USD)
    and internal organizational value (Org-Credits).
    """

    # The Exchange Rate: 1 USD = 100 Internal Credits
    USD_TO_CREDITS = Decimal("100.00")

    # The 'Micro-Billing' floor
    MIN_BILLABLE_AMOUNT = Decimal("0.01")


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Canonical system strings for API keys, privacy modes, and user states.
# Why: Prevents typos and enforces consistency in string-based logic.
# Root Cause: Typos in string literals cause subtle bugs.
# Context: Used throughout the platform for identity and state management.
# --- Canonical System Strings ---

# Cryptographic Token Formatting
API_KEY_PREFIX = "tp-"
API_KEY_LENGTH = 32

# Observability Modes
PRIVACY_MODE_NORMAL = "normal"
PRIVACY_MODE_STRICT = "strict"

# Actor Lifecycle States
USER_STATUS_ACTIVE = "active"
USER_STATUS_VACATION = "on_vacation"
USER_STATUS_SUSPENDED = "suspended"
