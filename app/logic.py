"""
TokenPool Core Business Logic
Handles quota management, vacation sharing, priority overrides, and efficiency scoring.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple, List
from datetime import datetime, timedelta
import hashlib
import secrets

from sqlmodel import Session, select
from litellm import completion, completion_cost

from .models import (
    User, Team, TeamMemberLink, RequestLog, LeaderboardEntry, 
    OrgSettings, ApprovalRequest,
    UserStatus, ProjectPriority,
    ChatCompletionRequest, ChatMessage
)


# -------------------------------------------------------------------
# Data Classes for Results
# -------------------------------------------------------------------

@dataclass
class QuotaCheckResult:
    """Result of a quota availability check."""
    allowed: bool
    source: str  # "personal", "team_pool", "vacation_share", "priority_bypass"
    available_credits: Decimal
    message: str
    requires_approval: bool = False
    approval_instructions: Optional[dict] = None


@dataclass
class CostEstimate:
    """Estimated cost for a request."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_credits: Decimal
    provider: str
    model: str


# -------------------------------------------------------------------
# Credit/Cost Calculation
# -------------------------------------------------------------------

class CreditCalculator:
    """Calculate Org-Credits from token usage using LiteLLM cost mapping."""
    
    # Conversion factor: actual cost -> org credits (1 USD = 100 credits by default)
    USD_TO_CREDITS = Decimal("100.00")
    
    # Fallback rates per 1000 tokens when LiteLLM doesn't have pricing
    FALLBACK_RATES = {
        "gpt-4": Decimal("0.03"),
        "gpt-4-turbo": Decimal("0.01"),
        "gpt-4o": Decimal("0.005"),
        "gpt-3.5-turbo": Decimal("0.0015"),
        "claude-3-opus": Decimal("0.015"),
        "claude-3-sonnet": Decimal("0.003"),
        "claude-3-haiku": Decimal("0.00025"),
        "gemini-pro": Decimal("0.0005"),
        "gemini-1.5-pro": Decimal("0.00125"),
        "default": Decimal("0.005"),
    }
    
    @classmethod
    def calculate_cost(
        cls,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        response: Optional[dict] = None
    ) -> Decimal:
        """
        Calculate cost in Org-Credits.
        Uses LiteLLM's cost calculation when available, falls back to internal rates.
        """
        try:
            # Try to use LiteLLM's cost calculation
            if response:
                usd_cost = completion_cost(completion_response=response)
                return Decimal(str(usd_cost)) * cls.USD_TO_CREDITS
        except Exception:
            pass
        
        # Fallback to internal rates
        rate = cls._get_rate_for_model(model)
        total_tokens = prompt_tokens + completion_tokens
        return (Decimal(total_tokens) / Decimal("1000")) * rate * cls.USD_TO_CREDITS
    
    @classmethod
    def _get_rate_for_model(cls, model: str) -> Decimal:
        """Get the per-1000-token rate for a model."""
        model_lower = model.lower()
        
        for key, rate in cls.FALLBACK_RATES.items():
            if key in model_lower:
                return rate
        
        return cls.FALLBACK_RATES["default"]
    
    @classmethod
    def estimate_cost(cls, model: str, estimated_tokens: int) -> Decimal:
        """Estimate cost for pre-flight quota checks."""
        rate = cls._get_rate_for_model(model)
        return (Decimal(estimated_tokens) / Decimal("1000")) * rate * cls.USD_TO_CREDITS


# -------------------------------------------------------------------
# Quota Management
# -------------------------------------------------------------------

