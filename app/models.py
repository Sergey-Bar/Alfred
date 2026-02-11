"""
TokenPool Database Models
SQLModel-based models for user management, team quotas, and request tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from decimal import Decimal
import uuid

from sqlmodel import SQLModel, Field, Relationship


class UserStatus(str, Enum):
    """User activity status for quota sharing."""
    ACTIVE = "active"
    ON_VACATION = "on_vacation"
    SUSPENDED = "suspended"


class ProjectPriority(str, Enum):
    """Project priority levels for quota bypass rules."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# -------------------------------------------------------------------
# Association Tables
# -------------------------------------------------------------------

class TeamMemberLink(SQLModel, table=True):
    """Many-to-many relationship between teams and users."""
    __tablename__ = "team_member_links"
    
    team_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="teams.id", primary_key=True
    )
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    is_admin: bool = Field(default=False)


# -------------------------------------------------------------------
# Core Models
# -------------------------------------------------------------------

class Team(SQLModel, table=True):
    """Team model with shared quota pool."""
    __tablename__ = "teams"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Shared quota pool in "Org-Credits"
    common_pool: Decimal = Field(default=Decimal("10000.00"), max_digits=12, decimal_places=2)
    used_pool: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    
    # Vacation sharing settings
    vacation_share_percentage: Decimal = Field(
        default=Decimal("10.00"), 
        max_digits=5, 
        decimal_places=2,
        description="Max percentage of pool available for vacation sharing"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    members: List["User"] = Relationship(back_populates="teams", link_model=TeamMemberLink)
    
    @property
    def available_pool(self) -> Decimal:
        """Calculate remaining available pool credits."""
        return self.common_pool - self.used_pool
    
    @property
    def vacation_share_limit(self) -> Decimal:
        """Calculate max credits available for vacation sharing."""
        return (self.available_pool * self.vacation_share_percentage) / Decimal("100.00")


class User(SQLModel, table=True):
    """User model with personal quota and status tracking."""
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    api_key_hash: str = Field(max_length=255, description="Hashed API key for authentication")
    
    # Personal quota in "Org-Credits"  
    personal_quota: Decimal = Field(default=Decimal("1000.00"), max_digits=12, decimal_places=2)
    used_tokens: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    
    # User status
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    
    # Default project priority for the user
    default_priority: ProjectPriority = Field(default=ProjectPriority.NORMAL)
    
    # Privacy preferences
    strict_privacy_default: bool = Field(default=False, description="Default privacy mode for requests")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_request_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    teams: List[Team] = Relationship(back_populates="members", link_model=TeamMemberLink)
    requests: List["RequestLog"] = Relationship(back_populates="user")
    leaderboard_entries: List["LeaderboardEntry"] = Relationship(back_populates="user")
    
    @property
    def available_quota(self) -> Decimal:
        """Calculate remaining personal quota."""
        return self.personal_quota - self.used_tokens
    
    @property
    def is_on_vacation(self) -> bool:
        """Check if user is currently on vacation."""
        return self.status == UserStatus.ON_VACATION


class RequestLog(SQLModel, table=True):
    """Log of API requests with optional message storage based on privacy mode."""
    __tablename__ = "request_logs"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    
    # Request metadata
    model: str = Field(max_length=100, description="AI model used")
    provider: str = Field(max_length=50, description="LLM provider (openai, anthropic, etc)")
    
    # Token usage (always stored)
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    
    # Cost in Org-Credits
    cost_credits: Decimal = Field(max_digits=10, decimal_places=6)
    
    # Quota source tracking
    quota_source: str = Field(
        max_length=50, 
        description="Source of quota: personal, team_pool, vacation_share, priority_bypass"
    )
    
    # Priority that was used
    priority: ProjectPriority = Field(default=ProjectPriority.NORMAL)
    
    # Privacy flag - if True, messages were not logged
    strict_privacy: bool = Field(default=False)
    
    # Request/Response content (only stored if strict_privacy=False)
    messages_json: Optional[str] = Field(
        default=None, 
        description="JSON-encoded request messages (null if privacy mode)"
    )
    response_content: Optional[str] = Field(
        default=None,
        description="Response content (null if privacy mode)"
    )
    
    # Efficiency metrics
    efficiency_score: Optional[Decimal] = Field(
        default=None, 
        max_digits=6, 
        decimal_places=4,
        description="completion_tokens / prompt_tokens ratio"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: Optional[int] = Field(default=None, description="Request latency in milliseconds")
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="requests")


class LeaderboardEntry(SQLModel, table=True):
    """Efficiency leaderboard for tracking user performance."""
    __tablename__ = "leaderboard"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    
    # Time period for the entry
    period_start: datetime = Field(index=True)
    period_end: datetime = Field(index=True)
    period_type: str = Field(max_length=20, description="daily, weekly, monthly")
    
    # Aggregated metrics
    total_requests: int = Field(default=0, ge=0)
    total_prompt_tokens: int = Field(default=0, ge=0)
    total_completion_tokens: int = Field(default=0, ge=0)
    total_cost_credits: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    
    # Efficiency score (average completion/prompt ratio)
    avg_efficiency_score: Decimal = Field(
        default=Decimal("0.00"), 
        max_digits=6, 
        decimal_places=4
    )
    
    # Ranking
    rank: Optional[int] = Field(default=None, ge=1)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="leaderboard_entries")


