"""
TokenPool - AI Token Quota Manager
FastAPI application with quota management, privacy modes, and efficiency tracking.
"""

import time
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, SQLModel, create_engine, select
from pydantic import BaseModel

from .config import settings
from .logging_config import setup_logging, get_logger, user_id_var
from .middleware import setup_middleware
from .exceptions import (
    setup_exception_handlers,
    QuotaExceededException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    LLMProviderException
)
from .models import (
    User, Team, TeamMemberLink, RequestLog, LeaderboardEntry,
    OrgSettings, ApprovalRequest,
    UserStatus, ProjectPriority,
    ChatCompletionRequest, ChatCompletionResponse, ChatChoice,
    ChatMessage, UsageInfo, QuotaErrorResponse
)
from .logic import (
    QuotaManager, CreditCalculator, EfficiencyScorer,
    RequestLogger, AuthManager, LLMProxy, ApprovalManager
)

# Initialize logging
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    mask_pii=settings.mask_pii_in_logs,
    log_file=settings.log_file
)
logger = get_logger(__name__)


# -------------------------------------------------------------------
# Database Configuration
# -------------------------------------------------------------------

# Create engine using settings
connect_args = {"check_same_thread": False} if settings.is_sqlite else {}
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args=connect_args,
    pool_pre_ping=True  # Enable connection health checks
)


# -------------------------------------------------------------------
# Lifespan & Database Setup
# -------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - setup and teardown."""
    logger.info(
        "Starting TokenPool",
        extra_data={
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug
        }
    )
    
    # Create tables (in development/test only - use Alembic in production)
    if settings.environment in ("development", "test"):
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created (dev/test mode)")
    
    # Initialize default organization settings
    with Session(engine) as session:
        org_settings = session.exec(select(OrgSettings)).first()
        if not org_settings:
            org_settings = OrgSettings()
            session.add(org_settings)
            session.commit()
            logger.info("Default organization settings initialized")
    
    yield
    
    logger.info("Shutting down TokenPool")


# -------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    description="Open Source Multi-LLM Proxy Gateway with Quota Management",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Setup exception handlers
setup_exception_handlers(app)

# Setup middleware (includes rate limiting, request context, etc.)
setup_middleware(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Dependencies
# -------------------------------------------------------------------

def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session


async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    session: Session = Depends(get_session)
) -> User:
    """
    Authenticate user via API key.
    Supports both Authorization: Bearer <key> and X-API-Key: <key> headers.
    """
    api_key = None
    
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization[7:]
    elif x_api_key:
        api_key = x_api_key
    
    if not api_key:
        raise AuthenticationException(
            "Missing API key. Provide via 'Authorization: Bearer <key>' or 'X-API-Key' header"
        )
    
    user = AuthManager.authenticate(session, api_key)
    
    if not user:
        raise AuthenticationException("Invalid API key")
    
    if user.status == UserStatus.SUSPENDED:
        raise AuthorizationException("Account suspended")
    
    # Set user ID in logging context
    user_id_var.set(str(user.id))
    
    return user


def get_privacy_mode(
    x_privacy_mode: Optional[str] = Header(None, alias="X-Privacy-Mode"),
    user: User = Depends(get_current_user)
) -> bool:
    """
    Determine if strict privacy mode is enabled.
    Can be set via X-Privacy-Mode: strict header or user's default preference.
    """
    if x_privacy_mode and x_privacy_mode.lower() == "strict":
        return True
    return user.strict_privacy_default


# -------------------------------------------------------------------
# Request/Response Models
# -------------------------------------------------------------------

class UserCreate(BaseModel):
    """Create a new user."""
    email: str
    name: str
    personal_quota: Optional[Decimal] = Decimal("1000.00")


class UserResponse(BaseModel):
    """User information response."""
    id: str
    email: str
    name: str
    status: str
    personal_quota: float
    used_tokens: float
    available_quota: float
    default_priority: str


class ApiKeyResponse(BaseModel):
    """API key creation response."""
    api_key: str
    message: str


class TeamCreate(BaseModel):
    """Create a new team."""
    name: str
    description: Optional[str] = None
    common_pool: Optional[Decimal] = Decimal("10000.00")


class TeamResponse(BaseModel):
    """Team information response."""
    id: str
    name: str
    description: Optional[str]
    common_pool: float
    used_pool: float
    available_pool: float
    member_count: int


class ApprovalRequestCreate(BaseModel):
    """Create an approval request."""
    requested_credits: Decimal
    reason: str
    priority: Optional[ProjectPriority] = ProjectPriority.HIGH