class QuotaManager:
    """Manage user quotas with team sharing and priority overrides."""
    
    def __init__(self, session: Session):
        self.session = session
        self._org_settings: Optional[OrgSettings] = None
    
    @property
    def org_settings(self) -> OrgSettings:
        """Get or create organization settings."""
        if self._org_settings is None:
            statement = select(OrgSettings)
            self._org_settings = self.session.exec(statement).first()
            if self._org_settings is None:
                self._org_settings = OrgSettings()
                self.session.add(self._org_settings)
                self.session.commit()
                self.session.refresh(self._org_settings)
        return self._org_settings
    
    def check_quota(
        self,
        user: User,
        estimated_cost: Decimal,
        priority: ProjectPriority = ProjectPriority.NORMAL
    ) -> QuotaCheckResult:
        """
        Check if user has sufficient quota for a request.
        Implements the balancer logic with vacation sharing and priority bypass.
        """
        # Step 1: Check personal quota
        if user.available_quota >= estimated_cost:
            return QuotaCheckResult(
                allowed=True,
                source="personal",
                available_credits=user.available_quota,
                message="Using personal quota"
            )
        
        # Step 2: Check for Critical priority bypass
        if priority == ProjectPriority.CRITICAL and self.org_settings.allow_priority_bypass:
            team_pool = self._get_total_team_pool(user)
            if team_pool >= estimated_cost:
                return QuotaCheckResult(
                    allowed=True,
                    source="priority_bypass",
                    available_credits=team_pool,
                    message="Critical priority: bypassing to team pool"
                )
        
        # Step 3: Check vacation sharing
        if self.org_settings.allow_vacation_sharing:
            vacation_credits = self._get_vacation_share_credits(user)
            if vacation_credits >= estimated_cost:
                return QuotaCheckResult(
                    allowed=True,
                    source="vacation_share",
                    available_credits=vacation_credits,
                    message="Using vacation share from team members"
                )
        
        # Step 4: Quota exceeded - provide approval instructions
        return QuotaCheckResult(
            allowed=False,
            source="none",
            available_credits=user.available_quota,
            message="Quota exceeded. Manager approval required.",
            requires_approval=True,
            approval_instructions={
                "process": "Manager Approval Required",
                "steps": [
                    "1. Submit an approval request via POST /v1/approvals",
                    "2. Include your reason and requested credit amount",
                    "3. A team admin will review and approve/reject",
                    "4. Once approved, credits will be added to your quota"
                ],
                "endpoint": "/v1/approvals",
                "required_fields": ["requested_credits", "reason"],
                "optional_fields": ["priority"],
                "personal_quota_remaining": float(user.available_quota),
                "personal_quota_total": float(user.personal_quota)
            }
        )
    
    def _get_total_team_pool(self, user: User) -> Decimal:
        """Get total available credits from all user's teams."""
        total = Decimal("0.00")
        
        # Query teams the user belongs to
        statement = (
            select(Team)
            .join(TeamMemberLink)
            .where(TeamMemberLink.user_id == user.id)
        )
        teams = self.session.exec(statement).all()
        
        for team in teams:
            total += team.available_pool
        
        return total
    
    def _get_vacation_share_credits(self, user: User) -> Decimal:
        """
        Calculate available credits from team members on vacation.
        Returns up to 10% of the team pool when members are on vacation.
        """
        total_vacation_credits = Decimal("0.00")
        
        # Get user's teams
        statement = (
            select(Team)
            .join(TeamMemberLink)
            .where(TeamMemberLink.user_id == user.id)
        )
        teams = self.session.exec(statement).all()
        
        for team in teams:
            # Check if any team members are on vacation
            vacation_members = self._get_vacation_members(team, exclude_user=user)
            
            if vacation_members:
                # Allow up to vacation_share_percentage of the team pool
                share_limit = team.vacation_share_limit
                total_vacation_credits += share_limit
        
        return total_vacation_credits
    
    def _get_vacation_members(self, team: Team, exclude_user: User) -> List[User]:
        """Get team members who are currently on vacation."""
        statement = (
            select(User)
            .join(TeamMemberLink)
            .where(TeamMemberLink.team_id == team.id)
            .where(User.id != exclude_user.id)
            .where(User.status == UserStatus.ON_VACATION)
        )
        return list(self.session.exec(statement).all())
    
    def deduct_quota(
        self,
        user: User,
        cost: Decimal,
        source: str,
        team: Optional[Team] = None
    ) -> None:
        """Deduct credits from the appropriate quota source."""
        if source == "personal":
            user.used_tokens += cost
            user.last_request_at = datetime.utcnow()
            self.session.add(user)
        
        elif source in ("team_pool", "priority_bypass", "vacation_share"):
            # Deduct from team pool if specified, otherwise from first team
            if team is None:
                statement = (
                    select(Team)
                    .join(TeamMemberLink)
                    .where(TeamMemberLink.user_id == user.id)
                )
                team = self.session.exec(statement).first()
            
            if team:
                team.used_pool += cost
                team.updated_at = datetime.utcnow()
                self.session.add(team)
            
            user.last_request_at = datetime.utcnow()
            self.session.add(user)
        
        self.session.commit()
    
    def add_quota(self, user: User, credits: Decimal) -> None:
        """Add credits to a user's personal quota."""
        user.personal_quota += credits
        user.updated_at = datetime.utcnow()
        self.session.add(user)
        self.session.commit()


