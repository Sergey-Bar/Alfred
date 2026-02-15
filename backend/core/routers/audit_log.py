
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Adds audit log API endpoints to expose backend audit logs for admin UI and compliance dashboards.
# Why: Enables frontend to fetch and display audit/activity logs for transparency and compliance.
# Root Cause: No API existed for retrieving audit logs for admin review or analytics.
# Context: This router should be registered in main.py. Future: consider pagination, filtering, and streaming to SIEM.

# Model Suitability: For REST API patterns, GPT-4.1 is sufficient; for advanced analytics, a more advanced model may be preferred.

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from ..dependencies import get_session, require_admin
from ..models import AuditLog
from typing import List, Optional

router = APIRouter(prefix="/v1", tags=["Audit Log"])

@router.get("/admin/audit-logs", response_model=List[dict], dependencies=[Depends(require_admin)])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    session: Session = Depends(get_session)
):
    """
    Retrieve recent audit log entries for admin review.
    Supports pagination for large log volumes.
    """
    logs = session.exec(select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)).all()
    return [
        {
            "id": str(log.id),
            "actor_user_id": str(log.actor_user_id) if log.actor_user_id else None,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details_json,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
