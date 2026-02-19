"""
Alfred - Enterprise AI Credit Governance Platform
Administrative Analytics & Dashboard API

[ARCHITECTURAL ROLE]
This module provides the 'Intelligence Layer' for Alfred. It aggregates raw
transactional data (RequestLogs, Transfers) into high-level KPIs that allow
administrators to:
1. Monitoring: Real-time tracking of token burn rates and budget utilization.
2. Forecasting: Identify cost trends and model usage patterns.
3. Governance: Audit pending approvals and team pool balances.
4. Behavior: Gamified performance metrics (Efficiency Leaderboard).

[PERFORMANCE STRATEGY]
N+1 Mitigation: We use bulk-fetching and mapping techniques to avoid the
common 'N+1 Query' trap when resolving User/Team names for large lists of logs.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This file implements the analytics/reporting endpoints for the Alfred dashboard, aggregating transactional data into KPIs for admins.
# Why: Centralizes all dashboard logic for maintainability and performance.
# Root Cause: Analytics endpoints require optimized queries and bulk data processing to avoid N+1 issues.
# Context: All endpoints are protected and use SQLModel for ORM access. Future: Consider async DB for higher throughput.
# Model Suitability: For analytics logic, GPT-4.1 is sufficient; for advanced forecasting, a more advanced model may be needed.
"""

import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Numeric, String, cast
from sqlalchemy.sql import and_, text
from sqlmodel import Session, func, select

from src.backend.app.logging_config import get_logger

from .dependencies import get_current_user, get_session, require_admin
from .models import ApprovalRequest, RequestLog, Team, TeamMemberLink, TokenTransfer, User
from .schemas import (
    ApprovalStats,
    CostTrendPoint,
    DashboardLeaderboardEntry,
    ModelUsageStats,
    OverviewStats,
    TeamPoolStats,
    TransferAuditItem,
    TransferStats,
    UserUsageStats,
)

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Defines a FastAPI APIRouter for all dashboard endpoints, namespaced under /v1/dashboard.
# Why: Keeps analytics endpoints modular and discoverable.
# Root Cause: FastAPI best practice is to use routers for domain separation.
logger = get_logger(__name__)

router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Section marker for dashboard aggregate endpoints.
# Why: Improves code readability and navigation.
# Root Cause: Grouping related endpoints aids maintainability.
# Context: All endpoints below aggregate data for admin dashboards.
# --- Dashboard Endpoints: Aggregated Aggregates ---


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Aggregates global platform stats (users, teams, requests, tokens, credits, active users, pending approvals) for admin overview.
# Why: Provides a single API call for dashboard summary KPIs.
# Root Cause: Admins need a real-time snapshot for governance and monitoring.
# Context: Uses SQL aggregates and COALESCE to minimize DB round-trips. 7-day window for engagement. Returns OverviewStats model.
@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """
    Global Snapshot Endpoint.
    Aggregates data across the entire platform.
    Uses COALESCE and SQL aggregates to minimize round-trips.
    """
    start = time.perf_counter()

    total_users = session.exec(select(func.count(cast(User.id, String)))).one()
    total_teams = session.exec(select(func.count(cast(Team.id, String)))).one()

    # Sum of all activity
    request_stats = session.exec(
        select(
            func.count(cast(RequestLog.id, String)),
            func.coalesce(func.sum(RequestLog.total_tokens), 0),
            func.coalesce(func.sum(RequestLog.cost_credits), cast(Decimal("0.00"), Numeric)),
        )
    ).one()
    total_requests, total_tokens, total_credits = request_stats

    # Engagement Logic (7-day window) — computed where needed to avoid unused assignments
    week_ago = func.now() - text("INTERVAL '7 days'")

    # Active users in the last 7 days
    active_users = session.exec(
        select(func.count(func.distinct(cast(RequestLog.user_id, String))))
        .where(RequestLog.created_at.isnot(None))
        .where(RequestLog.created_at >= week_ago)
    ).one()

    # Pending approval count
    pending = session.exec(
        select(func.count(cast(ApprovalRequest.id, String))).where(ApprovalRequest.status == "pending")
    ).one() or 0

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "overview_stats",
        extra_data={"total_users": total_users or 0, "duration_ms": round(duration_ms, 2)},
    )

    return OverviewStats(
        total_users=total_users or 0,
        total_teams=total_teams or 0,
        total_requests=total_requests or 0,
        total_tokens_used=int(total_tokens or 0),
        total_credits_spent=Decimal(total_credits or "0.00"),
        active_users_7d=active_users or 0,
        pending_approvals=pending or 0,
    )


