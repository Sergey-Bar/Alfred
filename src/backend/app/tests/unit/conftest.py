"""
Pytest configuration and fixtures for Alfred backend unit tests.

This file loads all fixtures from the main QA Backend conftest.py to enable test discovery and fixture reuse.
"""

import importlib.util
import sys
from pathlib import Path
import warnings
import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database import Base
from app.models import User, UserStatus

# Correct path to dev/QA/Backend/conftest.py
qa_backend_conftest = (
    Path(__file__).parent.parent.parent.parent.parent.parent
    / "dev"
    / "QA"
    / "Backend"
    / "conftest.py"
)

if qa_backend_conftest.exists():
    spec = importlib.util.spec_from_file_location("qa_backend_conftest", str(qa_backend_conftest))
    qa_backend = importlib.util.module_from_spec(spec)
    sys.modules["qa_backend_conftest"] = qa_backend
    spec.loader.exec_module(qa_backend)

    globals().update({k: v for k, v in qa_backend.__dict__.items() if not k.startswith("__")})
else:
    warnings.warn(f"QA Backend conftest.py not found at {qa_backend_conftest}. Some fixtures may be unavailable.")

@pytest.fixture
def test_client():
    """Fixture for creating a FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def admin_api_key():
    """Fixture for providing a mock admin API key."""
    return "mock-admin-api-key"

@pytest.fixture(scope="function")
def session():
    """Fixture for creating a database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(session):
    """Fixture for creating a mock user."""
    user = User(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test_user@example.com",
        name="Test User",
        personal_quota=1000.0,
        used_tokens=100.0,
        status=UserStatus.ACTIVE,
    )
    session.add(user)
    session.commit()
    return user
