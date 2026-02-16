"""
Alfred - Enterprise AI Credit Governance Platform
Core Domain Logic & Governance Engine

[ARCHITECTURAL ROLE]
This module is the "Heart" of the Alfred platform. It implements the complex
governance logic that differentiates Alfred from a simple LLM proxy:
1. Credit Calculation: Normalized billing across disparate model providers.
2. Quota Management: Multi-tier allocation (Personal -> Team -> Vacation Share).
3. Efficiency Scoring: Gamified performance metrics to encourage concise prompting.
4. Resilience: Robust retry and fallback mechanisms for high-availability.

[GOVERNANCE PHILOSOPHY]
The balancer logic implements 'Elastic Quotas'. While individuals have hard limits,
the system allows for 'Priority Borrowing' from team pools and 'Vacation Reallocation'
to ensure mission-critical work is never blocked by rigid administrative silos.
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from litellm import completion, completion_cost
from sqlmodel import Session, select

from .constants import CreditConversion

# --- Resiliency Configuration (Tenacity) ---
# We use Tenacity for robust, exponential-backoff retries.
# This is critical for Enterprise durability where LLM endpoints frequently timeout.
try:
    import logging

    from tenacity import (
        before_sleep_log,
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )

    retry_logger = logging.getLogger(__name__)
    TENACITY_AVAILABLE = True
except ImportError:
    # Fail gracefully if tenacity is missing, allowing the app to run in degraded mode.
    TENACITY_AVAILABLE = False
    retry_logger = None

from .config import settings
from .models import (
    ApprovalRequest,
    ChatCompletionRequest,
    LeaderboardEntry,
    OrgSettings,
    ProjectPriority,
    RequestLog,
    Team,
    TeamMemberLink,
    User,
    UserStatus,
)


@dataclass
class QuotaCheckResult:
    """
    Governance Decision Object.
    Encapsulates the result of the multi-tier quota evaluation.
    """

    allowed: bool
    source: str  # "personal", "team_pool", "vacation_share", "priority_bypass"
    available_credits: Decimal
    message: str
    requires_approval: bool = False
    approval_instructions: Optional[dict] = None


@dataclass
class CostEstimate:
    """Logical prediction for pre-flight billing checks."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_credits: Decimal
    provider: str
    model: str


# --- 1. The Credit Ledger: Mapping Raw Tokens to Org-Value ---


class CreditCalculator:
    """
    Financial Quantizer.
    Normalizes token usage from 50+ providers into a single internal currency: 'Org-Credits'.
    """

    # Global conversion factor defined by the Org (e.g. 1 USD = 1000 Credits)
    USD_TO_CREDITS = CreditConversion.USD_TO_CREDITS

    # Standard Capability-Tier Pricing (Per 1000 Tokens)
    # These rates ensure pricing stability even when providers change their raw underlying costs.
    FALLBACK_RATES = {
        "gpt-4": Decimal("0.03"),
        "gpt-4-turbo": Decimal("0.01"),
        "gpt-4o": Decimal("0.005"),
        "gpt-4o-mini": Decimal("0.00015"),
        "gpt-3.5-turbo": Decimal("0.0015"),
        "o1": Decimal("0.015"),
        "o1-mini": Decimal("0.003"),
        "claude-3-opus": Decimal("0.015"),
        "claude-3-sonnet": Decimal("0.003"),
        "claude-3.5-sonnet": Decimal("0.003"),
        "claude-3-haiku": Decimal("0.00025"),
        "gemini-pro": Decimal("0.0005"),
        "gemini-1.5-pro": Decimal("0.00125"),
        "gemini-1.5-flash": Decimal("0.000075"),
        "llama-3": Decimal("0.0001"),
        "default": Decimal("0.005"),
    }

    @classmethod
    def calculate_cost(
        cls, model: str, prompt_tokens: int, completion_tokens: int, response: Optional[dict] = None
    ) -> Decimal:
        """
        High-Precision Billing Calculation.
        Priority:
        1. Provider-reported cost via LiteLLM.
        2. Alfred's logical fallback rates per model family.
        """
        try:
            if response:
                # Use standard completion_cost (reports in USD)
                usd_cost = completion_cost(completion_response=response)
                # Convert to Org-Credits
                return Decimal(str(usd_cost)) * cls.USD_TO_CREDITS
        except Exception:
            # Swallow parsing errors and proceed to fallback
            pass

        # Heuristic Logic
        rate = cls._get_rate_for_model(model)
        total_tokens = prompt_tokens + completion_tokens
        return (Decimal(total_tokens) / Decimal("1000")) * rate * cls.USD_TO_CREDITS

    @classmethod
    def _get_rate_for_model(cls, model: str) -> Decimal:
        """Pattern-matching tier identification."""
        model_lower = model.lower()
        for key, rate in cls.FALLBACK_RATES.items():
            if key in model_lower:
                return rate
        return cls.FALLBACK_RATES["default"]

    @classmethod
    def estimate_cost(cls, model: str, estimated_tokens: int) -> Decimal:
        """Pre-flight predictor used to deny requests before they incur vendor costs."""
        rate = cls._get_rate_for_model(model)
        return (Decimal(estimated_tokens) / Decimal("1000")) * rate * cls.USD_TO_CREDITS


