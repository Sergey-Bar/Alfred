"""
Pytest configuration and fixtures for TokenPool tests.
"""

import os
import pytest
from decimal import Decimal
from sqlmodel import Session, SQLModel, create_engine

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite:///./test_tokenpool.db"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    # Cleanup
    SQLModel.metadata.drop_all(engine)
    if os.path.exists("./test_tokenpool.db"):
        os.remove("./test_tokenpool.db")


@pytest.fixture
def session(engine):
    """Create test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_user(session):
    """Create a test user."""
    from app.models import User
    from app.logic import AuthManager
    
    _, api_key_hash = AuthManager.generate_api_key()
    
    user = User(
        email="test@example.com",
        name="Test User",
        api_key_hash=api_key_hash,
        personal_quota=Decimal("1000.00"),
        used_tokens=Decimal("0.00")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_team(session):
    """Create a test team."""
    from app.models import Team
    
    team = Team(
        name="Test Team",
        description="A test team",
        common_pool=Decimal("10000.00"),
        used_pool=Decimal("0.00")
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    # Override database for tests
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    
    with TestClient(app) as client:
        yield client
