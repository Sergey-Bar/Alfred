from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

# In-memory store for demo purposes
DATA_QUALITY_EVENTS = []


class DataQualityEvent(BaseModel):
    id: int
    timestamp: datetime
    dataset: str
    event_type: str  # e.g., 'drift', 'schema_change', 'missing_values'
    details: Optional[str] = None
    severity: str  # e.g., 'low', 'medium', 'high'


@router.post("/data-quality/events", status_code=status.HTTP_201_CREATED)
def report_data_quality_event(event: DataQualityEvent):
    DATA_QUALITY_EVENTS.append(event)
    return {"message": "Event recorded", "event_id": event.id}


@router.get("/data-quality/events", response_model=List[DataQualityEvent])
def get_data_quality_events(dataset: Optional[str] = None):
    if dataset:
        return [e for e in DATA_QUALITY_EVENTS if e.dataset == dataset]
    return DATA_QUALITY_EVENTS


@router.get("/data-quality/alerts", response_model=List[DataQualityEvent])
def get_high_severity_alerts():
    return [e for e in DATA_QUALITY_EVENTS if e.severity == "high"]
