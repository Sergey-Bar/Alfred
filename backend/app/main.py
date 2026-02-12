"""
Alfred - AI Token Quota Manager
FastAPI application with quota management, privacy modes, and efficiency tracking.
"""

import asyncio
import time
import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
import uuid

from fastapi import FastAPI, HTTPException, Header, Depends, Request, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel, create_engine, select
from pydantic import BaseModel
import os

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
    OrgSettings, ApprovalRequest, TokenTransfer,
    UserStatus, ProjectPriority,
    ChatCompletionRequest, ChatCompletionResponse, ChatChoice,
    ChatMessage, UsageInfo, QuotaErrorResponse
)
from .logic import (
    QuotaManager, CreditCalculator, EfficiencyScorer,
    RequestLogger, AuthManager, LLMProxy, ApprovalManager
)
from .integrations import (
    setup_notifications, get_notification_manager,
    NotificationEvent, EventType,
    emit_quota_exceeded, emit_quota_warning,
    emit_approval_requested, emit_approval_resolved,
    emit_vacation_status_change, emit_token_transfer
)
from .dashboard import router as dashboard_router

# Prometheus instrumentation is optional in test/dev environments; import
# defensively so tests don't require the package to be installed.
try:
    from prometheus_fastapi_instrumentator import Instrumentator
except Exception:
    Instrumentator = None

# Initialize logging
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    mask_pii=settings.mask_pii_in_logs,
    log_file=settings.log_file
)
logger = get_logger(__name__)


def create_background_task(coro):
    """Create a background task with error logging."""
    async def task_wrapper():
        try:
            await coro
        except Exception as e:
            logger.exception(f"Background task failed: {str(e)}")
    
    return asyncio.create_task(task_wrapper())


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
        "Starting Alfred",
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
    
    # Setup notifications if enabled
    if settings.notifications_enabled:
        notification_manager = setup_notifications(
            slack_webhook_url=settings.slack_webhook_url,
            slack_alerts_webhook_url=settings.slack_alerts_webhook_url,
            slack_bot_token=settings.slack_bot_token,
            teams_webhook_url=settings.teams_webhook_url,
            teams_alerts_webhook_url=settings.teams_alerts_webhook_url,
        )
        configured_count = len(notification_manager.configured_providers)
        if configured_count > 0:
            provider_names = [p.name for p in notification_manager.configured_providers]
            logger.info(
                f"Notifications enabled with {configured_count} provider(s)",
                extra_data={"providers": provider_names}
            )
        else:
            logger.info("Notifications enabled but no providers configured")
    
    yield
    
    # Cleanup notifications
    if settings.notifications_enabled:
        manager = get_notification_manager()
        await manager.close()
    
    logger.info("Shutting down Alfred")


# -------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    description="Enterprise AI Credit Governance Platform - Multi-LLM Proxy Gateway with B2B Quota Management, supporting OpenAI, Anthropic, Azure, AWS Bedrock, and self-hosted models",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Prometheus instrumentation (optional)
if Instrumentator is not None:
    try:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
        logger.info("Prometheus instrumentation configured at /metrics")
    except Exception:
        logger.exception("Failed to initialize Prometheus instrumentation")
else:
    logger.info("Prometheus instrumentation not installed; skipping /metrics")

# Setup exception handlers
setup_exception_handlers(app)

# Setup middleware (includes rate limiting, request context, etc.)
setup_middleware(app)

# CORS middleware - restricted in production
if settings.is_production:
    # Production: only allow specific origins
    cors_origins = [o for o in settings.cors_origins if o != "*"] or ["https://localhost"]
else:
    cors_origins = settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID", "X-Privacy-Mode", "X-Project-Priority"],
)

