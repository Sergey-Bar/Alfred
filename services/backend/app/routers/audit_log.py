
import csv
import io
import json
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlmodel import Session, select, col

from ..dependencies import get_session, require_admin
from ..models import AuditLog

router = APIRouter(prefix="/v1", tags=["Audit Log"])


@router.get("/admin/audit-logs", response_model=List[dict], dependencies=[Depends(require_admin)])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    action: Optional[str] = Query(default=None, description="Filter by action type"),
    target_type: Optional[str] = Query(default=None, description="Filter by target type"),
    actor_user_id: Optional[str] = Query(default=None, description="Filter by actor user ID"),
    start_date: Optional[str] = Query(default=None, description="Filter from date (ISO 8601)"),
    end_date: Optional[str] = Query(default=None, description="Filter to date (ISO 8601)"),
    session: Session = Depends(get_session),
):
    """
    Retrieve recent audit log entries for admin review.
    Supports pagination and filtering for large log volumes.
    """
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    if action:
        query = query.where(AuditLog.action == action)
    if target_type:
        query = query.where(AuditLog.target_type == target_type)
    if actor_user_id:
        query = query.where(col(AuditLog.actor_user_id) == actor_user_id)
    if start_date:
        try:
            dt = datetime.fromisoformat(start_date)
            query = query.where(AuditLog.created_at >= dt)
        except ValueError:
            pass
    if end_date:
        try:
            dt = datetime.fromisoformat(end_date)
            query = query.where(AuditLog.created_at <= dt)
        except ValueError:
            pass

    query = query.offset(skip).limit(limit)
    logs = session.exec(query).all()

    return [_audit_log_to_dict(log) for log in logs]


@router.get("/admin/audit-logs/export/csv", dependencies=[Depends(require_admin)])
async def export_audit_logs_csv(
    action: Optional[str] = Query(default=None),
    target_type: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    limit: int = Query(default=10000, le=100000),
    session: Session = Depends(get_session),
):
    """
    T141: Export audit logs as CSV file download.

    Streams audit log entries filtered by action, target type, and date range.
    Maximum 100,000 rows per export for memory safety.
    """
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    if action:
        query = query.where(AuditLog.action == action)
    if target_type:
        query = query.where(AuditLog.target_type == target_type)
    if start_date:
        try:
            query = query.where(AuditLog.created_at >= datetime.fromisoformat(start_date))
        except ValueError:
            pass
    if end_date:
        try:
            query = query.where(AuditLog.created_at <= datetime.fromisoformat(end_date))
        except ValueError:
            pass

    query = query.limit(limit)
    logs = session.exec(query).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "actor_user_id", "action", "target_type", "target_id",
        "details", "created_at", "sequence_number", "entry_hash",
    ])

    for log in logs:
        writer.writerow([
            str(log.id),
            str(log.actor_user_id) if log.actor_user_id else "",
            log.action,
            log.target_type or "",
            log.target_id or "",
            json.dumps(log.details_json) if log.details_json else "",
            log.created_at.isoformat() if log.created_at else "",
            getattr(log, "sequence_number", ""),
            getattr(log, "entry_hash", ""),
        ])

    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"alfred_audit_log_{now}.csv"

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/admin/audit-logs/export/json", dependencies=[Depends(require_admin)])
async def export_audit_logs_json(
    action: Optional[str] = Query(default=None),
    target_type: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    limit: int = Query(default=10000, le=100000),
    session: Session = Depends(get_session),
):
    """
    T141: Export audit logs as JSON file download.
    """
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    if action:
        query = query.where(AuditLog.action == action)
    if target_type:
        query = query.where(AuditLog.target_type == target_type)
    if start_date:
        try:
            query = query.where(AuditLog.created_at >= datetime.fromisoformat(start_date))
        except ValueError:
            pass
    if end_date:
        try:
            query = query.where(AuditLog.created_at <= datetime.fromisoformat(end_date))
        except ValueError:
            pass

    query = query.limit(limit)
    logs = session.exec(query).all()

    data = [_audit_log_to_dict(log) for log in logs]

    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"alfred_audit_log_{now}.json"

    return Response(
        content=json.dumps({"audit_logs": data, "count": len(data), "exported_at": now}, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _audit_log_to_dict(log: AuditLog) -> dict:
    """Convert an AuditLog model to a serializable dict."""
    return {
        "id": str(log.id),
        "actor_user_id": str(log.actor_user_id) if log.actor_user_id else None,
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "details": log.details_json,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "sequence_number": getattr(log, "sequence_number", None),
        "entry_hash": getattr(log, "entry_hash", None),
    }
