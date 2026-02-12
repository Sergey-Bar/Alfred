"""
Alfred Dashboard API
Endpoints for dashboard KPIs and analytics.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlmodel import Session, select, func, and_
from pydantic import BaseModel

from .models import (
    User, Team, TeamMemberLink, RequestLog, ApprovalRequest, TokenTransfer
)


router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])


# -------------------------------------------------------------------
# Response Models
# -------------------------------------------------------------------

class OverviewStats(BaseModel):
    """Overall system statistics."""
    total_users: int
    total_teams: int
    total_requests: int
    total_tokens_used: int
    total_credits_spent: float
    active_users_7d: int
    pending_approvals: int


class UserUsageStats(BaseModel):
    """User token usage statistics."""
    user_id: str
    name: str
    email: str
    personal_quota: float
    used_tokens: float
    available_quota: float
    usage_percent: float
    total_requests: int
    is_admin: bool
    status: str


class TeamPoolStats(BaseModel):
    """Team pool statistics."""
    team_id: str
    name: str
    common_pool: float
    used_pool: float
    available_pool: float
    usage_percent: float
    member_count: int


class CostTrendPoint(BaseModel):
    """Single point in cost trend."""
    date: str
    cost: float
    requests: int
    tokens: int


class ModelUsageStats(BaseModel):
    """Model usage breakdown."""
    model: str
    requests: int
    tokens: int
    cost: float
    percentage: float


class LeaderboardEntry(BaseModel):
    """Efficiency leaderboard entry."""
    rank: int
    user_id: str
    name: str
    efficiency_score: float
    total_requests: int
    total_tokens: int


class ApprovalStats(BaseModel):
    """Approval request statistics."""
    total_pending: int
    total_approved_7d: int
    total_rejected_7d: int
    avg_approval_time_hours: Optional[float]
    top_requesters: List[dict]


# -------------------------------------------------------------------
# Dependencies
# -------------------------------------------------------------------

def get_db_session():
    """Get database session - import from main to avoid circular imports."""
    from .main import engine
    from sqlmodel import Session
    with Session(engine) as session:
        yield session


async def get_current_dashboard_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    session: Session = Depends(get_db_session)
) -> User:
    """
    Authenticate user for dashboard access.
    Returns the authenticated user or raises 401.
    """
    from .logic import AuthManager
    
    # Get API key from either header
    api_key = None
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization[7:]
    elif x_api_key:
        api_key = x_api_key
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide via Authorization: Bearer <key> or X-API-Key header"
        )
    
    user = AuthManager.authenticate(session, api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user


def require_admin(user: User = Depends(get_current_dashboard_user)) -> User:
    """Require admin privileges for endpoint access."""
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required for this endpoint"
        )
    return user


# -------------------------------------------------------------------
# Dashboard Endpoints
# -------------------------------------------------------------------

@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(
    current_user: User = Depends(get_current_dashboard_user),
    session: Session = Depends(get_db_session)
):
    """
    Get overall system statistics.
    Available to all authenticated users.
    """
    # Total counts
    total_users = session.exec(select(func.count(User.id))).one()
    total_teams = session.exec(select(func.count(Team.id))).one()
    
    # Request stats
    request_stats = session.exec(
        select(
            func.count(RequestLog.id),
            func.coalesce(func.sum(RequestLog.total_tokens), 0),
            func.coalesce(func.sum(RequestLog.cost_credits), 0)
        )
    ).one()
    total_requests, total_tokens, total_credits = request_stats
    
    # Active users in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = session.exec(
        select(func.count(func.distinct(RequestLog.user_id)))
        .where(RequestLog.created_at >= week_ago)
    ).one()
    
    # Pending approvals
    pending = session.exec(
        select(func.count(ApprovalRequest.id))
        .where(ApprovalRequest.status == "pending")
    ).one()
    
    return OverviewStats(
        total_users=total_users or 0,
        total_teams=total_teams or 0,
        total_requests=total_requests or 0,
        total_tokens_used=int(total_tokens or 0),
        total_credits_spent=float(total_credits or 0),
        active_users_7d=active_users or 0,
        pending_approvals=pending or 0
    )


@router.get("/users", response_model=List[UserUsageStats])
async def get_user_usage_stats(
    current_user: User = Depends(get_current_dashboard_user),
    session: Session = Depends(get_db_session),
    limit: int = Query(default=50, le=200)
):
    """
    Get user usage statistics.
    Admins see all users, regular users see only themselves.
    """
    users = session.exec(
        select(User)
        .order_by(User.used_tokens.desc())
        .limit(limit)
    ).all()
    
    result = []
    for user in users:
        # Count requests for this user
        req_count = session.exec(
            select(func.count(RequestLog.id))
            .where(RequestLog.user_id == user.id)
        ).one() or 0
        
        usage_pct = 0.0
        if user.personal_quota > 0:
            usage_pct = float(user.used_tokens / user.personal_quota * 100)
        
        result.append(UserUsageStats(
            user_id=str(user.id),
            name=user.name,
            email=user.email,
            personal_quota=float(user.personal_quota),
            used_tokens=float(user.used_tokens),
            available_quota=float(user.available_quota),
            usage_percent=round(usage_pct, 1),
            total_requests=req_count,
            is_admin=getattr(user, 'is_admin', False),
            status=user.status.value
        ))
    
    return result


@router.get("/teams", response_model=List[TeamPoolStats])
async def get_team_pool_stats(
    current_user: User = Depends(get_current_dashboard_user),
    session: Session = Depends(get_db_session)
):
    """Get team pool statistics."""
    teams = session.exec(
        select(Team)
        .order_by(Team.used_pool.desc())
    ).all()
    
    result = []
    for team in teams:
        # Count members
        member_count = session.exec(
            select(func.count(TeamMemberLink.user_id))
            .where(TeamMemberLink.team_id == team.id)
        ).one() or 0
        
        usage_pct = 0.0
        if team.common_pool > 0:
            usage_pct = float(team.used_pool / team.common_pool * 100)
        
        result.append(TeamPoolStats(
            team_id=str(team.id),
            name=team.name,
            common_pool=float(team.common_pool),
            used_pool=float(team.used_pool),
            available_pool=float(team.available_pool),
            usage_percent=round(usage_pct, 1),
            member_count=member_count
        ))
    
    return result


@router.get("/trends", response_model=List[CostTrendPoint])
async def get_cost_trends(
    current_user: User = Depends(get_current_dashboard_user),
    session: Session = Depends(get_db_session),
    days: int = Query(default=30, le=90)
):
    """Get cost trends over time."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Get daily aggregates
    # Note: SQLite uses date() function, PostgreSQL uses DATE()
    logs = session.exec(
        select(RequestLog)
        .where(RequestLog.created_at >= cutoff)
        .order_by(RequestLog.created_at)
    ).all()
    
    # Aggregate by date
    daily_data = {}
    for log in logs:
        date_str = log.created_at.strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = {"cost": Decimal("0"), "requests": 0, "tokens": 0}
        daily_data[date_str]["cost"] += log.cost_credits
        daily_data[date_str]["requests"] += 1
        daily_data[date_str]["tokens"] += log.total_tokens
    
    # Fill in missing dates
    result = []
    current = cutoff.date()
    end = datetime.utcnow().date()
    
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        data = daily_data.get(date_str, {"cost": Decimal("0"), "requests": 0, "tokens": 0})
        result.append(CostTrendPoint(
            date=date_str,
            cost=float(data["cost"]),
            requests=data["requests"],
            tokens=data["tokens"]
        ))
        current += timedelta(days=1)
    
    return result


