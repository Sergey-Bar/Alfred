"""
[AI GENERATED]
Model: GitHub Copilot (GPT-5 mini)
Logic: Centralized shared pytest fixtures used across unit, integration and E2E tests.
Why: Consolidate duplicate fixtures and provide a single source of truth for engine/session/test client and credentials.
Root Cause: Multiple `conftest.py` files defined overlapping fixtures with slightly different behavior.
Context: Adapter conftest files may still override behavior for special cases (e.g., StaticPool). This module aims to provide safe defaults.
Model Suitability: Simple fixture glue — human review recommended.
"""

import logging
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)


# Ensure app package is importable (match other conftest behavior)
src_backend_dir = Path(__file__).parent.parent / "src" / "backend"
if src_backend_dir.exists():
    if str(src_backend_dir) not in sys.path:
        sys.path.insert(0, str(src_backend_dir))


def make_engine(test_database_url: str = "sqlite:///:memory:", static_pool: bool = False):
    """Create an SQLModel engine for tests.

    - `static_pool=True` uses `StaticPool` (useful for sharing an in-memory DB across threads).
    """
    if static_pool:
        engine = create_engine(
            test_database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(
            test_database_url,
            connect_args={"check_same_thread": False},
        )
    return engine


@pytest.fixture(scope="function")
def engine():
    """Default engine fixture (isolated in-memory DB). Adapter conftests may override this.

    Creates metadata before yielding and drops after.
    """
    engine = make_engine()
    try:
        # Import app models to register metadata if available
        try:
            import app.models  # noqa: F401
        except Exception:
            pass
        SQLModel.metadata.create_all(engine)
        yield engine
    finally:
        try:
            SQLModel.metadata.drop_all(engine)
        except Exception:
            pass


@pytest.fixture(scope="function")
def session(engine):
    """Provide a SQLModel Session bound to the test engine.

    Rolls back after each test to avoid cross-test contamination.
    """
    with Session(engine) as s:
        yield s
        try:
            s.rollback()
        except Exception:
            pass


@pytest.fixture(scope="function")
def test_user(session):
    try:
        from app.models import User, UserStatus
    except Exception:
        # Minimal fallback dataclass-like object if models are not importable
        class User:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        class UserStatus:
            ACTIVE = "active"

    user = None
    try:
        user = User(
            email="test@example.com",
            name="Test User",
            api_key_hash="testhash",
            personal_quota=1000.0,
            used_tokens=0.0,
            status=UserStatus.ACTIVE,
        )
        session.add(user)
        session.commit()
    except Exception:
        # best-effort for repos that don't have models importable
        pass
    return user


@pytest.fixture(scope="function")
def test_team(session):
    try:
        from app.models import Team
    except Exception:

        class Team:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

    team = None
    try:
        team = Team(
            name="Test Team", vacation_share_percentage=10.0, common_pool=1000.0, used_pool=0.0
        )
        session.add(team)
        session.commit()
    except Exception:
        pass
    return team


@pytest.fixture(scope="function")
def admin_api_key(session):
    """Create an admin user and return an auth header dict if possible."""
    try:
        from app.logic import AuthManager
        from app.models import User

        api_key, api_key_hash = AuthManager.generate_api_key()
        admin = User(
            email="admin@example.com", name="Admin", api_key_hash=api_key_hash, is_admin=True
        )
        session.add(admin)
        session.commit()
        return {"Authorization": f"Bearer {api_key}"}
    except Exception:
        return {"Authorization": "Bearer mock-admin-api-key"}


def _load_file_credentials():
    try:
        # tests/fixtures/credentials.py may be generated during CI runs
        from tests.fixtures import credentials as creds_mod  # type: ignore

        creds = getattr(creds_mod, "CREDENTIALS", {})
        if isinstance(creds, dict):
            return creds
    except Exception:
        return {}


def _load_env_credentials(keys=None):
    keys = keys or [
        "TEST_ADMIN_PASSWORD",
        "TEST_PASSWORD",
        "TEST_API_KEY",
        "ADMIN_PASSWORD",
        "API_KEY",
    ]
    out = {}
    for k in keys:
        v = os.getenv(k)
        if v:
            out[k] = v
    return out


@pytest.fixture(scope="session")
def test_credentials():
    """Return a dict of credentials for tests.

    Priority: generated `tests/fixtures/credentials.py` -> environment variables
    """
    creds = {}
    creds.update(_load_file_credentials())
    creds.update(_load_env_credentials())
    if not creds:
        logger.warning("No test credentials found in environment or generated fixtures.")
    return creds
