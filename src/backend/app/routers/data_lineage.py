from datetime import datetime
from typing import List, Optional

# [AI GENERATED]
# Model: GitHub Copilot (GPT-5 mini)
# Logic: Persist lineage events to the DB using SQLModel to replace ephemeral in-memory storage.
# Why: Ensures events are durable, queryable, and usable for audits and tracing across restarts.
# Root Cause: Demo in-memory lists lost events on restart and were not suitable for production use.
# Context: Requires DB migrations to create `lineage_events` table.
from app.dependencies import get_session
from app.models import LineageEventDB
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, select

router = APIRouter()


class LineageEvent(BaseModel):
    dataset: str
    operation: str  # e.g., 'ingest', 'transform', 'join', 'export'
    source_datasets: Optional[List[str]] = None
    user: Optional[str] = None
    details: Optional[str] = None
    timestamp: Optional[datetime] = None
    trace_id: Optional[str] = None


@router.post("/data-lineage/events", status_code=status.HTTP_201_CREATED)
def record_lineage_event(event: LineageEvent, session: Session = Depends(get_session)):
    ts = event.timestamp or datetime.utcnow()
    db_event = LineageEventDB(
        dataset=event.dataset,
        operation=event.operation,
        source_datasets=event.source_datasets,
        user=event.user,
        details=event.details,
        timestamp=ts,
    )
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return {"message": "Lineage event recorded", "event_id": db_event.id}


@router.get("/data-lineage/events", response_model=List[LineageEvent])
def get_lineage_events(
    dataset: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=5000),
    session: Session = Depends(get_session),
):
    stmt = select(LineageEventDB).offset(skip).limit(limit)
    if dataset:
        stmt = stmt.where(LineageEventDB.dataset == dataset)
    rows = session.exec(stmt).all()
    return [LineageEvent(**r.dict(exclude={"id"})) for r in rows]


@router.get("/data-lineage/trace", response_model=List[LineageEvent])
def trace_data_origin(
    dataset: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(2000, ge=1, le=20000),
    session: Session = Depends(get_session),
):
    # Guard: dataset must be non-empty
    if not dataset:
        raise HTTPException(status_code=400, detail="dataset parameter is required")

    stmt = (
        select(LineageEventDB)
        .where((LineageEventDB.dataset == dataset) | (LineageEventDB.source_datasets is not None))
        .offset(skip)
        .limit(limit)
    )
    rows = session.exec(stmt).all()
    # Filter in-Python for source inclusion to avoid complex JSON queries here
    results = [
        r
        for r in rows
        if r.dataset == dataset or (r.source_datasets and dataset in r.source_datasets)
    ]
    return [LineageEvent(**r.dict(exclude={"id"})) for r in results]