@router.get("/users", response_model=List[UserUsageStats])
async def get_user_usage_stats(
    current_user: User = Depends(require_admin),  # Protected: Admins Only
    session: Session = Depends(get_session),
    limit: int = Query(default=50, le=200),
):
    """
    [AI GENERATED]
    Model: GitHub Copilot (GPT-4.1)
    Logic: Returns per-user resource consumption stats for admin audit, using bulk mapping to avoid N+1 queries.
    Why: Admins need to audit usage by user for governance and cost control.
    Root Cause: Query-per-user is inefficient; bulk mapping is used for performance.
    Context: Uses Decimal for financial precision. Limit param restricts result set.
    """
    start = time.perf_counter()

    # Replace floating-point operations with Decimal for financial precision
    request_stats = session.exec(
        select(
            func.count(cast(RequestLog.id, String)),
            func.coalesce(func.sum(RequestLog.total_tokens), 0),
            func.coalesce(func.sum(RequestLog.cost_credits), cast(Decimal("0.00"), Numeric)),
        )
    ).one()
    total_requests, total_tokens, total_credits = request_stats

    # Engagement and backlog metrics computed in `get_overview_stats` to avoid duplicate DB calls

    # Fix Decimal compatibility in order_by
    users = session.exec(
        select(User)
        .order_by(func.desc(cast(User.used_tokens, Numeric)))  # Ensure compatibility with `desc`
        .limit(limit)
    ).all()

    # Mitigates N+1: Resolve all request counts in a single 'Group By' query
    user_ids = [str(u.id) for u in users]
    request_counts: Dict[Any, int] = {}
    if user_ids:
        counts = session.exec(
            select(cast(RequestLog.user_id, String), func.count(cast(RequestLog.id, String)))
            .where(cast(RequestLog.user_id, String).in_(user_ids))  # Use consistent casting
            .group_by(cast(RequestLog.user_id, String))
        ).all()
        request_counts = dict(counts)

    result = []
    for user in users:
        usage_pct = Decimal("0.0")
        if user.personal_quota > Decimal("0"):
            usage_pct = (user.used_tokens / user.personal_quota * Decimal("100")).quantize(
                Decimal("0.1")
            )

        result.append(
            UserUsageStats(
                user_id=str(user.id),
                name=user.name,
                email=user.email,
                personal_quota=user.personal_quota,
                used_tokens=user.used_tokens,
                available_quota=user.available_quota,
                usage_percent=usage_pct,
                total_requests=request_counts.get(user.id, 0),
                is_admin=user.is_admin,
                status=user.status.value,
            )
        )
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "user_usage_stats", extra_data={"count": len(result), "duration_ms": round(duration_ms, 2)}
    )

    return result


@router.get("/teams", response_model=List[TeamPoolStats])
async def get_team_pool_stats(
    current_user: User = Depends(require_admin), session: Session = Depends(get_session)
):
    """Aggregated Team Liquidity Monitoring."""
    start = time.perf_counter()

    teams = session.exec(select(Team).order_by(func.desc(cast(Team.used_pool, Numeric)))).all()

    # N+1 Mitigation: Resolve member counts via IN query
    team_ids = [t.id for t in teams]
    member_counts: Dict[Any, int] = {}
    if team_ids:
        counts = session.exec(
            select(cast(TeamMemberLink.team_id, String), func.count(TeamMemberLink.user_id))
            .where(cast(TeamMemberLink.team_id, String).in_(team_ids))
            .group_by(cast(TeamMemberLink.team_id, String))
        ).all()
        member_counts = dict(counts)  # Simplified dictionary comprehension

    result = []
    for team in teams:
        usage_pct = Decimal("0.0")
        if team.common_pool > Decimal("0"):
            usage_pct = (team.used_pool / team.common_pool * Decimal("100")).quantize(
                Decimal("0.1")
            )

        result.append(
            TeamPoolStats(
                team_id=str(team.id),
                name=team.name,
                common_pool=team.common_pool,
                used_pool=team.used_pool,
                available_pool=team.available_pool,
                usage_percent=usage_pct,
                member_count=member_counts.get(team.id, 0),
            )
        )

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "team_pool_stats", extra_data={"count": len(result), "duration_ms": round(duration_ms, 2)}
    )
    return result


