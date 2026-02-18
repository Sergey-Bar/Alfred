"""
// [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Lightweight health and test endpoints to surface DB connectivity and seeded user counts for test harnesses.
# Why: Provides a deterministic HTTP endpoint tests can call to verify the application is wired to the test DB and that fixtures seeded users are visible.
# Root Cause: Tests fail intermittently when the app engine and test fixtures use different databases; a simple endpoint helps detect this quickly.
# Context: This file is safe for tests only and exposes no sensitive info. Consider gating detailed endpoints to non-production environments.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_db_session
from app.config import settings
from app.models import User  # type: ignore

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
