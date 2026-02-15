
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Implements governance endpoints for token transfers, approvals, and quota management.
# Why: Required for unified governance and audit of credit flows and approvals.
# Root Cause: No AI-generated code header present in legacy router.
# Context: Extend for advanced audit logging, compliance, and governance analytics. For complex workflows, consider Claude Sonnet or GPT-5.1-Codex.

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlmodel import Session, select, func

from ..dependencies import get_current_user, get_session, create_background_task
from ..integrations import emit_token_transfer, emit_approval_requested, emit_approval_resolved
from ..metrics import approval_requests_total, credits_transferred_total
from ..models import (
    ApprovalRequest,
    ProjectPriority,
    RequestLog,
    Team,
    TeamMemberLink,
    TokenTransfer,
    User
)
from ..schemas import (
    ApprovalRequestCreate,
    ApprovalResponse,
    LeaderboardResponse,
    TokenTransferRequest,
    TokenTransferResponse
)
from ..logic import EfficiencyScorer
from ..models import LeaderboardEntry
from .websocket import manager as ws_manager

router = APIRouter(prefix="/v1", tags=["Governance & Credit Reallocation"])

@router.post("/users/me/transfers", response_model=TokenTransferResponse)
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
    # 1. Identify Recipient
    recipient = None
    if transfer.to_user_id:
        try:
            recipient = session.get(User, uuid.UUID(transfer.to_user_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Recipient ID format.")
    elif transfer.recipient_email:
        recipient = session.exec(select(User).where(User.email == transfer.recipient_email)).first()

    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found.")

    if recipient.id == user.id:
        raise HTTPException(status_code=400, detail="Safety Protocol: Self-transfer restricted.")

    # 2. Financial Validation
    transfer_amount = transfer.amount
    if user.available_quota < transfer_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Liquidity Crisis: Insufficient available credits. Balance: {user.available_quota}"
        )

    # 3. Atomic Settlement
    token_transfer = TokenTransfer(
        id=uuid.uuid4(),
        sender_id=user.id,
        recipient_id=recipient.id,
        amount=transfer_amount,
        message=transfer.message or transfer.reason
    )
    
    # Ledger Update
    user.used_tokens += transfer_amount
    recipient.personal_quota += transfer_amount
    
    session.add(token_transfer)
    session.add(user)
    session.add(recipient)
    session.commit()
    session.refresh(token_transfer)

    # Telemetry: Liquidity Velocity
    credits_transferred_total.labels(
        from_user_id=str(user.id),
        to_user_id=str(recipient.id)
    ).inc(float(transfer_amount))

    # 4. Success Notifications
    create_background_task(emit_token_transfer(
        sender_id=str(user.id),
        sender_name=user.name,
        sender_email=user.email,
        recipient_id=str(recipient.id),
        recipient_name=recipient.name,
        recipient_email=recipient.email,
        amount=transfer_amount,
        message=transfer.message or transfer.reason,
        sender_remaining=user.available_quota,
        recipient_new_total=recipient.personal_quota
    ))
    
    return TokenTransferResponse(
        transfer_id=str(token_transfer.id),
        sender_name=user.name,
        recipient_name=recipient.name,
        amount=transfer_amount,
        message=transfer.message or transfer.reason,
        sender_remaining_quota=user.available_quota,
        recipient_new_quota=recipient.personal_quota,
        timestamp=token_transfer.created_at.isoformat()
    )

@router.get("/users/me/transfers")
async def get_transfer_history(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = 20
):
    """Get credit reallocation history for the current user."""
    sent = session.exec(
        select(TokenTransfer).where(TokenTransfer.sender_id == user.id).order_by(TokenTransfer.created_at.desc()).limit(limit)
    ).all()
    
    received = session.exec(
        select(TokenTransfer).where(TokenTransfer.recipient_id == user.id).order_by(TokenTransfer.created_at.desc()).limit(limit)
    ).all()

    # Pre-fetch identities to avoid N+1 mapping
    all_related_ids = {t.recipient_id for t in sent} | {t.sender_id for t in received}
    u_map = {u.id: u for u in session.exec(select(User).where(User.id.in_(all_related_ids))).all()}

    def format_transfer(t: TokenTransfer, is_sent: bool):
        other_user = u_map.get(t.recipient_id if is_sent else t.sender_id)
        return {
            "id": str(t.id),
            "type": "sent" if is_sent else "received",
            "amount": t.amount,
            "other_user": {
                "id": str(other_user.id) if other_user else None,
                "name": other_user.name if other_user else "Unknown",
                "email": other_user.email if other_user else None
            },
            "message": t.message,
            "timestamp": t.created_at.isoformat()
        }

    history = [format_transfer(t, True) for t in sent] + [format_transfer(t, False) for t in received]
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {"transfers": history[:limit]}

@router.post("/approvals", response_model=ApprovalResponse)
async def create_approval_request(
    request_data: ApprovalRequestCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Triggered when a user hits their hard-quota. Provides a mechanism to request additional liquidity."""
    amount = request_data.requested_credits or request_data.requested_amount
    if not amount:
        raise HTTPException(status_code=400, detail="Requested amount is required.")

    approval = ApprovalRequest(
        id=uuid.uuid4(),
        user_id=user.id,
        requested_credits=amount,
        reason=request_data.reason,
        priority=request_data.priority or ProjectPriority.HIGH,
        status="pending"
    )
    
    session.add(approval)
    session.commit()
    session.refresh(approval)

    # Telemetry: Workflow Throughput
    from ..metrics import approval_requests_total
    approval_requests_total.labels(status="pending").inc()

    # Real-time Notification
    create_background_task(ws_manager.broadcast({
        "type": "new_approval_request",
        "user_name": user.name,
        "amount": float(amount),
        "reason": request_data.reason,
        "id": str(approval.id)
    }))

    # Trigger admin notifications
    create_background_task(emit_approval_requested(
        user_id=str(user.id),
        user_name=user.name,
        user_email=user.email,
        requested_credits=float(amount),
        reason=request_data.reason
    ))
    
    return ApprovalResponse(
        id=str(approval.id), status=approval.status,
        requested_credits=approval.requested_credits,
        approved_credits=None, reason=approval.reason,
        created_at=approval.created_at.isoformat()
    )

@router.get("/approvals/pending", response_model=List[ApprovalResponse])
async def get_pending_approvals(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Lists pending requests for all teams where the current user has 'Admin' privileges."""
    if not user.is_admin:
        # Check if they are a team admin
        admin_links = session.exec(select(TeamMemberLink).where(TeamMemberLink.user_id == user.id, TeamMemberLink.is_admin == True)).all()
        if not admin_links:
            raise HTTPException(status_code=403, detail="Access Denied: Administrative privileges required.")
        
        team_ids = [l.team_id for l in admin_links]
        # Get team members
        member_links = session.exec(select(TeamMemberLink).where(TeamMemberLink.team_id.in_(team_ids))).all()
        managed_user_ids = {l.user_id for l in member_links}
        
        all_pending = session.exec(
            select(ApprovalRequest)
            .where(ApprovalRequest.status == "pending")
            .where(ApprovalRequest.user_id.in_(managed_user_ids))
        ).all()
    else:
        # Global Admin: See everything
        all_pending = session.exec(select(ApprovalRequest).where(ApprovalRequest.status == "pending")).all()

    # Pre-fetch identities
    target_ids = {a.user_id for a in all_pending}
    u_map = {u.id: u for u in session.exec(select(User).where(User.id.in_(target_ids))).all()}

    return [
        ApprovalResponse(
            id=str(a.id), status=a.status,
            requested_credits=a.requested_credits,
            approved_credits=a.approved_credits if a.approved_credits else None,
            reason=a.reason, created_at=a.created_at.isoformat(),
            user_name=u_map.get(a.user_id).name if u_map.get(a.user_id) else "Unknown",
            user_email=u_map.get(a.user_id).email if u_map.get(a.user_id) else None
        )
        for a in all_pending
    ]

@router.post("/approvals/{approval_id}/resolve")
async def resolve_approval(
    approval_id: str,
    action: str = Query(..., pattern="^(approve|reject)$"),
    approved_credits: Optional[Decimal] = Body(None),
    reason: Optional[str] = Body(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Sign-off or deny a Quota Injection."""
    from ..logic import ApprovalManager
    mgr = ApprovalManager(session)
    
    try:
        if action == "approve":
            approval = mgr.approve(
                approval_id=approval_id,
                approver_id=str(user.id),
                approved_credits=approved_credits
            )
            
            target = session.get(User, approval.user_id)
            if target:
                create_background_task(emit_approval_resolved(
                    user_id=str(target.id), user_name=target.name,
                    user_email=target.email, approved=True,
                    credits=approval.approved_credits, approver_name=user.name
                ))
            
            # Telemetry: Resolution Approval
            approval_requests_total.labels(status="approved").inc()
            
            return {"msg": "Liquidity Injected.", "amount": approval.approved_credits}
        else:
            # Reject logic
            approval = session.get(ApprovalRequest, uuid.UUID(approval_id))
            if not approval: raise HTTPException(status_code=404, detail="WF not found")
            approval.status = "rejected"
            approval.resolved_at = datetime.now(timezone.utc)
            session.add(approval)
            session.commit()
            
            target = session.get(User, approval.user_id)
            if target:
                create_background_task(emit_approval_resolved(
                    user_id=str(target.id), user_name=target.name,
                    user_email=target.email, approved=False,
                    credits=approval.requested_credits,
                    approver_name=user.name, reason=reason
                ))
            
            # Telemetry: Resolution Rejection
            approval_requests_total.labels(status="rejected").inc()
            
            return {"msg": "Request Denied."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/leaderboard", response_model=List[LeaderboardResponse])
async def get_leaderboard(
    period: str = "daily",
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """Gamified Efficiency Ranking."""
    from ..models import LeaderboardEntry
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid period: daily, weekly, or monthly required.")

    scorer = EfficiencyScorer(session)
    entries = scorer.get_leaderboard(period, limit)
    
    u_map = {u.id: u for u in session.exec(select(User).where(User.id.in_({e.user_id for e in entries}))).all()}

    return [
        LeaderboardResponse(
            rank=i, user_id=str(e.user_id), user_name=u_map.get(e.user_id).name if u_map.get(e.user_id) else "Unknown",
            total_requests=e.total_requests, avg_efficiency_score=e.avg_efficiency_score,
            total_cost_credits=e.total_cost_credits
        )
        for i, e in enumerate(entries, 1)
    ]

@router.get("/analytics/usage")
async def get_usage_analytics(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    days: int = 7
):
    """Personal Spend Analysis."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    logs = session.exec(
        select(RequestLog)
        .where(RequestLog.user_id == user.id)
        .where(RequestLog.created_at >= since)
    ).all()
    
    history = {}
    by_model = {}
    
    for log in logs:
        ds = log.created_at.date().isoformat()
        if ds not in history: history[ds] = {"cost": Decimal("0"), "requests": 0, "tokens": 0}
        if log.model not in by_model: by_model[log.model] = {"cost": Decimal("0"), "requests": 0, "tokens": 0}
        
        history[ds]["cost"] += log.cost_credits
        history[ds]["requests"] += 1
        history[ds]["tokens"] += log.total_tokens
        
        by_model[log.model]["cost"] += log.cost_credits
        by_model[log.model]["requests"] += 1
        by_model[log.model]["tokens"] += log.total_tokens
        
    return {
        "period": f"{days} days", "total_requests": len(logs),
        "total_cost": sum(l.cost_credits for l in logs),
        "history": [{"date": d, "cost": v["cost"]} for d, v in sorted(history.items())],
        "by_model": {m: v["cost"] for m, v in by_model.items()}
    }
