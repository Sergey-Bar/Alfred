# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Add TestDataSet model for versioned/anonymized test data management.
# Why: Roadmap item 36 requires robust schema for test data versioning and anonymization.
# Root Cause: No persistent schema for test data sets.
# Context: Used by test_data_management router for CRUD and compliance. Future: add indexes, masking, and audit fields.

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    pass


class TestDataSet(BaseModel):
    __tablename__ = "test_data_sets"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Add persistent AnalyticsEventDB model for analytics event storage.
# Why: Roadmap bug: analytics API uses in-memory store; needs persistent storage (PostgreSQL, data warehouse).
# Root Cause: In-memory store is not production-ready.
# Context: Used by analytics router for event ingestion/query/aggregation. Future: add indexes, partitioning, and warehouse sync.
class AnalyticsEventDB(BaseModel):
    __tablename__ = "analytics_events"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(index=True)
    event_type: str = Field(index=True, max_length=100)
    user: Optional[str] = Field(default=None, index=True, max_length=100)
    dataset: Optional[str] = Field(default=None, index=True, max_length=100)
    value: Optional[float] = Field(default=None)
    event_metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )


"""
Alfred - Enterprise AI Credit Governance Platform
Database Models & Schema Definitions

[ARCHITECTURAL ROLE]
This module defines the Data Layer of the application using SQLModel (SQLAlchemy + Pydantic).
It bridges the gap between Python objects and relational database rows, handling:
1. Schema Generation: Automatically creates tables for SQLite/PostgreSQL.
2. ORM Mapping: Typed access to relationships (Users, Teams, Logs).
3. Serialization: Built-in Pydantic integration for API request/response validation.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This module defines all DB models, enums, and API schemas using SQLModel and Pydantic. It covers users, teams, logs, approvals, and governance settings.
# Why: Centralizing models ensures type safety, maintainability, and API contract enforcement.
# Root Cause: Scattered models lead to schema drift and API inconsistencies.
# Context: All DB and API schemas should be defined here. Future: consider modularizing for large-scale growth.
# Model Suitability: For SQLModel/Pydantic patterns, GPT-4.1 is sufficient; for advanced data modeling, a more advanced model may be preferred.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

# --- Enumerations for Strong Typing ---


class UserStatus(str, Enum):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Enum for user account states (active, vacation, suspended).
    # Why: Enforces strong typing and prevents invalid states.
    # Root Cause: String-based states are error-prone.
    # Context: Used by User model and governance logic.
    """
    State of a user account.
    ACTIVE: Standard operating mode.
    ON_VACATION: Signals that personal quota should be available to the team.
    SUSPENDED: Administrative block, prevents all API access.
    """
    ACTIVE = "active"
    ON_VACATION = "on_vacation"
    SUSPENDED = "suspended"


class ProjectPriority(str, Enum):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Enum for request priority tiers (low, normal, high, critical).
    # Why: Enables governance logic to branch on priority.
    # Root Cause: Priority as free text is error-prone.
    # Context: Used by User, RequestLog, and ApprovalRequest.
    """
    Inference Priority Tiers.
    Determines the governance logic applied to a request (e.g., whether to dip into team pools).
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# --- Association / Junction Tables ---