class ApprovalRequest(SQLModel, table=True):
    """Track manager approval requests for quota overrides."""
    __tablename__ = "approval_requests"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    team_id: Optional[uuid.UUID] = Field(foreign_key="teams.id", index=True)
    
    # Request details
    requested_credits: Decimal = Field(max_digits=12, decimal_places=2)
    reason: str = Field(max_length=1000)
    priority: ProjectPriority = Field(default=ProjectPriority.HIGH)
    
    # Approval status
    status: str = Field(default="pending", max_length=20)  # pending, approved, rejected
    approved_by: Optional[uuid.UUID] = Field(default=None)
    approved_credits: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    rejection_reason: Optional[str] = Field(default=None, max_length=500)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(default=None)


class OrgSettings(SQLModel, table=True):
    """Organization-wide settings for TokenPool."""
    __tablename__ = "org_settings"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Credit conversion rates (per 1000 tokens)
    openai_gpt4_rate: Decimal = Field(default=Decimal("0.03"), max_digits=10, decimal_places=6)
    openai_gpt35_rate: Decimal = Field(default=Decimal("0.002"), max_digits=10, decimal_places=6)
    anthropic_claude_rate: Decimal = Field(default=Decimal("0.025"), max_digits=10, decimal_places=6)
    gemini_rate: Decimal = Field(default=Decimal("0.001"), max_digits=10, decimal_places=6)
    default_rate: Decimal = Field(default=Decimal("0.01"), max_digits=10, decimal_places=6)
    
    # Global quota settings
    allow_vacation_sharing: bool = Field(default=True)
    allow_priority_bypass: bool = Field(default=True)
    max_vacation_share_percent: Decimal = Field(default=Decimal("10.00"), max_digits=5, decimal_places=2)
    
    # Privacy settings
    force_strict_privacy: bool = Field(default=False, description="Force privacy mode for all requests")
    log_retention_days: int = Field(default=90, description="Days to retain request logs")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# -------------------------------------------------------------------
# Pydantic Models for API Request/Response
# -------------------------------------------------------------------

class ChatMessage(SQLModel):
    """OpenAI-compatible chat message."""
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(SQLModel):
    """OpenAI-compatible chat completion request."""
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    stop: Optional[List[str]] = None
    stream: Optional[bool] = Field(default=False)
    user: Optional[str] = None
    
    # TokenPool specific
    project_priority: Optional[ProjectPriority] = Field(default=None)


class UsageInfo(SQLModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatChoice(SQLModel):
    """Chat completion choice."""
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionResponse(SQLModel):
    """OpenAI-compatible chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: UsageInfo
    
    # TokenPool extensions
    cost_credits: Optional[Decimal] = None
    quota_source: Optional[str] = None
    remaining_quota: Optional[Decimal] = None


class QuotaErrorResponse(SQLModel):
    """Error response for quota exceeded scenarios."""
    error: str
    code: str = "quota_exceeded"
    quota_remaining: Decimal
    message: str
    approval_process: dict