# -------------------------------------------------------------------
# Efficiency Scoring
# -------------------------------------------------------------------

class EfficiencyScorer:
    """Calculate and track efficiency scores for users."""
    
    def __init__(self, session: Session):
        self.session = session
    
    @staticmethod
    def calculate_efficiency_score(prompt_tokens: int, completion_tokens: int) -> Decimal:
        """
        Calculate efficiency score as completion_tokens / prompt_tokens.
        Higher scores indicate more output per input (potentially more efficient prompting).
        """
        if prompt_tokens == 0:
            return Decimal("0.00")
        
        score = Decimal(completion_tokens) / Decimal(prompt_tokens)
        return round(score, 4)
    
    def update_leaderboard(
        self,
        user: User,
        request_log: RequestLog,
        period_type: str = "daily"
    ) -> LeaderboardEntry:
        """Update or create leaderboard entry for the user."""
        now = datetime.utcnow()
        
        # Determine period boundaries
        if period_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period_type == "weekly":
            days_since_monday = now.weekday()
            period_start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            period_end = period_start + timedelta(weeks=1)
        else:  # monthly
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = now.replace(year=now.year + 1, month=1, day=1)
            else:
                period_end = now.replace(month=now.month + 1, day=1)
        
        # Find or create entry
        statement = select(LeaderboardEntry).where(
            LeaderboardEntry.user_id == user.id,
            LeaderboardEntry.period_type == period_type,
            LeaderboardEntry.period_start == period_start
        )
        entry = self.session.exec(statement).first()
        
        if entry is None:
            entry = LeaderboardEntry(
                user_id=user.id,
                period_start=period_start,
                period_end=period_end,
                period_type=period_type
            )
        
        # Update aggregated metrics
        entry.total_requests += 1
        entry.total_prompt_tokens += request_log.prompt_tokens
        entry.total_completion_tokens += request_log.completion_tokens
        entry.total_cost_credits += request_log.cost_credits
        
        # Recalculate average efficiency
        if entry.total_prompt_tokens > 0:
            entry.avg_efficiency_score = (
                Decimal(entry.total_completion_tokens) / Decimal(entry.total_prompt_tokens)
            )
        
        entry.updated_at = datetime.utcnow()
        
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        
        return entry
    
    def get_leaderboard(
        self,
        period_type: str = "daily",
        limit: int = 10
    ) -> List[LeaderboardEntry]:
        """Get the top performers by efficiency score."""
        now = datetime.utcnow()
        
        # Current period start
        if period_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "weekly":
            days_since_monday = now.weekday()
            period_start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        statement = (
            select(LeaderboardEntry)
            .where(LeaderboardEntry.period_type == period_type)
            .where(LeaderboardEntry.period_start == period_start)
            .order_by(LeaderboardEntry.avg_efficiency_score.desc())
            .limit(limit)
        )
        
        return list(self.session.exec(statement).all())


# -------------------------------------------------------------------
# Request Logging
# -------------------------------------------------------------------