# --- 2. The Balancer: Multi-Tier Quota Allocation ---


class QuotaManager:
    """
    Inland Revenue for AI Tokens.
    Implements the core 'Elastic Quota' algorithm.
    """

    def __init__(self, session: Session):
        self.session = session
        self._org_settings: Optional[OrgSettings] = None

    @property
    def org_settings(self) -> OrgSettings:
        """Dynamic governance settings pulled from DB with JIT creation."""
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
        priority: ProjectPriority = ProjectPriority.NORMAL,
    ) -> QuotaCheckResult:
        """
        Governance Cascading Logic.
        Resolves the question: 'Who pays for this request?'

        Logic Cascade:
        1. Personal: Does the user have enough of their own monthly allowance?
        2. Critical Bypass: If priority=CRITICAL, can they borrow from the team pool?
        3. Vacation Share: Is there 'Idle Liquidity' from out-of-office colleagues?
        4. Denial: Block request and provide 'Approval Workflow' instructions.
        """
        # --- TIER 1: SELF-RELIANCE ---
        if user.available_quota >= estimated_cost:
            return QuotaCheckResult(
                allowed=True,
                source="personal",
                available_credits=user.available_quota,
                message="Deducting from personal allowance.",
            )

        # --- TIER 2: MISSION-CRITICAL OVERRIDE ---
        if priority == ProjectPriority.CRITICAL and self.org_settings.allow_priority_bypass:
            team_pool = self._get_total_team_pool(user)
            if team_pool >= estimated_cost:
                return QuotaCheckResult(
                    allowed=True,
                    source="priority_bypass",
                    available_credits=team_pool,
                    message="Critical bypass: Utilizing shared team liquidity.",
                )

        # --- TIER 3: VACATION LIQUIDITY ---
        if self.org_settings.allow_vacation_sharing:
            vacation_credits = self._get_vacation_share_credits(user)
            if vacation_credits >= estimated_cost:
                return QuotaCheckResult(
                    allowed=True,
                    source="vacation_share",
                    available_credits=vacation_credits,
                    message="Idle liquidity boost: Using credits from teammates on vacation.",
                )

        # --- TIER 4: HARD STOP & WORKFLOW ---
        return QuotaCheckResult(
            allowed=False,
            source="none",
            available_credits=user.available_quota,
            message="Quota exceeded. Approval required.",
            requires_approval=True,
            approval_instructions={
                "process": "Manager Approval Required",
                "steps": [
                    "POST /v1/approvals with justification.",
                    "Wait for Team Admin review.",
                    "Credits auto-replenish upon approval.",
                ],
                "endpoint": "/v1/approvals",
            },
        )

    def _get_total_team_pool(self, user: User) -> Decimal:
        """Aggregate available credits across all user memberships."""
        total = Decimal("0.00")
        statement = select(Team).join(TeamMemberLink).where(TeamMemberLink.user_id == user.id)
        teams = self.session.exec(statement).all()
        for team in teams:
            total += team.available_pool
        return total

    def _get_vacation_share_credits(self, user: User) -> Decimal:
        """Heuristic: If 1+ member is away, unlock a capped percentage of the pool."""
        total_vacation_credits = Decimal("0.00")
        statement = select(Team).join(TeamMemberLink).where(TeamMemberLink.user_id == user.id)
        teams = self.session.exec(statement).all()
        for team in teams:
            if self._get_vacation_members(team, exclude_user=user):
                total_vacation_credits += team.vacation_share_limit
        return total_vacation_credits

    def _get_vacation_members(self, team: Team, exclude_user: User) -> List[User]:
        """Find colleagues whose status is 'ON_VACATION'."""
        statement = (
            select(User)
            .join(TeamMemberLink)
            .where(TeamMemberLink.team_id == team.id)
            .where(User.id != exclude_user.id)
            .where(User.status == UserStatus.ON_VACATION)
        )
        return list(self.session.exec(statement).all())

    def deduct_quota(
        self, user: User, cost: Decimal, source: str, team: Optional[Team] = None
    ) -> None:
        """Atomic deduction logic across ledgers."""
        if source == "personal":
            user.used_tokens += cost
            user.last_request_at = datetime.now(timezone.utc)
            self.session.add(user)
        elif source in ("team_pool", "priority_bypass", "vacation_share"):
            if team is None:
                # Default to primary team
                team = self.session.exec(
                    select(Team).join(TeamMemberLink).where(TeamMemberLink.user_id == user.id)
                ).first()
            if team:
                team.used_pool += cost
                team.updated_at = datetime.now(timezone.utc)
                self.session.add(team)
            user.last_request_at = datetime.now(timezone.utc)
            self.session.add(user)
        self.session.commit()

    def add_quota(self, user: User, amount: Decimal) -> None:
        """Atomic quota injection."""
        user.personal_quota += amount
        user.updated_at = datetime.now(timezone.utc)
        self.session.add(user)
        self.session.commit()