@router.get("/models", response_model=List[ModelUsageStats])
async def get_model_usage(
    current_user: User = Depends(get_current_dashboard_user),
    session: Session = Depends(get_db_session),
    days: int = Query(default=30, le=90)
):
    """Get model usage breakdown."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    logs = session.exec(
        select(RequestLog)
        .where(RequestLog.created_at >= cutoff)
    ).all()
    
    # Aggregate by model
    model_data = {}
    total_requests = 0
    
    for log in logs:
        model = log.model
        if model not in model_data:
            model_data[model] = {"requests": 0, "tokens": 0, "cost": Decimal("0")}
        model_data[model]["requests"] += 1
        model_data[model]["tokens"] += log.total_tokens
        model_data[model]["cost"] += log.cost_credits
        total_requests += 1
    
    # Convert to response
    result = []
    for model, data in sorted(model_data.items(), key=lambda x: x[1]["requests"], reverse=True):
        pct = (data["requests"] / total_requests * 100) if total_requests > 0 else 0
        result.append(ModelUsageStats(
            model=model,
            requests=data["requests"],
            tokens=data["tokens"],
            cost=float(data["cost"]),
            percentage=round(pct, 1)
        ))
    
    return result


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_efficiency_leaderboard(
    current_user: User = Depends(get_current_dashboard_user),
    session: Session = Depends(get_db_session),
    days: int = Query(default=30, le=90),
    limit: int = Query(default=10, le=50)
):
    """Get efficiency leaderboard."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Get user aggregates
    users = session.exec(select(User)).all()
    
    user_stats = []
    for user in users:
        logs = session.exec(
            select(RequestLog)
            .where(
                and_(
                    RequestLog.user_id == user.id,
                    RequestLog.created_at >= cutoff
                )
            )
        ).all()
        
        if not logs:
            continue
        
        total_prompt = sum(log.prompt_tokens for log in logs)
        total_completion = sum(log.completion_tokens for log in logs)
        total_tokens = sum(log.total_tokens for log in logs)
        
        # Efficiency = completion / prompt (higher is better - more output per input)
        efficiency = 0.0
        if total_prompt > 0:
            efficiency = total_completion / total_prompt
        
        user_stats.append({
            "user_id": str(user.id),
            "name": user.name,
            "efficiency_score": efficiency,
            "total_requests": len(logs),
            "total_tokens": total_tokens
        })
    
    # Sort by efficiency and assign ranks
    user_stats.sort(key=lambda x: x["efficiency_score"], reverse=True)
    
    result = []
    for i, stats in enumerate(user_stats[:limit], 1):
        result.append(LeaderboardEntry(
            rank=i,
            user_id=stats["user_id"],
            name=stats["name"],
            efficiency_score=round(stats["efficiency_score"], 4),
            total_requests=stats["total_requests"],
            total_tokens=stats["total_tokens"]
        ))
    
    return result


