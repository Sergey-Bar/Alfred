"""
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4 (Critical - Security)
Logic:       Enabled Pydantic strict mode across all input schemas
             to prevent type coercion attacks and subtle injection
             vectors. Strict mode rejects type coercion (e.g., "123"
             → 123), enforcing exact type matching.
Root Cause:  T218 - Input validation hardening required for production
             security. Type coercion can conceal injection payloads.
Context:     All user-facing input schemas now use ConfigDict(strict=True).
             Response schemas remain lenient for backward compatibility.
Suitability: L4 - Security-critical input validation requires maximum
             rigor. Claude Opus 4.6 selected for zero-defect output.
──────────────────────────────────────────────────────────────
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from .models import ProjectPriority


class ReportFormat(str, Enum):
    csv = "csv"
    pdf = "pdf"
    excel = "excel"


class CustomReportCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    description: Optional[str] = None
    query: str  # SQL or DSL for ad-hoc analytics
    schedule: Optional[str] = None  # cron or interval
    format: ReportFormat = ReportFormat.csv
    recipients: Optional[List[str]] = None  # emails for scheduled delivery


class CustomReportResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    query: str
    schedule: Optional[str]
    format: ReportFormat
    recipients: Optional[List[str]]
    created_at: datetime
    last_run: Optional[datetime]
    status: Optional[str]


class CustomReportRunRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    params: Optional[dict] = None
    format: Optional[ReportFormat] = None


class CustomReportRunResult(BaseModel):
    report_id: str
    run_id: str
    status: str
    output_url: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime]
    error: Optional[str] = None


class UserCreate(BaseModel):
    """
    Onboarding Identity Schema.

    Includes runtime guardrails against common injection vectors.
    """

    model_config = ConfigDict(strict=True)

    email: str
    name: str
    personal_quota: Optional[Decimal] = Decimal("1000.00")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Sanity check for RFC compliance and SQLi prevention."""
        import re

        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Malformed Email: Does not match standard RFC patterns.")
        if any(c in v for c in ("'", '"', ";", "--")):
            raise ValueError("Security Policy: Potential SQL injection detected in email string.")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Defensive scrubbing of display names to prevent Reflected XSS."""
        import re

        # Remove active scripts and high-risk HTML segments
        v = re.sub(r"<script.*?>.*?</script>", "", v, flags=re.IGNORECASE)
        v = re.sub(r"<.*?>", "", v)
        return v.strip()


class UserResponse(BaseModel):
    """Normalized User Profile for administrative audit."""

    id: str
    email: str
    name: str
    status: str
    personal_quota: Decimal
    used_tokens: Decimal
    available_quota: Decimal
    default_priority: str
    preferences: Optional[dict] = None


class UserCreateResponse(UserResponse):
    """Normalized User Profile with secret key."""

    api_key: str


class UserUpdate(BaseModel):
    """Partial State Modification for Users."""

    model_config = ConfigDict(strict=True)

    name: Optional[str] = None
    personal_quota: Optional[Decimal] = None
    status: Optional[str] = None


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(strict=True)

    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[dict] = None


class ApiKeyResponse(BaseModel):
    """Ephemeral Secret Delivery (Only shown once)."""

    api_key: str
    message: str


# --- Team Schemas ---


class TeamCreate(BaseModel):
    """Organization Team Provisioning."""

    model_config = ConfigDict(strict=True)

    name: str
    description: Optional[str] = None
    common_pool: Optional[Decimal] = Decimal("10000.00")


class TeamResponse(BaseModel):
    """Team Capitalization Stats."""

    id: str
    name: str
    description: Optional[str]
    common_pool: Decimal
    used_pool: Decimal
    available_pool: Decimal
    member_count: int


class TeamUpdate(BaseModel):
    """Partial State Modification for Teams."""

    model_config = ConfigDict(strict=True)

    name: Optional[str] = None
    description: Optional[str] = None
    common_pool: Optional[Decimal] = None


class TeamMember(BaseModel):
    id: str
    name: str
    email: str
    is_admin: bool


class AddMemberByEmailRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    email: str
    is_admin: bool = False


# --- Governance Schemas ---


class ApprovalRequestCreate(BaseModel):
    """
    Capital Expenditure Request.

    Allows users to justify 'Quota Injections' for specific high-priority projects.
    """

    model_config = ConfigDict(strict=True)

    requested_credits: Optional[Decimal] = None
    requested_amount: Optional[Decimal] = None
    reason: str
    priority: Optional[ProjectPriority] = ProjectPriority.HIGH


class ApprovalResponse(BaseModel):
    """Workflow Status for Quota Requests."""

    id: str
    status: str
    requested_credits: Decimal
    approved_credits: Optional[Decimal]
    reason: str
    created_at: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class TokenTransferRequest(BaseModel):
    """Request body for credit reallocation.

    Supports either `recipient_email` or `to_user_id` (frontend uses `to_user_id`).
    """

    model_config = ConfigDict(strict=True)

    recipient_email: Optional[str] = None
    to_user_id: Optional[str] = None
    amount: Decimal
    message: Optional[str] = None
    reason: Optional[str] = None


class TokenTransferResponse(BaseModel):
    """Response for credit reallocation."""

    transfer_id: str
    sender_name: str
    recipient_name: str
    amount: Decimal
    message: Optional[str] = None
    sender_remaining_quota: Decimal
    recipient_new_quota: Decimal
    timestamp: str


class LeaderboardResponse(BaseModel):
    """Gamified Engineering KPI."""

    rank: int
    user_id: str
    user_name: str
    total_requests: int
    avg_efficiency_score: Decimal
    total_cost_credits: Decimal


class QuotaStatusResponse(BaseModel):
    """Real-time Financial Position."""

    personal_quota: Decimal
    used_tokens: Decimal
    available_quota: Decimal
    team_pool_available: Decimal
    vacation_share_available: Decimal
    status: str


# --- Dashboard & Analytics Schemas ---


class OverviewStats(BaseModel):
    """The 'C-Suite' View: System-wide health metrics."""

    total_users: int
    total_teams: int
    total_requests: int
    total_tokens_used: int
    total_credits_spent: Decimal
    active_users_7d: int
    pending_approvals: int


class UserUsageStats(BaseModel):
    """Granular user efficiency profile."""

    user_id: str
    name: str
    email: str
    personal_quota: Decimal
    used_tokens: Decimal
    available_quota: Decimal
    usage_percent: Decimal
    total_requests: int
    is_admin: bool
    status: str


class TeamPoolStats(BaseModel):
    """Shared liquidity performance tracking."""

    team_id: str
    name: str
    common_pool: Decimal
    used_pool: Decimal
    available_pool: Decimal
    usage_percent: Decimal
    member_count: int


class CostTrendPoint(BaseModel):
    """Temporal data point for charting cost velocity."""

    date: str
    cost: Decimal
    requests: int
    tokens: int


class ModelUsageStats(BaseModel):
    """Vendor distribution analysis (e.g. GPT-4 vs Claude)."""

    model: str
    requests: int
    tokens: int
    cost: Decimal
    percentage: Decimal


class DashboardLeaderboardEntry(BaseModel):
    """Gamified efficiency ranking metadata."""

    rank: int
    user_id: str
    name: str
    efficiency_score: Decimal
    total_requests: int
    total_tokens: int


class ApprovalStats(BaseModel):
    """Workflow efficiency metrics."""

    total_pending: int
    total_approved_7d: int
    total_rejected_7d: int
    avg_approval_time_hours: Optional[Decimal]
    top_requesters: List[dict]


class TransferAuditItem(BaseModel):
    """Individual transfer record for audit."""

    id: str
    amount: Decimal
    timestamp: str
    sender: str
    recipient: str
    message: Optional[str]


class TransferStats(BaseModel):
    """Aggregated transfer metrics and audit log."""

    total_transfers: int
    total_amount: Decimal
    recent_transfers: List[TransferAuditItem]
