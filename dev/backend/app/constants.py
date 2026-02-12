"""Application constants and configuration values"""

from decimal import Decimal
from enum import Enum


class QuotaLimits(Enum):
    """Quota-related limits and thresholds"""
    
    # Transfer limits
    MAX_TRANSFER_AMOUNT = Decimal("100000.00")
    MIN_TRANSFER_AMOUNT = Decimal("1.00")
    
    # MFA thresholds
    MFA_REQUIRED_THRESHOLD = Decimal("10000.00")
    
    # Approval thresholds
    APPROVAL_REQUIRED_THRESHOLD = Decimal("5000.00")
    
    # Vacation mode
    MAX_VACATION_SHARE_PERCENTAGE = Decimal("25.00")
    DEFAULT_VACATION_SHARE_PERCENTAGE = Decimal("10.00")


class APILimits:
    """API request limits"""
    
    # Rate limiting
    DEFAULT_RATE_LIMIT_REQUESTS = 100
    DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60
    
    # Pagination
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 50
    
    # Message limits
    MAX_MESSAGE_LENGTH = 50000
    MAX_MESSAGES_PER_REQUEST = 100
    
    # Request timeouts (seconds)
    LLM_REQUEST_TIMEOUT = 30
    DATABASE_QUERY_TIMEOUT = 10


class CreditConversion:
    """Credit calculation constants"""
    
    # 1 USD = 100 Org-Credits
    USD_TO_CREDITS = Decimal("100.00")
    
    # Minimum billable amount
    MIN_BILLABLE_AMOUNT = Decimal("0.01")


# API Key configuration
API_KEY_PREFIX = "tp-"
API_KEY_LENGTH = 32

# Privacy modes
PRIVACY_MODE_NORMAL = "normal"
PRIVACY_MODE_STRICT = "strict"

# User statuses
USER_STATUS_ACTIVE = "active"
USER_STATUS_VACATION = "on_vacation"
USER_STATUS_SUSPENDED = "suspended"