# Include dashboard router
app.include_router(dashboard_router)

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


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require the current user to be an admin."""
    if not getattr(user, "is_admin", False):
        raise AuthorizationException("Admin privileges required")
    return user


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
    preferences: Optional[dict] = None  # JSON parsed dict



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


class UserUpdate(BaseModel):
    """Update user data."""
    name: Optional[str] = None
    personal_quota: Optional[Decimal] = None
    status: Optional[str] = None


class TeamUpdate(BaseModel):
    """Update team data."""
    name: Optional[str] = None
    description: Optional[str] = None
    common_pool: Optional[Decimal] = None


class ApprovalRequestCreate(BaseModel):
    """Create an approval request.

    Accept either `requested_credits` or `requested_amount` for compatibility with frontend.
    """
    requested_credits: Optional[Decimal] = None
    requested_amount: Optional[Decimal] = None
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
    user_name: Optional[str] = None
    user_email: Optional[str] = None


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
        # Emit quota exceeded notification
        if settings.notifications_enabled and settings.notify_on_quota_exceeded:
            create_background_task(emit_quota_exceeded(
                user_id=str(user.id),
                user_name=user.name,
                user_email=user.email,
                requested_credits=float(estimated_cost),
                available_credits=float(user.available_quota)
            ))
        
        # Return 403 with approval process info
        error_response = QuotaErrorResponse(
            error="Quota exceeded",
            code="quota_exceeded",
            quota_remaining=float(user.available_quota),  # Convert Decimal to float for JSON serialization
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
        
        # Check for quota warning threshold
        if settings.notifications_enabled:
            quota_percentage_used = float(
                (user.used_tokens / user.personal_quota) * 100
            ) if user.personal_quota > 0 else 0
            
            if quota_percentage_used >= settings.notify_quota_warning_threshold:
                create_background_task(emit_quota_warning(
                    user_id=str(user.id),
                    user_name=user.name,
                    user_email=user.email,
                    quota_remaining=float(user.available_quota),
                    quota_total=float(user.personal_quota),
                    percentage_used=quota_percentage_used
                ))
        
        # Build response with Alfred extensions
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

@app.post("/v1/admin/users", response_model=ApiKeyResponse, dependencies=[Depends(require_admin)])
async def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
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
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="create_user",
            target_type="user",
            target_id=str(user.id),
            details={"email": user.email, "name": user.name},
        )
    except Exception:
        pass
    
    return ApiKeyResponse(
        api_key=api_key,
        message="Store this API key securely - it cannot be retrieved later"
    )


@app.get("/v1/admin/users", response_model=List[UserResponse], dependencies=[Depends(require_admin)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all users (admin endpoint)."""
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            status=user.status.value,
            personal_quota=float(user.personal_quota),
            used_tokens=float(user.used_tokens),
            available_quota=float(user.available_quota),
            default_priority=user.default_priority.value
        )
        for user in users
    ]


@app.put("/v1/admin/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Update a user (admin endpoint)."""
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.personal_quota is not None:
        user.personal_quota = user_data.personal_quota
    if user_data.status is not None:
        user.status = UserStatus(user_data.status)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="update_user",
            target_type="user",
            target_id=str(user.id),
            details={"updated_fields": [k for k, v in user_data.dict(exclude_unset=True).items()]},
        )
    except Exception:
        pass
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        status=user.status.value,
        personal_quota=float(user.personal_quota),
        used_tokens=float(user.used_tokens),
        available_quota=float(user.available_quota),
        default_priority=user.default_priority.value,
        preferences=json.loads(user.preferences_json) if user.preferences_json else {}
    )


