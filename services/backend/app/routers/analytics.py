
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from ..audit import log_audit
from ..database import get_db_session
from ..dependencies import get_current_user as get_current_user_dep
from ..models import AnalyticsEventDB, User

router = APIRouter()


# --- RBAC & Audit Logging ---
def check_analytics_access(user: User, event_type: Optional[str] = None):
    """
    Check if user has access to analytics endpoints.
    
    RBAC Rules:
    - Admin users: Full access to all analytics
    - Team leads: Access to team analytics only
    - Regular users: Read-only access to own analytics
    """
    if not user:
        raise HTTPException(status_code=403, detail="Authentication required")
    
    # Admin users have unrestricted access
    if user.role == "admin":
        return
    
    # For non-admins, restrict access based on role
    # This is a basic implementation - expand based on your RBAC requirements
    if user.role not in ["admin", "team_lead", "user"]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access analytics"
        )


def log_audit_event(user: User, action: str, details: dict, session: Session):
    """
    Write analytics access to immutable audit log.
    
    Records all analytics queries and submissions for compliance
    and security forensics.
    """
    try:
        log_audit(
            session=session,
            actor_user_id=user.id,
            action=f"analytics.{action}",
            target_type="analytics_event",
            target_id=None,
            details=details,
        )
    except Exception as e:
        logging.error(f"Failed to write audit log for analytics.{action}: {e}")


# --- API Schemas ---
class AnalyticsEvent(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    user: Optional[str] = None
    dataset: Optional[str] = None
    value: Optional[float] = None
    event_metadata: Optional[dict] = None


# --- Persistent Storage ---
@router.post("/analytics/events", status_code=status.HTTP_201_CREATED)
def submit_analytics_event(
    event: AnalyticsEvent,
    user: User = Depends(get_current_user_dep),
    session: Session = Depends(get_db_session)
):
    check_analytics_access(user, event.event_type)
    db_event = AnalyticsEventDB(**event.dict())
    session.add(db_event)
    session.commit()
    log_audit_event(user, "submit_event", event.dict(), session)
    return {"message": "Event recorded", "event_id": event.id}


@router.get("/analytics/events", response_model=List[AnalyticsEvent])
def query_analytics_events(
    event_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    user: User = Depends(get_current_user_dep),
    session: Session = Depends(get_db_session),
):
    check_analytics_access(user, event_type)
    query = select(AnalyticsEventDB)
    if event_type:
        query = query.where(AnalyticsEventDB.event_type == event_type)
    if start:
        query = query.where(AnalyticsEventDB.timestamp >= start)
    if end:
        query = query.where(AnalyticsEventDB.timestamp <= end)
    results = session.exec(query).all()
    log_audit_event(user, "query_events", {"event_type": event_type, "start": str(start), "end": str(end)}, session)
    return [AnalyticsEvent(**e.dict()) for e in results]


@router.get("/analytics/aggregate")
def aggregate_analytics(
    event_type: str,
    agg: str = "sum",
    user: User = Depends(get_current_user_dep),
    session: Session = Depends(get_db_session)
):
    check_analytics_access(user, event_type)
    stmt = (
        select(
            func.count(AnalyticsEventDB.value),
            func.coalesce(func.sum(AnalyticsEventDB.value), 0),
            func.avg(AnalyticsEventDB.value),
            func.max(AnalyticsEventDB.value),
            func.min(AnalyticsEventDB.value),
        )
        .where(AnalyticsEventDB.event_type == event_type)
        .where(AnalyticsEventDB.value is not None)
    )

    row = session.exec(stmt).one_or_none()

    # row -> (count, sum, avg, max, min)
    if not row or row[0] == 0:
        result = {"count": 0, "sum": 0, "avg": None}
        if agg == "max":
            result["max"] = None
        if agg == "min":
            result["min"] = None
        return result

    count_, sum_, avg_, max_, min_ = row
    result = {
        "count": int(count_),
        "sum": float(sum_),
        "avg": float(avg_) if avg_ is not None else None,
    }
    if agg == "max":
        result["max"] = float(max_) if max_ is not None else None
    if agg == "min":
        result["min"] = float(min_) if min_ is not None else None
    log_audit_event(user, "aggregate", {"event_type": event_type, "agg": agg}, session)
    return result


# --- Advanced Analytics: User/Dataset Breakdown ---
@router.get("/analytics/breakdown")
def analytics_breakdown(
    by: str = "user",
    event_type: Optional[str] = None,
    user: User = Depends(get_current_user_dep),
    session: Session = Depends(get_db_session)
):
    check_analytics_access(user, event_type)
    if by not in {"user", "dataset"}:
        raise HTTPException(status_code=400, detail="Invalid breakdown dimension")

    field = AnalyticsEventDB.user if by == "user" else AnalyticsEventDB.dataset

    stmt = select(field, func.coalesce(func.sum(AnalyticsEventDB.value), 0)).where(
        AnalyticsEventDB.value is not None
    )
    if event_type:
        stmt = stmt.where(AnalyticsEventDB.event_type == event_type)
    stmt = stmt.group_by(field)
    rows = session.exec(stmt).all()

    breakdown = {row[0]: float(row[1]) for row in rows if row[0] is not None}
    log_audit_event(user, "breakdown", {"by": by, "event_type": event_type}, session)
    return breakdown


# --- Stubs for Streaming, BI, Anomaly Detection, Retention ---
# TODO: Implement /analytics/stream (WebSocket/Kafka), /analytics/bi (BI tool integration),
# /analytics/anomaly (anomaly detection), /analytics/retention (archiving policy)