# --- 3. Behavioral Scant: The Gamification Layer ---


class EfficiencyScorer:
    """
    The 'Token-Frugality' Metric.
    Calculates how well a user utilizes their prompt budget.
    Score = (Complexity of Output / Verbosity of Input).
    """

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def calculate_efficiency_score(prompt_tokens: int, completion_tokens: int) -> Decimal:
        """Ordinal efficiency score."""
        if prompt_tokens == 0:
            return Decimal("0.00")
        return round(Decimal(completion_tokens) / Decimal(prompt_tokens), 4)

    def get_leaderboard(
        self, period_type: str = "daily", limit: int = 10
    ) -> List[LeaderboardEntry]:
        """Fetch the current leaderboard entries for a given period."""
        now = datetime.now(timezone.utc)
        if period_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "weekly":
            period_start = (now - timedelta(days=now.weekday())).replace(
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

    def update_leaderboard(
        self, user: User, request_log: RequestLog, period_type: str = "daily"
    ) -> LeaderboardEntry:
        """Asynchronous update of the performance leaderboard."""
        now = datetime.now(timezone.utc)

        # Temporal bucketing logic
        if period_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "weekly":
            period_start = (now - timedelta(days=now.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        statement = select(LeaderboardEntry).where(
            LeaderboardEntry.user_id == user.id,
            LeaderboardEntry.period_type == period_type,
            LeaderboardEntry.period_start == period_start,
        )
        entry = self.session.exec(statement).first() or LeaderboardEntry(
            user_id=user.id,
            period_start=period_start,
            period_end=period_start
            + (timedelta(days=1) if period_type == "daily" else timedelta(weeks=1)),
            period_type=period_type,
        )

        # Atomic Aggregation
        entry.total_requests += 1
        entry.total_prompt_tokens += request_log.prompt_tokens
        entry.total_completion_tokens += request_log.completion_tokens
        entry.total_cost_credits += request_log.cost_credits

        if entry.total_prompt_tokens > 0:
            entry.avg_efficiency_score = Decimal(entry.total_completion_tokens) / Decimal(
                entry.total_prompt_tokens
            )

        entry.updated_at = now
        self.session.add(entry)
        self.session.commit()
        return entry


# --- 4. The Auditing Layer ---


class RequestLogger:
    """Ensures a perfect paper trail for compliance."""

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
        provider: str = "openai",
    ) -> RequestLog:
        """Storage logic with conditional redaction for Privacy-By-Design."""
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        messages_json = None
        response_content = None

        # Content Redaction for High-Privacy Requests
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
            total_tokens=usage.get("total_tokens", prompt_tokens + completion_tokens),
            cost_credits=cost_credits,
            quota_source=quota_source,
            priority=request.project_priority or user.default_priority,
            strict_privacy=strict_privacy,
            messages_json=messages_json,
            response_content=response_content,
            efficiency_score=EfficiencyScorer.calculate_efficiency_score(
                prompt_tokens, completion_tokens
            ),
            latency_ms=latency_ms,
        )

        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log


# --- 5. Security & Orchestration ---


class AuthManager:
    """Security Boundary Manager."""

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """One-way cryptographically secure trace of the API secret."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def generate_api_key() -> Tuple[str, str]:
        """Entropy source for new user secrets."""
        plaintext = f"{settings.api_key_prefix}{secrets.token_urlsafe(settings.api_key_length)}"
        return plaintext, AuthManager.hash_api_key(plaintext)


class LLMProxy:
    """The High-Availability Gateway."""

    @staticmethod
    async def forward_request(
        request: ChatCompletionRequest, api_keys: Optional[dict] = None
    ) -> dict:
        """
        Intelligent Routing with Resilience.
        Automatically retries on provider failure with exponential backoff.
        """
        # Translation: Alfred -> Provider
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        kwargs = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": 1.0,
            "acompletion": True,  # Asynchronous non-blocking call
        }
        if request.max_tokens:
            kwargs["max_tokens"] = request.max_tokens
        if api_keys:
            kwargs.update(api_keys)

        # Execution with Tracing & Retries
        if TENACITY_AVAILABLE:

            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                before_sleep=before_sleep_log(retry_logger, logging.WARNING),
                reraise=True,
            )
            async def _call():
                return await completion(**kwargs)

            response = await _call()
        else:
            response = await completion(**kwargs)

        return response.model_dump() if hasattr(response, "model_dump") else dict(response)


# --- 6. The Exception Desk: Manual Overrides ---


class ApprovalManager:
    """Handles the 'Human-in-the-Loop' governance workflow."""

    def __init__(self, session: Session):
        self.session = session

    def create_request(
        self,
        user: User,
        requested_credits: Decimal,
        reason: str,
        priority: ProjectPriority = ProjectPriority.HIGH,
        team_id: Optional[str] = None,
    ) -> ApprovalRequest:
        """Registers a formal intent to consume more than the allocated budget."""
        import uuid as uuid_module

        approval = ApprovalRequest(
            user_id=user.id,
            team_id=uuid_module.UUID(team_id) if team_id else None,
            requested_credits=requested_credits,
            reason=reason,
            priority=priority,
            status="pending",
        )
        self.session.add(approval)
        self.session.commit()
        return approval

    def approve(
        self, approval_id: str, approver_id: str, approved_credits: Optional[Decimal] = None
    ) -> ApprovalRequest:
        """Finalizes an audit-compliant quota injection."""
        import uuid as uuid_module

        approval = self.session.exec(
            select(ApprovalRequest).where(ApprovalRequest.id == uuid_module.UUID(approval_id))
        ).first()
        if not approval:
            raise ValueError("Invalid workflow ID.")

        approval.status = "approved"
        approval.approved_by = uuid_module.UUID(approver_id)
        approval.approved_credits = approved_credits or approval.requested_credits
        approval.resolved_at = datetime.now(timezone.utc)

        # Atomic Replenishment
        user = self.session.exec(select(User).where(User.id == approval.user_id)).first()
        if user:
            user.personal_quota += approval.approved_credits
            user.updated_at = datetime.now(timezone.utc)
            self.session.add(user)

        self.session.add(approval)
        self.session.commit()
        return approval

    def allocate_vacation_liquidity(
        self, user_id: uuid.UUID, team_id: uuid.UUID, requested_quota: Decimal
    ):
        """Allocate vacation liquidity for non-critical requests."""
        from .models import TeamMemberLink, User, UserStatus

        # Fetch team members on vacation
        vacation_members = self.session.exec(
            select(User).where(
                User.status == UserStatus.ON_VACATION,
                TeamMemberLink.team_id == team_id,
                TeamMemberLink.user_id == User.id,
            )
        ).all()

        total_vacation_quota = sum(
            member.personal_quota - member.used_tokens for member in vacation_members
        )

        if total_vacation_quota >= requested_quota:
            # Allocate quota from vacation pool
            for member in vacation_members:
                available_quota = member.personal_quota - member.used_tokens
                if available_quota > 0:
                    allocation = min(available_quota, requested_quota)
                    member.used_tokens += allocation
                    requested_quota -= allocation
                    self.session.add(member)
                    if requested_quota == 0:
                        break
            self.session.commit()
            return True
        return False


def allocate_vacation_liquidity(session: Session, user_id, team_id, requested_quota: Decimal):
    """Compatibility wrapper: allow tests and callers to call a module-level function.

    Args:
        session: SQLModel/SQLAlchemy session
        user_id: UUID of the requesting user
        team_id: UUID of the team
        requested_quota: amount requested from vacation liquidity

    Returns:
        bool indicating whether allocation succeeded
    """
    mgr = ApprovalManager(session)
    return mgr.allocate_vacation_liquidity(user_id, team_id, requested_quota)
