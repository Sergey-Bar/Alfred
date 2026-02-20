"""
"""

from typing import Any

from app.config import settings
from app.database import get_db_session
from app.models import User  # type: ignore
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

router = APIRouter()


@router.get("/health")
def health() -> Any:
    return {"status": "healthy", "version": settings.app_version}


@router.get("/test/users_count")
def users_count(session: Session = Depends(get_db_session)) -> dict:
    """Return a simple count of users in the DB to help tests verify DB wiring."""
    stmt = select(User)
    results = session.exec(stmt)
    count = len(list(results))
    return {"users_count": count}