class TeamMemberLink(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Junction table for many-to-many user/team relationships, tracks admin rights and join time.
    # Why: Enables flexible team membership and delegated admin.
    # Root Cause: Many-to-many relationships require explicit linking.
    # Context: Used by Team and User models.
    """
    Many-to-Many Link for Users and Teams.
    Tracks membership and handles delegated administrative rights within a team.
    """
    __tablename__ = "team_member_links"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team_id: Optional[uuid.UUID] = Field(default=None, foreign_key="teams.id", primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id", primary_key=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_admin: bool = Field(default=False, description="Allows managing other members in this team")


# --- Core Domain Models ---


class Team(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Represents a team entity with shared liquidity, governance, and member relationships.
    # Why: Enables quota sharing and team-based governance.
    # Root Cause: Teams are the primary unit of shared quota.
    # Context: Used by User, ApprovalRequest, and analytics.
    """
    Team Entity.
    The primary unit of 'Shared Liquidity'. Teams provide a safety net for users
    who have exhausted their personal quotas but are working on high-priority tasks.
    """
    __tablename__ = "teams"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Financial Ledger
    common_pool: Decimal = Field(
        default=Decimal("10000.00"),
        max_digits=12,
        decimal_places=2,
        description="Total allocated team budget",
    )
    used_pool: Decimal = Field(
        default=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
        description="Cumulative spend across the team pool",
    )

    # Governance Constraints
    vacation_share_percentage: Decimal = Field(
        default=Decimal("10.00"),
        max_digits=5,
        decimal_places=2,
        description="Cap on how much of the pool is accessible via the 'Vacation Sharing' mechanism",
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ORM Navigation
    members: List["User"] = Relationship(back_populates="teams", link_model=TeamMemberLink)

    @property
    def available_pool(self) -> Decimal:
        """Real-time calculation of remaining team liquidity."""
        return self.common_pool - self.used_pool

    @property
    def vacation_share_limit(self) -> Decimal:
        """Constraint calculation for automated vacation sharing."""
        logging.debug(
            f"Calculating vacation_share_limit: available_pool={self.available_pool}, vacation_share_percentage={self.vacation_share_percentage}"
        )
        return (self.available_pool * self.vacation_share_percentage) / Decimal("100.00")

    @vacation_share_limit.setter
    def vacation_share_limit(self, value: Decimal):
        """Allow updates to the vacation share limit."""
        self.vacation_share_percentage = (value / self.available_pool) * Decimal("100.00")


class User(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Represents a user with personal quota, API key, admin rights, and team memberships.
    # Why: Central actor for all governance and quota logic.
    # Root Cause: Users are the primary identity and quota holders.
    # Context: Used by all business logic and API endpoints.
    """
    User Entity.
    The central actor of the system. Holds personal 'Org-Credits' and authentication hashes.
    """
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    api_key_hash: str = Field(max_length=255, description="Argon2 or PBKDF2 hash of the API secret")

    # Access Control
    is_admin: bool = Field(
        default=False, description="Grants access to organization-wide administrative APIs"
    )

    # Quota Management
    personal_quota: Decimal = Field(
        default=Decimal("1000.00"),
        max_digits=12,
        decimal_places=2,
        description="Monthly credit allowance",
    )
    used_tokens: Decimal = Field(
        default=Decimal("0.00"), max_digits=12, decimal_places=2, description="Burned credits"
    )

    status: UserStatus = Field(default=UserStatus.ACTIVE)
    default_priority: ProjectPriority = Field(default=ProjectPriority.NORMAL)

    # Privacy Features
    strict_privacy_default: bool = Field(
        default=False, description="Automatically redacts request content from logs for this user"
    )

    # Flexible Metadata
    preferences_json: Optional[str] = Field(
        default=None, description="Schema-less storage for UI settings/themes"
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_request_at: Optional[datetime] = Field(
        default=None, description="High-water mark for user activity"
    )

    # ORM Navigation
    teams: List[Team] = Relationship(back_populates="members", link_model=TeamMemberLink)
    requests: List["RequestLog"] = Relationship(back_populates="user")
    leaderboard_entries: List["LeaderboardEntry"] = Relationship(back_populates="user")

    @property
    def available_quota(self) -> Decimal:
        """Real-time remaining personal budget."""
        return self.personal_quota - self.used_tokens

    @property
    def is_on_vacation(self) -> bool:
        """Helper for triggering the 'Vacation Sharing' liquidity logic."""
        return self.status == UserStatus.ON_VACATION


class RequestLog(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Stores every AI request for audit, analytics, and quota tracking.
    # Why: Enables detailed usage analytics and compliance.
    # Root Cause: Request logs are required for billing and forensics.
    # Context: Used by analytics, dashboard, and quota logic.
    """
    Request Execution Audit Trail.
    Stores the technical details of every AI interaction. Performance optimized for indexing.
    """
    __tablename__ = "request_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Inference Metadata
    model: str = Field(
        max_length=100, description="Logical identifier of the LLM (e.g., gpt-4-turbo)"
    )
    provider: str = Field(max_length=50, description="Backend platform (openai, anthropic, etc.)")

    # Token Intelligence (Granular usage tracking)
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)

    # Credits Calculation (The 'Invoice' for the request)
    cost_credits: Decimal = Field(max_digits=10, decimal_places=6)

    quota_source: str = Field(
        max_length=50,
        description="Audit string identifying the budget used (e.g., 'personal', 'team_pool')",
    )

    priority: ProjectPriority = Field(default=ProjectPriority.NORMAL)
    strict_privacy: bool = Field(
        default=False, description="If true, request content was purged before storage"
    )

    # Content Storage (Conditional)
    messages_json: Optional[str] = Field(
        default=None, description="Full request payload (Purged if strict_privacy=True)"
    )
    response_content: Optional[str] = Field(
        default=None, description="Full response payload (Purged if strict_privacy=True)"
    )

    # Efficiency Analytics
    efficiency_score: Optional[Decimal] = Field(
        default=None,
        max_digits=6,
        decimal_places=4,
        description="The 'Intelligence Density'—ratio of output comprehension to input verbosity",
    )

    # Timing Data
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    latency_ms: Optional[int] = Field(
        default=None, description="Provider round-trip time in milliseconds"
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="requests")


class LeaderboardEntry(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Aggregates user performance for gamification and dashboard leaderboards.
    # Why: Enables competitive analytics and engagement.
    # Root Cause: Gamification requires periodic aggregation.
    # Context: Used by dashboard and analytics endpoints.
    """
    Aggregated Performance Metrics.
    Optimized for the Gamification dashboard. Updated asynchronously via background workers.
    """
    __tablename__ = "leaderboard"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Temporal Bucketing
    period_start: datetime = Field(index=True)
    period_end: datetime = Field(index=True)
    period_type: str = Field(max_length=20, description="Type of aggregate: daily, weekly, monthly")

    # Aggregated Stats
    total_requests: int = Field(default=0, ge=0)
    total_prompt_tokens: int = Field(default=0, ge=0)
    total_completion_tokens: int = Field(default=0, ge=0)
    total_cost_credits: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)

    avg_efficiency_score: Decimal = Field(
        default=0, description="Average efficiency score for the period"
    )

    rank: Optional[int] = Field(
        default=None, ge=1, description="Calculated ordinal position in the org"
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="leaderboard_entries")


class ApprovalRequest(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Represents a manual quota override workflow for users/teams.
    # Why: Enables exception handling for business-critical requests.
    # Root Cause: Not all quota needs can be automated.
    # Context: Used by governance and admin endpoints.
    """
    Quota Exception Workflow.
    Used when a user needs a manual budget override for an approved business case.
    """
    __tablename__ = "approval_requests"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    team_id: Optional[uuid.UUID] = Field(foreign_key="teams.id", index=True)

    # The 'Ask'
    requested_credits: Decimal = Field(max_digits=12, decimal_places=2)
    reason: str = Field(max_length=1000, description="Justification for the budget override")
    priority: ProjectPriority = Field(default=ProjectPriority.HIGH)

    # The 'State'
    status: str = Field(default="pending", max_length=20)  # pending, approved, rejected

    # Audit Trail
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    approved_by: Optional[uuid.UUID] = Field(default=None, description="User ID of the reviewer")
    approved_credits: Optional[Decimal] = Field(
        default=None, max_digits=12, decimal_places=2, description="Final amount allocated"
    )
    rejection_reason: Optional[str] = Field(default=None, max_length=500)
    resolved_at: Optional[datetime] = Field(default=None)


class AuditLog(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Stores all privileged/admin actions for compliance and forensics.
    # Why: Required for SOC2/ISO27001 and incident response.
    # Root Cause: Admin actions must be permanently recorded.
    # Context: Used by audit logging and compliance modules.
    """
    Administrative Ledger.
    Records every high-privileged action for compliance (SOC2/ISO27001 readiness).
    """
    __tablename__ = "audit_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    actor_user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id", index=True)
    action: str = Field(
        max_length=200, description="Canonical action name (e.g. 'user.rotate_key')"
    )
    target_type: Optional[str] = Field(default=None, max_length=100)
    target_id: Optional[str] = Field(default=None, max_length=100)

    details_json: Optional[str] = Field(
        default=None, description="Opaque data representing the delta change"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class TokenTransfer(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Tracks intra-org credit transfers between users.
    # Why: Enables peer-to-peer quota sharing and analytics.
    # Root Cause: Quota sharing is a core governance feature.
    # Context: Used by governance and analytics modules.
    """
    Intra-Org Credit Reallocation.
    Tracks users sharing their own quotas with colleagues.
    """
    __tablename__ = "token_transfers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    sender_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    recipient_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    amount: Decimal = Field(max_digits=12, decimal_places=2, description="Credits reallocated")
    message: Optional[str] = Field(default=None, max_length=500)

    status: str = Field(default="completed", max_length=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class OrgSettings(SQLModel, table=True):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Stores org-wide governance and compliance settings, including rates and privacy.
    # Why: Enables dynamic policy changes without code deploys.
    # Root Cause: Hard-coded policy is inflexible and risky.
    # Context: Used at startup and by governance logic.
    """
    Global Governance Configuration.
    Database-backed overrides for system settings. Allows dynamic org-wide policy changes.
    """
    __tablename__ = "org_settings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Conversion Ledger (The relative 'Weight' of a token)
    openai_gpt4_rate: Decimal = Field(default=Decimal("0.03"), max_digits=10, decimal_places=6)
    openai_gpt35_rate: Decimal = Field(default=Decimal("0.002"), max_digits=10, decimal_places=6)
    anthropic_claude_rate: Decimal = Field(
        default=Decimal("0.025"), max_digits=10, decimal_places=6
    )
    gemini_rate: Decimal = Field(default=Decimal("0.001"), max_digits=10, decimal_places=6)
    default_rate: Decimal = Field(default=Decimal("0.01"), max_digits=10, decimal_places=6)

    # Global Policy Switches
    allow_vacation_sharing: bool = Field(default=True)
    allow_priority_bypass: bool = Field(default=True)
    max_vacation_share_percent: Decimal = Field(
        default=Decimal("10.00"), max_digits=5, decimal_places=2
    )

    # Regulatory Compliance
    force_strict_privacy: bool = Field(default=False)
    log_retention_days: int = Field(default=90)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- API Contract Models (Pydantic context) ---

# --- RBAC Models: Roles & Permissions ---
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Adds flexible RBAC models for roles, permissions, and assignments. Enables fine-grained access control and future policy enforcement.
# Why: Required for enterprise-grade governance, least-privilege, and compliance.
# Root Cause: Prior model only supported admin/non-admin; lacked extensibility for custom roles and permissions.
# Context: Used by new RBAC routers and permission checks. Future: can be extended for org/team scoping, hierarchical roles, and policy engines.
# Model Suitability: GPT-4.1 is suitable for SQLModel/Pydantic RBAC patterns; for advanced policy engines, consider Claude 3 or Gemini 1.5.


class Role(BaseModel):
    """
    RBAC Role definition (e.g., admin, manager, auditor, user).
    """

    __tablename__ = "roles"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=64)
    description: Optional[str] = Field(default=None, max_length=255)
    # Future: org_id/team_id for scoping


class Permission(BaseModel):
    """
    RBAC Permission definition (e.g., user:create, team:delete, audit:view).
    """

    __tablename__ = "permissions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=64)
    description: Optional[str] = Field(default=None, max_length=255)


class UserRole(BaseModel):
    """
    Assignment of a Role to a User (many-to-many).
    """

    __tablename__ = "user_roles"
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="roles.id", primary_key=True)
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RolePermission(BaseModel):
    """
    Assignment of a Permission to a Role (many-to-many).
    """

    __tablename__ = "role_permissions"
    role_id: uuid.UUID = Field(foreign_key="roles.id", primary_key=True)
    permission_id: uuid.UUID = Field(foreign_key="permissions.id", primary_key=True)
    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessage(SQLModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: OpenAI-compatible message schema for chat API requests.
    # Why: Ensures API compatibility and type safety.
    # Root Cause: Schema drift breaks API contract.
    # Context: Used by ChatCompletionRequest and ChatChoice.
    """OpenAI-compatible message schema for the API layer."""
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Unified request schema for chat completions, with Alfred-specific governance fields.
    # Why: Enables governance logic to enforce policy on every request.
    # Root Cause: API requests must be validated and enriched.
    # Context: Used by proxy and governance routers.
    """
    The unified request format for Alfred's governance proxy.
    Wraps standard OpenAI parameters with Alfred-specific governance headers.
    """
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)

    # Internal Alfred Logic
    project_priority: Optional[ProjectPriority] = Field(default=None)


class UsageInfo(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Token usage reporting schema for API responses.
    # Why: Enables quota tracking and analytics.
    # Root Cause: Usage info is required for billing and dashboards.
    # Context: Used by ChatCompletionResponse and analytics.
    """Token reporting following provider standards."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatChoice(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Represents a single completion option in chat API responses.
    # Why: Enables multi-choice completions and API compatibility.
    # Root Cause: OpenAI API supports multiple choices per request.
    # Context: Used by ChatCompletionResponse.
    """Indicates one of the generated completion options."""
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Unified response schema for chat completions, with governance extensions.
    # Why: Ensures all responses include quota/cost info for compliance.
    # Root Cause: API responses must be enriched for governance.
    # Context: Used by proxy and dashboard endpoints.
    """
    The unified response from the Alfred Gateway.
    Injects quota and cost information into the standard LLM response payload.
    """
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: UsageInfo

    # Governance Extensions (Added by Alfred)
    cost_credits: Optional[Decimal] = None
    quota_source: Optional[str] = None
    remaining_quota: Optional[Decimal] = None


class QuotaErrorResponse(BaseModel):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Standardized error schema for quota-exceeded responses.
    # Why: Ensures clients can handle quota errors programmatically.
    # Root Cause: Inconsistent error schemas break client logic.
    # Context: Used by governance and proxy routers.
    """Transparent messaging when a user's request is blocked by governance rules."""
    error: str
    code: str = "quota_exceeded"
    quota_remaining: float
    message: str
    approval_process: Dict[str, Any]


# Added fields for enhanced governance workflows
class QuotaInjectionRequest(BaseModel):
    __tablename__ = "quota_injection_requests"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    team_id: Optional[uuid.UUID] = Field(default=None, index=True)
    requested_quota: Decimal = Field()
    status: str = Field(default="PENDING", max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Optional[datetime] = Field(default=None)
    approved_by: Optional[uuid.UUID] = Field(default=None)
    approval_notes: Optional[str] = Field(default=None, max_length=500)


# [AI GENERATED]
# Model: GitHub Copilot (Claude Opus 4.5)
# Logic: Safety incident tracking for audit trail and compliance reporting.
# Why: Enterprise compliance requires immutable log of all safety violations.
# Root Cause: GDPR, HIPAA, SOC2 require audit trails for data protection incidents.
# Context: Used by safety pipeline for incident logging and dashboard analytics.
# Model Suitability: Claude Opus 4.5 used for critical compliance infrastructure.
class SafetyIncident(BaseModel):
    """
    Safety Incident Log.

    Immutable audit trail for all safety violations detected by the pipeline.
    Used for compliance reporting, analytics, and security monitoring.
    """

    __tablename__ = "safety_incidents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    # Context
    user_id: Optional[uuid.UUID] = Field(default=None, index=True, foreign_key="users.id")
    org_id: Optional[uuid.UUID] = Field(default=None, index=True)
    request_id: Optional[str] = Field(default=None, index=True, max_length=100)

    # Violation details
    violation_category: str = Field(index=True, max_length=50)  # pii, secret, injection, blocklist
    violation_type: str = Field(
        index=True, max_length=100
    )  # ssn, openai_api_key, ignore_instructions, etc.
    severity: str = Field(index=True, max_length=20)  # low, medium, high, critical
    confidence: float = Field()
    description: str = Field(max_length=500)

    # Action taken
    enforcement_mode: str = Field(index=True, max_length=20)  # block, redact, warn, allow
    request_allowed: bool = Field(index=True)
    was_redacted: bool = Field(default=False)

    # Metadata (do NOT log actual PII/secrets)
    violation_count: int = Field(default=1)
    provider: Optional[str] = Field(default=None, max_length=100)

    # Additional context (JSON)
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))


# [AI GENERATED]
# Model: GitHub Copilot (Claude Opus 4.5)
# Logic: Persistent safety policy configuration per organization.
# Why: Enables per-org customization of safety enforcement modes and thresholds.
# Root Cause: Different organizations have different compliance requirements.
# Context: Used by safety pipeline to load org-specific policies.
# Model Suitability: Claude Opus 4.5 used for critical compliance infrastructure.
class SafetyPolicyDB(BaseModel):
    """
    Safety Policy Configuration.

    Stores organization-specific safety policy settings.
    Loaded by safety pipeline to determine enforcement modes.
    """

    __tablename__ = "safety_policies"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    org_id: uuid.UUID = Field(index=True, unique=True)

    # PII settings
    pii_enabled: bool = Field(default=True)
    pii_enforcement: str = Field(default="block", max_length=20)  # block, redact, warn, allow
    pii_types: Optional[List[str]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    pii_allow_redaction: bool = Field(default=True)

    # Secret settings
    secret_enabled: bool = Field(default=True)
    secret_enforcement: str = Field(default="block", max_length=20)
    secret_types: Optional[List[str]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    secret_check_entropy: bool = Field(default=True)
    secret_entropy_threshold: float = Field(default=4.5)

    # Injection settings
    injection_enabled: bool = Field(default=True)
    injection_enforcement: str = Field(default="block", max_length=20)
    injection_types: Optional[List[str]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    injection_min_severity: str = Field(default="high", max_length=20)
    injection_block_threshold: str = Field(default="high", max_length=20)

    # Custom blocklist
    blocklist_enabled: bool = Field(default=True)
    blocklist_patterns: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    blocklist_enforcement: str = Field(default="warn", max_length=20)

    # Global settings
    log_violations: bool = Field(default=True)
    notify_on_critical: bool = Field(default=True)
    strict_mode: bool = Field(default=False)
    allow_user_override: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
