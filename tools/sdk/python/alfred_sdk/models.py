"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Pydantic models for Alfred SDK data types.
Root Cause:  Sprint task T184 — Python SDK.
Context:     Type-safe models for API responses.
Suitability: L2 — Standard Pydantic patterns.
──────────────────────────────────────────────────────────────
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    TEAM_ADMIN = "team_admin"
    SUPER_ADMIN = "super_admin"


class TransactionType(str, Enum):
    DEDUCTION = "deduction"
    REFUND = "refund"
    CREDIT = "credit"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    CHARGEBACK = "chargeback"


class TransferStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    AUDIT = "audit"


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    CONCLUDED = "concluded"


# ============================================================
# Core Models
# ============================================================

class User(BaseModel):
    """User account model."""
    id: str
    email: str
    name: str
    role: UserRole = UserRole.USER
    team_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None


class Team(BaseModel):
    """Team/organization model."""
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    member_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None


class Wallet(BaseModel):
    """Credit wallet model."""
    id: str
    owner_id: str
    owner_type: str  # "user" or "team"
    balance: float
    hard_limit: float
    soft_limit: float
    currency: str = "USD"
    created_at: datetime
    updated_at: Optional[datetime] = None


class Transaction(BaseModel):
    """Ledger transaction model."""
    id: str
    wallet_id: str
    type: TransactionType
    amount: float
    balance_after: float
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    idempotency_key: Optional[str] = None


class Transfer(BaseModel):
    """Credit transfer between users/teams."""
    id: str
    from_wallet_id: str
    to_wallet_id: str
    amount: float
    message: Optional[str] = None
    status: TransferStatus
    requires_approval: bool = False
    approved_by: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class APIKey(BaseModel):
    """API key for authentication."""
    id: str
    name: str
    key_prefix: str  # First 8 chars for identification
    user_id: str
    scopes: List[str] = Field(default_factory=list)
    is_active: bool = True
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime


class Provider(BaseModel):
    """LLM provider configuration."""
    id: str
    name: str
    type: str  # openai, anthropic, gemini, etc.
    is_enabled: bool = True
    priority: int = 0
    rate_limit: Optional[int] = None
    models: List[str] = Field(default_factory=list)
    health_status: str = "healthy"
    last_health_check: Optional[datetime] = None


class Policy(BaseModel):
    """Governance policy."""
    id: str
    name: str
    description: Optional[str] = None
    rules: Dict[str, Any] = Field(default_factory=dict)
    action: PolicyAction = PolicyAction.DENY
    is_active: bool = True
    is_dry_run: bool = False
    priority: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None


class Experiment(BaseModel):
    """A/B testing experiment."""
    id: str
    name: str
    description: Optional[str] = None
    status: ExperimentStatus
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    traffic_split: Dict[str, float] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime


# ============================================================
# Analytics Models
# ============================================================

class UsageReport(BaseModel):
    """Usage statistics report."""
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_tokens_input: int
    total_tokens_output: int
    total_cost: float
    by_model: List[Dict[str, Any]] = Field(default_factory=list)
    by_day: List[Dict[str, Any]] = Field(default_factory=list)
    by_user: List[Dict[str, Any]] = Field(default_factory=list)


class CostBreakdown(BaseModel):
    """Cost attribution breakdown."""
    total_cost: float
    by_provider: Dict[str, float] = Field(default_factory=dict)
    by_model: Dict[str, float] = Field(default_factory=dict)
    by_team: Dict[str, float] = Field(default_factory=dict)
    by_user: Dict[str, float] = Field(default_factory=dict)
    period_start: datetime
    period_end: datetime


class ModelPricing(BaseModel):
    """Model pricing information."""
    model: str
    provider: str
    input_price_per_1k: float
    output_price_per_1k: float
    context_window: int
    is_available: bool = True


# ============================================================
# Request/Response Models
# ============================================================

class CompletionRequest(BaseModel):
    """Chat completion request (OpenAI-compatible)."""
    model: str
    messages: List[Dict[str, str]]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    user: Optional[str] = None


class CompletionResponse(BaseModel):
    """Chat completion response."""
    id: str
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    created: int
    cost: Optional[float] = None
    cached: bool = False


class PaginatedResponse(BaseModel):
    """Paginated list response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_more: bool