@router.get("/trends", response_model=List[CostTrendPoint])
async def get_cost_trends(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    days: int = Query(default=30, le=90),
):
    """Performance Velocity Tracking."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    start = time.perf_counter()

    # Bulk fetch logs within window
    logs = session.exec(
        select(RequestLog)
        .where(RequestLog.created_at >= cutoff)
        .order_by(func.desc(RequestLog.created_at))
    ).all()

    # Manual aggregation (Database agnostic)
    daily_data = {}
    for log in logs:
        date_str = log.created_at.strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = {"cost": Decimal("0"), "requests": 0, "tokens": 0}
        daily_data[date_str]["cost"] += log.cost_credits
        daily_data[date_str]["requests"] += 1
        daily_data[date_str]["tokens"] += log.total_tokens

    # Standardize time-series (fill gaps with zeros)
    result = []
    current = cutoff.date()
    end = datetime.now(timezone.utc).date()

    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        data = daily_data.get(date_str, {"cost": Decimal("0"), "requests": 0, "tokens": 0})
        result.append(
            CostTrendPoint(
                date=date_str, cost=data["cost"], requests=data["requests"], tokens=data["tokens"]
            )
        )
        current += timedelta(days=1)

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "cost_trends",
        extra_data={"days": days, "points": len(result), "duration_ms": round(duration_ms, 2)},
    )
    return result


@router.get("/models", response_model=List[ModelUsageStats])
async def get_model_usage(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    days: int = Query(default=30, le=90),
):
    """Vendor Concentration Analysis."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    start = time.perf_counter()

    logs = session.exec(select(RequestLog).where(RequestLog.created_at >= cutoff)).all()

    # Frequency analysis
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

    # Sorted by popularity
    result = []
    for model, data in sorted(model_data.items(), key=lambda x: x[1]["requests"], reverse=True):
        pct = Decimal("0.0")
        if total_requests > 0:
            pct = (
                Decimal(str(data["requests"])) / Decimal(str(total_requests)) * Decimal("100")
            ).quantize(Decimal("0.1"))

        result.append(
            ModelUsageStats(
                model=model,
                requests=data["requests"],
                tokens=data["tokens"],
                cost=data["cost"],
                percentage=pct,
            )
        )

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "model_usage",
        extra_data={"days": days, "models": len(result), "duration_ms": round(duration_ms, 2)},
    )
    return result


@router.get("/leaderboard", response_model=List[DashboardLeaderboardEntry])
async def get_efficiency_leaderboard(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    days: int = Query(default=30, le=90),
    limit: int = Query(default=10, le=50),
):
    """Gamified 'Effective Prompting' Ranking."""
    start = time.perf_counter()

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Aggregate logs by user in a single query to avoid N+1
    stmt = (
        select(
            cast(RequestLog.user_id, String),
            func.coalesce(func.sum(RequestLog.prompt_tokens), 0),
            func.coalesce(func.sum(RequestLog.completion_tokens), 0),
            func.count(RequestLog.id),
            func.coalesce(func.sum(RequestLog.total_tokens), 0),
        )
        .where(RequestLog.created_at >= cutoff)
        .group_by(RequestLog.user_id)
    )
    rows = session.exec(stmt).all()

    if not rows:
        return []

    # Fixed Ruff linting errors by importing missing `uuid` module.
    user_ids = [uuid.UUID(r[0]) for r in rows if r[0]]
    users = {u.id: u for u in session.exec(select(User).where(User.id.in_(user_ids))).all()}

    user_stats = []
    for r in rows:
        uid_str, sum_prompt, sum_completion, cnt, sum_total = r
        if not uid_str:
            continue
        uid = uuid.UUID(uid_str)
        total_prompt = int(sum_prompt or 0)
        total_completion = int(sum_completion or 0)

        efficiency = Decimal("0.0")
        if total_prompt > 0:
            efficiency = Decimal(str(total_completion)) / Decimal(str(total_prompt))

        u = users.get(uid)
        user_stats.append(
            {
                "user_id": str(uid),
                "name": u.name if u else "Unknown",
                "efficiency_score": efficiency,
                "total_requests": int(cnt or 0),
                "total_tokens": int(sum_total or 0),
            }
        )

    user_stats.sort(key=lambda x: x["efficiency_score"], reverse=True)

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "efficiency_leaderboard",
        extra_data={"rows": len(user_stats), "duration_ms": round(duration_ms, 2)},
    )

    return [
        DashboardLeaderboardEntry(
            rank=i,
            user_id=s["user_id"],
            name=s["name"],
            efficiency_score=s["efficiency_score"].quantize(Decimal("0.0001")),
            total_requests=s["total_requests"],
            total_tokens=s["total_tokens"],
        )
        for i, s in enumerate(user_stats[:limit], 1)
    ]