class RequestLogger:
    """Log requests with privacy mode support."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def log_request(
        self,
        user: User,
        request: ChatCompletionRequest,
        response: dict,
        cost_credits: Decimal,
        quota_source: str,
        strict_privacy: bool,
        latency_ms: int,
        provider: str = "openai"
    ) -> RequestLog:
        """
        Log a completed request.
        If strict_privacy is True, messages and response content are NOT stored.
        """
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        
        # Calculate efficiency score
        efficiency_score = EfficiencyScorer.calculate_efficiency_score(
            prompt_tokens, completion_tokens
        )
        
        # Prepare content (only if not strict privacy)
        messages_json = None
        response_content = None
        
        if not strict_privacy:
            import json
            messages_json = json.dumps([m.model_dump() for m in request.messages])
            choices = response.get("choices", [])
            if choices:
                response_content = choices[0].get("message", {}).get("content", "")
        
        log = RequestLog(
            user_id=user.id,
            model=request.model,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_credits=cost_credits,
            quota_source=quota_source,
            priority=request.project_priority or user.default_priority,
            strict_privacy=strict_privacy,
            messages_json=messages_json,
            response_content=response_content,
            efficiency_score=efficiency_score,
            latency_ms=latency_ms
        )
        
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        
        return log


# -------------------------------------------------------------------
# Authentication
# -------------------------------------------------------------------

class AuthManager:
    """Handle API key authentication."""
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def generate_api_key() -> Tuple[str, str]:
        """Generate a new API key and return (plaintext, hash)."""
        plaintext = f"ab-{secrets.token_urlsafe(32)}"
        hashed = AuthManager.hash_api_key(plaintext)
        return plaintext, hashed
    
    @classmethod
    def authenticate(cls, session: Session, api_key: str) -> Optional[User]:
        """Authenticate a user by API key."""
        key_hash = cls.hash_api_key(api_key)
        statement = select(User).where(User.api_key_hash == key_hash)
        return session.exec(statement).first()


# -------------------------------------------------------------------
# LLM Proxy
# -------------------------------------------------------------------

class LLMProxy:
    """Proxy requests to LLM providers via LiteLLM."""
    
    @staticmethod
    async def forward_request(
        request: ChatCompletionRequest,
        api_keys: Optional[dict] = None
    ) -> dict:
        """
        Forward a chat completion request to the appropriate provider via LiteLLM.
        
        Args:
            request: The chat completion request
            api_keys: Optional dict of provider API keys
        
        Returns:
            The response from the LLM provider
        """
        # Convert messages to dict format
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Build kwargs for litellm
        kwargs = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
        }
        
        if request.max_tokens:
            kwargs["max_tokens"] = request.max_tokens
        
        if request.stop:
            kwargs["stop"] = request.stop
        
        # Add API keys if provided
        if api_keys:
            kwargs.update(api_keys)
        
        # Make the request via litellm
        response = await completion(**kwargs, acompletion=True)
        
        # Convert to dict
        return response.model_dump() if hasattr(response, 'model_dump') else dict(response)


# -------------------------------------------------------------------
# Approval Management
# -------------------------------------------------------------------

class ApprovalManager:
    """Manage quota approval requests."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_request(
        self,
        user: User,
        requested_credits: Decimal,
        reason: str,
        priority: ProjectPriority = ProjectPriority.HIGH,
        team_id: Optional[str] = None
    ) -> ApprovalRequest:
        """Create a new approval request."""
        import uuid as uuid_module
        
        approval = ApprovalRequest(
            user_id=user.id,
            team_id=uuid_module.UUID(team_id) if team_id else None,
            requested_credits=requested_credits,
            reason=reason,
            priority=priority,
            status="pending"
        )
        
        self.session.add(approval)
        self.session.commit()
        self.session.refresh(approval)
        
        return approval
    
    def approve(
        self,
        approval_id: str,
        approver_id: str,
        approved_credits: Optional[Decimal] = None
    ) -> ApprovalRequest:
        """Approve a quota request."""
        import uuid as uuid_module
        
        statement = select(ApprovalRequest).where(
            ApprovalRequest.id == uuid_module.UUID(approval_id)
        )
        approval = self.session.exec(statement).first()
        
        if not approval:
            raise ValueError("Approval request not found")
        
        approval.status = "approved"
        approval.approved_by = uuid_module.UUID(approver_id)
        approval.approved_credits = approved_credits or approval.requested_credits
        approval.resolved_at = datetime.utcnow()
        
        # Add credits to user
        user_statement = select(User).where(User.id == approval.user_id)
        user = self.session.exec(user_statement).first()
        
        if user:
            user.personal_quota += approval.approved_credits
            user.updated_at = datetime.utcnow()
            self.session.add(user)
        
        self.session.add(approval)
        self.session.commit()
        self.session.refresh(approval)
        
        return approval
    
    def reject(
        self,
        approval_id: str,
        rejector_id: str,
        reason: str
    ) -> ApprovalRequest:
        """Reject a quota request."""
        import uuid as uuid_module
        
        statement = select(ApprovalRequest).where(
            ApprovalRequest.id == uuid_module.UUID(approval_id)
        )
        approval = self.session.exec(statement).first()
        
        if not approval:
            raise ValueError("Approval request not found")
        
        approval.status = "rejected"
        approval.approved_by = uuid_module.UUID(rejector_id)
        approval.rejection_reason = reason
        approval.resolved_at = datetime.utcnow()
        
        self.session.add(approval)
        self.session.commit()
        self.session.refresh(approval)
        
        return approval
    
    def get_pending(self, team_id: Optional[str] = None) -> List[ApprovalRequest]:
        """Get pending approval requests."""
        import uuid as uuid_module
        
        statement = select(ApprovalRequest).where(ApprovalRequest.status == "pending")
        
        if team_id:
            statement = statement.where(ApprovalRequest.team_id == uuid_module.UUID(team_id))
        
        return list(self.session.exec(statement).all())