class ApprovalResponse(BaseModel):
    """Approval request response."""
    id: str
    status: str
    requested_credits: float
    approved_credits: Optional[float]
    reason: str
    created_at: str


class LeaderboardResponse(BaseModel):
    """Leaderboard entry response."""
    rank: int
    user_id: str
    user_name: str
    total_requests: int
    avg_efficiency_score: float
    total_cost_credits: float


class QuotaStatusResponse(BaseModel):
    """User quota status response."""
    personal_quota: float
    used_tokens: float
    available_quota: float
    team_pool_available: float
    vacation_share_available: float
    status: str


# -------------------------------------------------------------------
# Main Chat Completions Endpoint
# -------------------------------------------------------------------

@app.post("/v1/chat/completions", response_model=None)
async def chat_completions(
    request: ChatCompletionRequest,
    user: User = Depends(get_current_user),
    strict_privacy: bool = Depends(get_privacy_mode),
    session: Session = Depends(get_session),
    x_project_priority: Optional[str] = Header(None, alias="X-Project-Priority")
):
    """
    OpenAI-compatible chat completions endpoint with quota management.
    
    Features:
    - Quota checking with personal/team/vacation sharing
    - Priority-based overrides for critical projects
    - Privacy mode (X-Privacy-Mode: strict) - no message logging
    - Efficiency scoring and leaderboard tracking
    - Dynamic pricing via LiteLLM
    """
    start_time = time.time()
    
    # Determine priority
    priority = request.project_priority
    if x_project_priority:
        try:
            priority = ProjectPriority(x_project_priority.lower())
        except ValueError:
            pass
    if priority is None:
        priority = user.default_priority
    
    # Estimate cost for quota check
    estimated_tokens = sum(len(m.content.split()) * 1.3 for m in request.messages) + 500
    estimated_cost = CreditCalculator.estimate_cost(request.model, int(estimated_tokens))
    
    # Check quota
    quota_manager = QuotaManager(session)
    quota_result = quota_manager.check_quota(user, estimated_cost, priority)
    
    if not quota_result.allowed:
        # Return 403 with approval process info
        error_response = QuotaErrorResponse(
            error="Quota exceeded",
            code="quota_exceeded",
            quota_remaining=user.available_quota,
            message=quota_result.message,
            approval_process=quota_result.approval_instructions
        )
        return JSONResponse(
            status_code=403,
            content=error_response.model_dump()
        )
    
    # Check org-wide privacy setting
    org_settings = quota_manager.org_settings
    if org_settings.force_strict_privacy:
        strict_privacy = True
    
    try:
        # Forward request to LLM provider
        response = await LLMProxy.forward_request(request)
        
        # Calculate actual cost
        usage = response.get("usage", {})
        actual_cost = CreditCalculator.calculate_cost(
            model=request.model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            response=response
        )
        
        # Deduct quota
        quota_manager.deduct_quota(user, actual_cost, quota_result.source)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Log request
        request_logger = RequestLogger(session)
        log = request_logger.log_request(
            user=user,
            request=request,
            response=response,
            cost_credits=actual_cost,
            quota_source=quota_result.source,
            strict_privacy=strict_privacy,
            latency_ms=latency_ms,
            provider=_detect_provider(request.model)
        )
        
        # Update leaderboard
        scorer = EfficiencyScorer(session)
        scorer.update_leaderboard(user, log, "daily")
        
        # Refresh user to get updated quota
        session.refresh(user)
        
        # Build response with TokenPool extensions
        choices = response.get("choices", [])
        response_choices = [
            ChatChoice(
                index=c.get("index", i),
                message=ChatMessage(
                    role=c.get("message", {}).get("role", "assistant"),
                    content=c.get("message", {}).get("content", "")
                ),
                finish_reason=c.get("finish_reason", "stop")
            )
            for i, c in enumerate(choices)
        ]
        
        return ChatCompletionResponse(
            id=response.get("id", f"chatcmpl-{uuid.uuid4().hex[:24]}"),
            object="chat.completion",
            created=response.get("created", int(time.time())),
            model=response.get("model", request.model),
            choices=response_choices,
            usage=UsageInfo(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0)
            ),
            cost_credits=actual_cost,
            quota_source=quota_result.source,
            remaining_quota=user.available_quota
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with LLM provider: {str(e)}"
        )


def _detect_provider(model: str) -> str:
    """Detect the provider based on model name."""
    model_lower = model.lower()
    if "gpt" in model_lower or "openai" in model_lower:
        return "openai"
    elif "claude" in model_lower or "anthropic" in model_lower:
        return "anthropic"
    elif "gemini" in model_lower or "google" in model_lower:
        return "google"
    elif "mistral" in model_lower:
        return "mistral"
    elif "llama" in model_lower:
        return "meta"
    return "unknown"