@router.get("/approvals", response_model=ApprovalStats)
async def get_approval_stats(
    current_user: User = Depends(get_current_dashboard_user),
    session: Session = Depends(get_db_session)
):
    """Get approval request statistics."""
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Counts
    pending = session.exec(
        select(func.count(ApprovalRequest.id))
        .where(ApprovalRequest.status == "pending")
    ).one() or 0
    
    approved_7d = session.exec(
        select(func.count(ApprovalRequest.id))
        .where(
            and_(
                ApprovalRequest.status == "approved",
                ApprovalRequest.resolved_at >= week_ago
            )
        )
    ).one() or 0
    
    rejected_7d = session.exec(
        select(func.count(ApprovalRequest.id))
        .where(
            and_(
                ApprovalRequest.status == "rejected",
                ApprovalRequest.resolved_at >= week_ago
            )
        )
    ).one() or 0
    
    # Average approval time
    resolved = session.exec(
        select(ApprovalRequest)
        .where(
            and_(
                ApprovalRequest.status != "pending",
                ApprovalRequest.resolved_at.isnot(None)
            )
        )
        .limit(100)
    ).all()
    
    avg_time = None
    if resolved:
        times = []
        for req in resolved:
            if req.resolved_at and req.created_at:
                diff = (req.resolved_at - req.created_at).total_seconds() / 3600
                times.append(diff)
        if times:
            avg_time = sum(times) / len(times)
    
    # Top requesters
    requester_counts = {}
    all_requests = session.exec(
        select(ApprovalRequest)
        .where(ApprovalRequest.created_at >= week_ago)
    ).all()
    
    for req in all_requests:
        user = session.get(User, req.user_id)
        if user:
            name = user.name
            requester_counts[name] = requester_counts.get(name, 0) + 1
    
    top_requesters = [
        {"name": name, "count": count}
        for name, count in sorted(requester_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    return ApprovalStats(
        total_pending=pending,
        total_approved_7d=approved_7d,
        total_rejected_7d=rejected_7d,
        avg_approval_time_hours=round(avg_time, 1) if avg_time else None,
        top_requesters=top_requesters
    )


@router.get("/transfers")
async def get_transfer_stats(
    current_user: User = Depends(get_current_dashboard_user),
    session: Session = Depends(get_db_session),
    days: int = Query(default=30, le=90)
):
    """Get credit reallocation statistics."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    transfers = session.exec(
        select(TokenTransfer)
        .where(TokenTransfer.created_at >= cutoff)
        .order_by(TokenTransfer.created_at.desc())
    ).all()
    
    total_amount = sum(float(t.amount) for t in transfers)
    
    # Format transfers
    transfer_list = []
    for t in transfers[:20]:  # Last 20 transfers
        sender = session.get(User, t.sender_id)
        recipient = session.get(User, t.recipient_id)
        transfer_list.append({
            "id": str(t.id),
            "sender": sender.name if sender else "Unknown",
            "recipient": recipient.name if recipient else "Unknown",
            "amount": float(t.amount),
            "message": t.message,
            "timestamp": t.created_at.isoformat()
        })
    
    return {
        "total_transfers": len(transfers),
        "total_amount": total_amount,
        "recent_transfers": transfer_list
    }