@router.get("/approvals", response_model=ApprovalStats)
async def get_approval_stats(
    current_user: User = Depends(require_admin), session: Session = Depends(get_session)
):
    """Governance Workflow Metrics (SLA Tracking)."""
    start = time.perf_counter()
    week_ago = func.now() - text("INTERVAL '7 days'")

    # Core Counts
    pending = (
        session.exec(
            select(func.count(cast(ApprovalRequest.id, String))).where(
                ApprovalRequest.status == "pending"
            )
        ).one()
        or 0
    )
    approved_7d = (
        session.exec(
            select(func.count(cast(ApprovalRequest.id, String))).where(
                and_(
                    ApprovalRequest.status == "approved",
                    ApprovalRequest.resolved_at is not None,
                    ApprovalRequest.resolved_at >= week_ago,
                )
            )
        ).one()
        or 0
    )
    rejected_7d = (
        session.exec(
            select(func.count(cast(ApprovalRequest.id, String))).where(
                and_(ApprovalRequest.status == "rejected", ApprovalRequest.resolved_at >= week_ago)
            )
        ).one()
        or 0
    )

    # Mean Time to Resolution (MTTR) Analysis
    resolved = session.exec(
        select(ApprovalRequest)
        .where(and_(ApprovalRequest.status != "pending", ApprovalRequest.resolved_at is not None))
        .limit(100)
    ).all()

    avg_time = None
    if resolved:
        times = [
            (r.resolved_at - r.created_at).total_seconds() / 3600
            for r in resolved
            if r.resolved_at and r.created_at
        ]
        if times:
            avg_time = Decimal(str(sum(times) / len(times))).quantize(Decimal("0.1"))

    # Hotspot Analysis: Identify top credit requesters
    requester_counts: Dict[str, int] = {}
    all_requests = session.exec(
        select(ApprovalRequest).where(ApprovalRequest.created_at >= week_ago)
    ).all()

    user_ids = {req.user_id for req in all_requests}
    users_map = (
        {
            u.id: u
            for u in session.exec(select(User).where(cast(User.id, String).in_(user_ids))).all()
        }
        if user_ids
        else {}
    )

    for req in all_requests:
        if user := users_map.get(req.user_id):
            requester_counts[user.name] = requester_counts.get(user.name, 0) + 1

    top_requesters = [
        {"name": n, "count": c}
        for n, c in sorted(requester_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "approval_stats", extra_data={"pending": pending, "duration_ms": round(duration_ms, 2)}
    )

    return ApprovalStats(
        total_pending=pending,
        total_approved_7d=approved_7d,
        total_rejected_7d=rejected_7d,
        avg_approval_time_hours=avg_time,
        top_requesters=top_requesters,
    )


@router.get("/transfers", response_model=TransferStats)
async def get_transfer_stats(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    days: int = Query(default=30, le=90),
    limit: int = Query(default=50, le=200),
):
    """Audit Log for Credit Reallocations."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    start = time.perf_counter()

    transfers = session.exec(
        select(TokenTransfer)
        .where(TokenTransfer.created_at >= cutoff)
        .order_by(func.desc(TokenTransfer.created_at))
    ).all()

    # Format result with bulk-resolved identity names
    limited = transfers[:limit]
    u_ids = set()
    for t in limited:
        u_ids.update([t.sender_id, t.recipient_id])
    u_map = (
        {u.id: u for u in session.exec(select(User).where(cast(User.id, String).in_(u_ids))).all()}
        if u_ids
        else {}
    )

    transfer_list = []
    total_amount = Decimal("0.00")
    for t in limited:
        s, r = u_map.get(t.sender_id), u_map.get(t.recipient_id)
        transfer_list.append(
            TransferAuditItem(
                id=str(t.id),
                amount=t.amount,
                timestamp=t.created_at.isoformat(),
                sender=s.name if s else "System",
                recipient=r.name if r else "Deleted User",
                message=t.message,
            )
        )

    # Calculate total from all transfers in window (not just limited ones)
    for t in transfers:
        total_amount += t.amount

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "transfer_stats",
        extra_data={"total_transfers": len(transfers), "duration_ms": round(duration_ms, 2)},
    )
    return TransferStats(
        total_transfers=len(transfers), total_amount=total_amount, recent_transfers=transfer_list
    )