# -------------------------------------------------------------------
# User Management Endpoints
# -------------------------------------------------------------------

@app.post("/v1/admin/users", response_model=ApiKeyResponse)
async def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Create a new user and return their API key."""
    # Check if email already exists
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate API key
    api_key, api_key_hash = AuthManager.generate_api_key()
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        api_key_hash=api_key_hash,
        personal_quota=user_data.personal_quota
    )
    
    session.add(user)
    session.commit()
    
    return ApiKeyResponse(
        api_key=api_key,
        message="Store this API key securely - it cannot be retrieved later"
    )


@app.get("/v1/users/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        status=user.status.value,
        personal_quota=float(user.personal_quota),
        used_tokens=float(user.used_tokens),
        available_quota=float(user.available_quota),
        default_priority=user.default_priority.value
    )


@app.get("/v1/users/me/quota", response_model=QuotaStatusResponse)
async def get_quota_status(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get detailed quota status including team and vacation sharing."""
    quota_manager = QuotaManager(session)
    
    team_pool = quota_manager._get_total_team_pool(user)
    vacation_share = quota_manager._get_vacation_share_credits(user)
    
    return QuotaStatusResponse(
        personal_quota=float(user.personal_quota),
        used_tokens=float(user.used_tokens),
        available_quota=float(user.available_quota),
        team_pool_available=float(team_pool),
        vacation_share_available=float(vacation_share),
        status=user.status.value
    )