@app.delete("/v1/admin/users/{user_id}", dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Delete a user (admin endpoint)."""
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="delete_user",
            target_type="user",
            target_id=str(user.id),
            details={"email": user.email},
        )
    except Exception:
        pass

    return {"message": "User deleted successfully"}


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
        default_priority=user.default_priority.value,
        preferences=json.loads(user.preferences_json) if user.preferences_json else {}
    )


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[dict] = None

@app.put("/v1/users/me", response_model=UserResponse)
async def update_my_profile(
    updates: UserProfileUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user profile."""
    if updates.email is not None and updates.email != user.email:
        # Check if email is taken
        existing = session.exec(select(User).where(User.email == updates.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = updates.email
        
    if updates.name is not None:
        user.name = updates.name
    
    if updates.preferences is not None:
        user.preferences_json = json.dumps(updates.preferences)
    
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        status=user.status.value,
        personal_quota=float(user.personal_quota),
        used_tokens=float(user.used_tokens),
        available_quota=float(user.available_quota),
        default_priority=user.default_priority.value,
        preferences=json.loads(user.preferences_json) if user.preferences_json else {}
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
    old_status = user.status
    user.status = status
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    
    # Send vacation status notification if status changed to/from vacation
    if settings.notifications_enabled and settings.notify_on_vacation_change:
        is_vacation_change = (
            old_status == UserStatus.ON_VACATION or status == UserStatus.ON_VACATION
        )
        if is_vacation_change:
            create_background_task(emit_vacation_status_change(
                user_id=str(user.id),
                user_name=user.name,
                user_email=user.email,
                on_vacation=(status == UserStatus.ON_VACATION)
            ))
    
    return {"message": f"Status updated to {status.value}"}


@app.put("/v1/users/me/privacy")
async def update_privacy_preference(
    mode: Optional[str] = Query(None, alias='mode'),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update user's default privacy preference.

    Accepts query param `mode` (e.g., 'strict' or 'normal') as used by the frontend.
    """
    if mode is None:
        raise HTTPException(status_code=400, detail="mode query parameter is required")

    strict_privacy = True if str(mode).lower() in ('strict', 'true', '1') else False

    user.strict_privacy_default = strict_privacy
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    
    return {"message": f"Privacy preference updated to {'strict' if strict_privacy else 'normal'}"}


# -------------------------------------------------------------------
# Credit Reallocation Endpoints
# -------------------------------------------------------------------

class TokenTransferRequest(BaseModel):
    """Request body for credit reallocation.

    Supports either `recipient_email` or `to_user_id` (frontend uses `to_user_id`).
    """
    recipient_email: Optional[str] = None
    to_user_id: Optional[str] = None
    amount: float
    message: Optional[str] = None
    reason: Optional[str] = None


class TokenTransferResponse(BaseModel):
    """Response for credit reallocation."""
    transfer_id: str
    sender_name: str
    recipient_name: str
    amount: float
    message: Optional[str] = None
    sender_remaining_quota: float
    recipient_new_quota: float
    timestamp: str


@app.post("/v1/users/me/transfer", response_model=TokenTransferResponse)
async def transfer_tokens(
    transfer: TokenTransferRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Reallocate credits to another user.
    
    Transfer credits from your allocated quota to another user.
    This enables dynamic budget management when project needs change.
    Notifications will be sent to both parties via configured channels.
    """
    # Validate amount
    if transfer.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")
    
    if Decimal(str(transfer.amount)) > user.available_quota:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient quota. You have {float(user.available_quota):.2f} credits available"
        )
    
    # Find recipient by id (to_user_id) or email
    recipient = None
    if transfer.to_user_id:
        try:
            recipient = session.get(User, uuid.UUID(transfer.to_user_id))
        except Exception:
            recipient = None

    if not recipient and transfer.recipient_email:
        recipient = session.exec(
            select(User).where(User.email == transfer.recipient_email)
        ).first()
    
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    if recipient.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot transfer tokens to yourself")
    
    # Perform the transfer
    transfer_amount = Decimal(str(transfer.amount))
    
    # Deduct from sender (add to used_tokens)
    user.used_tokens += transfer_amount
    user.updated_at = datetime.now(timezone.utc)
    
    # Add to recipient (increase their personal_quota)
    recipient.personal_quota += transfer_amount
    recipient.updated_at = datetime.now(timezone.utc)
    
    # Create transfer record
    token_transfer = TokenTransfer(
        sender_id=user.id,
        recipient_id=recipient.id,
        amount=transfer_amount,
        message=transfer.message or transfer.reason,
        status="completed"
    )
    
    session.add(user)
    session.add(recipient)
    session.add(token_transfer)
    session.commit()
    session.refresh(token_transfer)
    session.refresh(user)
    session.refresh(recipient)
    
    # Send notifications
    create_background_task(emit_token_transfer(
        sender_id=str(user.id),
        sender_name=user.name,
        sender_email=user.email,
        recipient_id=str(recipient.id),
        recipient_name=recipient.name,
        recipient_email=recipient.email,
        amount=float(transfer_amount),
        message=transfer.message or transfer.reason,
        sender_remaining=float(user.available_quota),
        recipient_new_total=float(recipient.personal_quota)
    ))
    
    return TokenTransferResponse(
        transfer_id=str(token_transfer.id),
        sender_name=user.name,
        recipient_name=recipient.name,
        amount=float(transfer_amount),
        message=transfer.message or transfer.reason,
        sender_remaining_quota=float(user.available_quota),
        recipient_new_quota=float(recipient.personal_quota),
        timestamp=token_transfer.created_at.isoformat()
    )


@app.get("/v1/users/me/transfers")
async def get_transfer_history(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = 20
):
    """
    Get credit reallocation history for the current user.
    
    Shows both outgoing and incoming reallocations for audit purposes.
    """
    # Get transfers where user is sender or recipient
    sent_transfers = session.exec(
        select(TokenTransfer)
        .where(TokenTransfer.sender_id == user.id)
        .order_by(TokenTransfer.created_at.desc())
        .limit(limit)
    ).all()
    
    received_transfers = session.exec(
        select(TokenTransfer)
        .where(TokenTransfer.recipient_id == user.id)
        .order_by(TokenTransfer.created_at.desc())
        .limit(limit)
    ).all()
    
    # Collect all related user IDs to fetch in one query
    related_user_ids = set()
    for t in sent_transfers:
        related_user_ids.add(t.recipient_id)
    for t in received_transfers:
        related_user_ids.add(t.sender_id)
        
    related_users = {}
    if related_user_ids:
        users = session.exec(select(User).where(User.id.in_(related_user_ids))).all()
        related_users = {u.id: u for u in users}
    
    # Format response
    def format_transfer(t: TokenTransfer, is_sent: bool) -> dict:
        other_user_id = t.recipient_id if is_sent else t.sender_id
        other_user = related_users.get(other_user_id)
        return {
            "id": str(t.id),
            "type": "sent" if is_sent else "received",
            "amount": float(t.amount),
            "other_user": {
                "id": str(other_user.id) if other_user else None,
                "name": other_user.name if other_user else "Unknown",
                "email": other_user.email if other_user else None
            },
            "message": t.message,
            "timestamp": t.created_at.isoformat()
        }
    
    sent = [format_transfer(t, True) for t in sent_transfers]
    received = [format_transfer(t, False) for t in received_transfers]
    
    return {
        "sent": sent,
        "received": received,
        "total_sent": len(sent),
        "total_received": len(received)
    }


# -------------------------------------------------------------------
# Team Management Endpoints
# -------------------------------------------------------------------

@app.post("/v1/admin/teams", response_model=TeamResponse, dependencies=[Depends(require_admin)])
async def create_team(
    team_data: TeamCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
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
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="create_team",
            target_type="team",
            target_id=str(team.id),
            details={"name": team.name},
        )
    except Exception:
        pass
    
    return TeamResponse(
        id=str(team.id),
        name=team.name,
        description=team.description,
        common_pool=float(team.common_pool),
        used_pool=float(team.used_pool),
        available_pool=float(team.available_pool),
        member_count=0
    )


@app.get("/v1/admin/teams", response_model=List[TeamResponse], dependencies=[Depends(require_admin)])
async def list_teams(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all teams (admin endpoint)."""
    teams = session.exec(select(Team).offset(skip).limit(limit)).all()
    result = []
    for team in teams:
        member_count = len(session.exec(
            select(TeamMemberLink).where(TeamMemberLink.team_id == team.id)
        ).all())
        result.append(TeamResponse(
            id=str(team.id),
            name=team.name,
            description=team.description,
            common_pool=float(team.common_pool),
            used_pool=float(team.used_pool),
            available_pool=float(team.available_pool),
            member_count=member_count
        ))
    return result


@app.put("/v1/admin/teams/{team_id}", response_model=TeamResponse, dependencies=[Depends(require_admin)])
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Update a team (admin endpoint)."""
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team_data.name is not None:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description
    if team_data.common_pool is not None:
        team.common_pool = team_data.common_pool
    
    session.add(team)
    session.commit()
    session.refresh(team)
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="update_team",
            target_type="team",
            target_id=str(team.id),
            details={"updated_fields": [k for k, v in team_data.dict(exclude_unset=True).items()]},
        )
    except Exception:
        pass
    
    member_count = len(session.exec(
        select(TeamMemberLink).where(TeamMemberLink.team_id == team.id)
    ).all())
    
    return TeamResponse(
        id=str(team.id),
        name=team.name,
        description=team.description,
        common_pool=float(team.common_pool),
        used_pool=float(team.used_pool),
        available_pool=float(team.available_pool),
        member_count=member_count
    )


@app.delete("/v1/admin/teams/{team_id}", dependencies=[Depends(require_admin)])
async def delete_team(
    team_id: str,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Delete a team (admin endpoint)."""
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Delete team memberships first
    memberships = session.exec(
        select(TeamMemberLink).where(TeamMemberLink.team_id == team.id)
    ).all()
    for membership in memberships:
        session.delete(membership)
    
    session.delete(team)
    session.commit()
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="delete_team",
            target_type="team",
            target_id=str(team.id),
            details={"name": team.name},
        )
    except Exception:
        pass

    return {"message": "Team deleted successfully"}



class TeamMember(BaseModel):
    id: str
    name: str
    email: str
    is_admin: bool

class AddMemberByEmailRequest(BaseModel):
    email: str
    is_admin: bool = False

@app.get("/v1/admin/teams/{team_id}/members", response_model=List[TeamMember], dependencies=[Depends(require_admin)])
async def get_team_members(
    team_id: str,
    session: Session = Depends(get_session)
):
    """Get members of a team."""
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    members = session.exec(
        select(User, TeamMemberLink.is_admin)
        .join(TeamMemberLink, User.id == TeamMemberLink.user_id)
        .where(TeamMemberLink.team_id == team.id)
    ).all()
    
    return [
        TeamMember(
            id=str(user.id),
            name=user.name,
            email=user.email,
            is_admin=is_admin
        )
        for user, is_admin in members
    ]


@app.post("/v1/admin/teams/{team_id}/members", dependencies=[Depends(require_admin)])
async def add_team_member_email(
    team_id: str, 
    request: AddMemberByEmailRequest,
    session: Session = Depends(get_session)
):
    """Add member by email."""
    # Verify team exists
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found with this email")
        
    # Check existing membership
    existing = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == uuid.UUID(team_id),
            TeamMemberLink.user_id == user.id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already in team")
        
    # Add membership
    link = TeamMemberLink(
        team_id=uuid.UUID(team_id),
        user_id=user.id,
        is_admin=request.is_admin
    )
    session.add(link)
    session.commit()
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=None,
            action="add_team_member",
            target_type="team",
            target_id=str(team.id),
            details={"added_user_id": str(user.id), "added_email": user.email},
        )
    except Exception:
        pass
    
    return {"message": "User added to team successfully"}


@app.post("/v1/admin/teams/{team_id}/members/{user_id}", dependencies=[Depends(require_admin)])
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
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=None,
            action="add_team_member",
            target_type="team",
            target_id=str(team.id),
            details={"added_user_id": str(user.id), "is_admin": is_admin},
        )
    except Exception:
        pass

    return {"message": f"User added to team {'as admin' if is_admin else ''}"}


@app.delete("/v1/admin/teams/{team_id}/members/{user_id}", dependencies=[Depends(require_admin)])
async def remove_team_member(
    team_id: str,
    user_id: str,
    session: Session = Depends(get_session)
):
    """Remove a user from a team."""
    membership = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == uuid.UUID(team_id),
            TeamMemberLink.user_id == uuid.UUID(user_id)
        )
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="User is not a member of this team")
    
    session.delete(membership)
    session.commit()
    try:
        from .audit import log_audit

        log_audit(
            session=session,
            actor_user_id=None,
            action="remove_team_member",
            target_type="team",
            target_id=str(team_id),
            details={"removed_user_id": user_id},
        )
    except Exception:
        pass
    
    return {"message": "User removed from team"}


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
    
    # Support `requested_credits` or `requested_amount` from frontend
    requested = request_data.requested_credits or request_data.requested_amount
    if requested is None:
        raise HTTPException(status_code=400, detail="requested_credits or requested_amount is required")

    approval = manager.create_request(
        user=user,
        requested_credits=requested,
        reason=request_data.reason,
        priority=request_data.priority
    )
    
    # Emit notification for new approval request
    if settings.notifications_enabled and settings.notify_on_approval_request:
        # Use resolved `requested` value (supports requested_credits or requested_amount)
        try:
            requested_float = float(requested)
        except Exception:
            requested_float = None

        # Enqueue notification via Redis/RQ if available, otherwise fall back to in-process
        try:
            from .notifications import enqueue_notification

            enqueue_notification('approval_requested', {
                'user_id': str(user.id),
                'user_name': user.name,
                'user_email': user.email,
                'requested_credits': requested_float,
                'reason': request_data.reason
            })
        except Exception:
            # Last-resort fallback to async task
            create_background_task(emit_approval_requested(
                user_id=str(user.id),
                user_name=user.name,
                user_email=user.email,
                requested_credits=requested_float,
                reason=request_data.reason
            ))
    
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
    
    response = []
    for a in all_pending:
        user_info = session.get(User, a.user_id)
        response.append(ApprovalResponse(
            id=str(a.id),
            status=a.status,
            requested_credits=float(a.requested_credits),
            approved_credits=float(a.approved_credits) if a.approved_credits else None,
            reason=a.reason,
            created_at=a.created_at.isoformat(),
            user_name=user_info.name if user_info else "Unknown",
            user_email=user_info.email if user_info else None
        ))
    
    return response


@app.post("/v1/approvals/{approval_id}/approve")
async def approve_request(
    approval_id: str,
    approved_credits: Optional[Decimal] = None,
    approved_amount: Optional[Decimal] = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Approve a quota request (for team admins)."""
    manager = ApprovalManager(session)
    
    try:
        # Allow query param `approved_amount` from frontend as alias
        actual_approved = approved_amount or approved_credits
        approval = manager.approve(
            approval_id=approval_id,
            approver_id=str(user.id),
            approved_credits=actual_approved
        )
        
        # Send notification to the requester
        if settings.notifications_enabled and settings.notify_on_approval_request:
            # Get the requesting user
            requesting_user = session.get(User, approval.user_id)
            if requesting_user:
                try:
                    from .notifications import enqueue_notification

                    enqueue_notification('approval_resolved', {
                        'user_id': str(requesting_user.id),
                        'user_name': requesting_user.name,
                        'user_email': requesting_user.email,
                        'approved': True,
                        'credits': float(approval.approved_credits),
                        'approver_name': user.name
                    })
                except Exception:
                    create_background_task(emit_approval_resolved(
                        user_id=str(requesting_user.id),
                        user_name=requesting_user.name,
                        user_email=requesting_user.email,
                        approved=True,
                        credits=float(approval.approved_credits),
                        approver_name=user.name
                    ))
        
        return {"message": "Request approved", "approved_credits": float(approval.approved_credits)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/v1/approvals/{approval_id}/reject")
async def reject_request(
    approval_id: str,
    reason: Optional[str] = Body(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Reject a quota request (for team admins)."""
    manager = ApprovalManager(session)
    
    try:
        # Get the approval first to get the requesting user
        from .models import ApprovalRequest as ApprovalRequestModel
        approval_statement = select(ApprovalRequestModel).where(
            ApprovalRequestModel.id == uuid.UUID(approval_id)
        )
        approval = session.exec(approval_statement).first()
        
        manager.reject(
            approval_id=approval_id,
            rejector_id=str(user.id),
            reason=reason or ''
        )
        
        # Send notification to the requester
        if settings.notifications_enabled and settings.notify_on_approval_request and approval:
            requesting_user = session.get(User, approval.user_id)
            if requesting_user:
                try:
                    from .notifications import enqueue_notification

                    enqueue_notification('approval_resolved', {
                        'user_id': str(requesting_user.id),
                        'user_name': requesting_user.name,
                        'user_email': requesting_user.email,
                        'approved': False,
                        'credits': float(approval.requested_credits),
                        'approver_name': user.name,
                        'reason': reason
                    })
                except Exception:
                    create_background_task(emit_approval_resolved(
                        user_id=str(requesting_user.id),
                        user_name=requesting_user.name,
                        user_email=requesting_user.email,
                        approved=False,
                        credits=float(approval.requested_credits),
                        approver_name=user.name,
                        reason=reason
                    ))
        
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
    
    # Bulk fetch users
    user_ids = {entry.user_id for entry in entries}
    users_map = {}
    if user_ids:
        users = session.exec(select(User).where(User.id.in_(user_ids))).all()
        users_map = {u.id: u for u in users}
    
    result = []
    for i, entry in enumerate(entries, 1):
        # Get user name
        user = users_map.get(entry.user_id)
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
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
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
            
    # Calculate daily history
    history = {}
    for log in logs:
        date_str = log.created_at.date().isoformat()
        if date_str not in history:
            history[date_str] = {"tokens": 0, "cost": Decimal("0")}
        history[date_str]["tokens"] += log.total_tokens
        history[date_str]["cost"] += log.cost_credits
        
    history_list = [
        {
            "date": date,
            "tokens": data["tokens"],
            "cost": float(data["cost"])
        }
        for date, data in sorted(history.items())
    ]
    
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
        },
        "history": history_list
    }


# -------------------------------------------------------------------
# Health Check
# -------------------------------------------------------------------


class IntegrationConfig(BaseModel):
    id: str
    name: str
    enabled: bool

@app.get("/v1/config/integrations", response_model=List[IntegrationConfig])
async def get_integrations_config():
    """Get status of configured integrations."""
    manager = get_notification_manager()
    supported = ["slack", "teams", "telegram", "whatsapp"]
    
    # Check what's configured
    configured_names = set()
    if manager:
        configured_names = {p.name.lower() for p in manager.configured_providers}
    
    result = []
    for name in supported:
        display_name = {
            "slack": "Slack",
            "teams": "Microsoft Teams",
            "telegram": "Telegram",
            "whatsapp": "WhatsApp"
        }.get(name, name.capitalize())
        
        result.append(IntegrationConfig(
            id=name,
            name=display_name,
            enabled=name in configured_names
        ))
    return result

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# -------------------------------------------------------------------
# Static Files & SPA Serving (must be last to avoid catch-all conflicts)
# -------------------------------------------------------------------

static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
_static_exists = os.path.exists(static_dir) and os.path.exists(os.path.join(static_dir, "index.html"))

if _static_exists:
    # Mount assets directory
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")

    @app.get("/", include_in_schema=False)
    async def serve_spa():
        """Serve the React SPA index.html."""
        return FileResponse(os.path.join(static_dir, "index.html"))

    @app.get("/{path:path}", include_in_schema=False)
    async def serve_spa_fallback(path: str):
        """Fallback route for SPA - serve index.html for client-side routing."""
        # Don't intercept API routes - let them return proper 404s
        if path.startswith("v1/") or path.startswith("docs") or path.startswith("openapi") or path.startswith("health"):
            raise HTTPException(status_code=404, detail="Not found")
        file_path = os.path.join(static_dir, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Alfred",
            "version": "1.0.0",
            "description": "Open Source AI Token Quota Manager",
            "docs": "/docs",
            "health": "/health"
        }