@app.put("/v1/users/me/status")
async def update_user_status(
    status: UserStatus,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user's status (e.g., set to vacation)."""
    user.status = status
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    
    return {"message": f"Status updated to {status.value}"}


@app.put("/v1/users/me/privacy")
async def update_privacy_preference(
    strict_privacy: bool,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update user's default privacy preference."""
    user.strict_privacy_default = strict_privacy
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    
    return {"message": f"Privacy preference updated to {'strict' if strict_privacy else 'normal'}"}


# -------------------------------------------------------------------
# Team Management Endpoints
# -------------------------------------------------------------------

@app.post("/v1/admin/teams", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    session: Session = Depends(get_session)
):
    """Create a new team."""
    team = Team(
        name=team_data.name,
        description=team_data.description,
        common_pool=team_data.common_pool
    )
    
    session.add(team)
    session.commit()
    session.refresh(team)
    
    return TeamResponse(
        id=str(team.id),
        name=team.name,
        description=team.description,
        common_pool=float(team.common_pool),
        used_pool=float(team.used_pool),
        available_pool=float(team.available_pool),
        member_count=0
    )


@app.post("/v1/admin/teams/{team_id}/members/{user_id}")
async def add_team_member(
    team_id: str,
    user_id: str,
    is_admin: bool = False,
    session: Session = Depends(get_session)
):
    """Add a user to a team."""
    # Verify team exists
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Verify user exists
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == uuid.UUID(team_id),
            TeamMemberLink.user_id == uuid.UUID(user_id)
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already in team")
    
    # Add membership
    link = TeamMemberLink(
        team_id=uuid.UUID(team_id),
        user_id=uuid.UUID(user_id),
        is_admin=is_admin
    )
    
    session.add(link)
    session.commit()
    
    return {"message": f"User added to team {'as admin' if is_admin else ''}"}


@app.get("/v1/teams/my-teams")
async def get_my_teams(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get teams the current user belongs to."""
    statement = (
        select(Team)
        .join(TeamMemberLink)
        .where(TeamMemberLink.user_id == user.id)
    )
    teams = session.exec(statement).all()
    
    result = []
    for team in teams:
        # Count members
        member_count = session.exec(
            select(TeamMemberLink).where(TeamMemberLink.team_id == team.id)
        ).all()
        
        result.append(TeamResponse(
            id=str(team.id),
            name=team.name,
            description=team.description,
            common_pool=float(team.common_pool),
            used_pool=float(team.used_pool),
            available_pool=float(team.available_pool),
            member_count=len(member_count)
        ))
    
    return result


# -------------------------------------------------------------------
# Approval Endpoints
# -------------------------------------------------------------------

@app.post("/v1/approvals", response_model=ApprovalResponse)
async def create_approval_request(
    request_data: ApprovalRequestCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a quota approval request."""
    manager = ApprovalManager(session)
    
    approval = manager.create_request(
        user=user,
        requested_credits=request_data.requested_credits,
        reason=request_data.reason,
        priority=request_data.priority
    )
    
    return ApprovalResponse(
        id=str(approval.id),
        status=approval.status,
        requested_credits=float(approval.requested_credits),
        approved_credits=None,
        reason=approval.reason,
        created_at=approval.created_at.isoformat()
    )


@app.get("/v1/approvals/pending")
async def get_pending_approvals(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get pending approval requests (for team admins)."""
    manager = ApprovalManager(session)
    
    # Get user's teams where they are admin
    admin_teams = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.user_id == user.id,
            TeamMemberLink.is_admin == True
        )
    ).all()
    
    all_pending = []
    for link in admin_teams:
        pending = manager.get_pending(str(link.team_id))
        all_pending.extend(pending)
    
    return [
        ApprovalResponse(
            id=str(a.id),
            status=a.status,
            requested_credits=float(a.requested_credits),
            approved_credits=float(a.approved_credits) if a.approved_credits else None,
            reason=a.reason,
            created_at=a.created_at.isoformat()
        )
        for a in all_pending
    ]


@app.post("/v1/approvals/{approval_id}/approve")
async def approve_request(
    approval_id: str,
    approved_credits: Optional[Decimal] = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Approve a quota request (for team admins)."""
    manager = ApprovalManager(session)
    
    try:
        approval = manager.approve(
            approval_id=approval_id,
            approver_id=str(user.id),
            approved_credits=approved_credits
        )
        return {"message": "Request approved", "approved_credits": float(approval.approved_credits)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/v1/approvals/{approval_id}/reject")
async def reject_request(
    approval_id: str,
    reason: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Reject a quota request (for team admins)."""
    manager = ApprovalManager(session)
    
    try:
        manager.reject(
            approval_id=approval_id,
            rejector_id=str(user.id),
            reason=reason
        )
        return {"message": "Request rejected"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------------------------------------------------------
# Leaderboard Endpoints
# -------------------------------------------------------------------

@app.get("/v1/leaderboard")
async def get_leaderboard(
    period: str = "daily",
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """Get the efficiency leaderboard."""
    if period not in ("daily", "weekly", "monthly"):
        raise HTTPException(status_code=400, detail="Invalid period. Use: daily, weekly, monthly")
    
    scorer = EfficiencyScorer(session)
    entries = scorer.get_leaderboard(period, limit)
    
    result = []
    for i, entry in enumerate(entries, 1):
        # Get user name
        user = session.get(User, entry.user_id)
        user_name = user.name if user else "Unknown"
        
        result.append(LeaderboardResponse(
            rank=i,
            user_id=str(entry.user_id),
            user_name=user_name,
            total_requests=entry.total_requests,
            avg_efficiency_score=float(entry.avg_efficiency_score),
            total_cost_credits=float(entry.total_cost_credits)
        ))
    
    return result


# -------------------------------------------------------------------
# Analytics Endpoints
# -------------------------------------------------------------------

@app.get("/v1/analytics/usage")
async def get_usage_analytics(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    days: int = 7
):
    """Get usage analytics for the current user."""
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    statement = (
        select(RequestLog)
        .where(RequestLog.user_id == user.id)
        .where(RequestLog.created_at >= cutoff)
        .order_by(RequestLog.created_at.desc())
    )
    
    logs = session.exec(statement).all()
    
    total_requests = len(logs)
    total_tokens = sum(log.total_tokens for log in logs)
    total_cost = sum(log.cost_credits for log in logs)
    
    # Group by model
    by_model = {}
    for log in logs:
        if log.model not in by_model:
            by_model[log.model] = {"requests": 0, "tokens": 0, "cost": Decimal("0")}
        by_model[log.model]["requests"] += 1
        by_model[log.model]["tokens"] += log.total_tokens
        by_model[log.model]["cost"] += log.cost_credits
    
    # Calculate average efficiency
    avg_efficiency = Decimal("0")
    if logs:
        efficiencies = [log.efficiency_score for log in logs if log.efficiency_score]
        if efficiencies:
            avg_efficiency = sum(efficiencies) / len(efficiencies)
    
    return {
        "period_days": days,
        "total_requests": total_requests,
        "total_tokens": total_tokens,
        "total_cost_credits": float(total_cost),
        "average_efficiency_score": float(avg_efficiency),
        "by_model": {
            model: {
                "requests": data["requests"],
                "tokens": data["tokens"],
                "cost_credits": float(data["cost"])
            }
            for model, data in by_model.items()
        }
    }


# -------------------------------------------------------------------
# Health Check
# -------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "TokenPool",
        "version": "1.0.0",
        "description": "Open Source Multi-LLM Proxy Gateway",
        "docs": "/docs",
        "health": "/health"
    }
