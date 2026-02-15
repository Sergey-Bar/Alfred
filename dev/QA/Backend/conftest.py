"""
Pytest configuration and fixtures for Alfred tests.
"""

import sys
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Add backend directory to Python path so 'app' module can be imported
src_backend_dir = Path(__file__).parent.parent.parent / "src" / "backend"
print(f"[DEBUG] src_backend_dir: {src_backend_dir}")
sys.path.insert(0, str(src_backend_dir))
print(f"[DEBUG] sys.path: {sys.path}")

# Use SQLite in-memory for tests (truly in-memory - no file)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def engine():
    """Create test database engine - fresh for each test function."""
    # Use StaticPool to ensure the same in-memory database is shared across connections
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Critical: ensures single shared in-memory db
    )
    # Import models to register them with SQLModel metadata
    from app import models  # noqa: F401
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """Create test database session with transaction rollback."""
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def test_user(session):
    """Create a test user."""
    from app.logic import AuthManager
    from app.models import User

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
def admin_api_key(session):
    """Create an admin user and return auth headers for tests."""
    from decimal import Decimal

    from app.logic import AuthManager
    from app.models import User

    api_key, api_key_hash = AuthManager.generate_api_key()

    admin = User(
        email="admin@example.com",
        name="Admin",
        api_key_hash=api_key_hash,
        is_admin=True,
        personal_quota=Decimal("10000.00")
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return {"Authorization": f"Bearer {api_key}"}


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


@pytest.fixture(scope="function")
def test_client(engine, monkeypatch):
    """Create FastAPI test client with isolated database."""
    import app.main as main_module
    from fastapi.testclient import TestClient
    from sqlmodel import Session

    # Store original engine
    original_engine = main_module.engine

    # Patch the engine in main module BEFORE starting the app
    main_module.engine = engine

    # Override the session dependency to use our test engine
    def get_test_session():
        with Session(engine) as session:
            yield session

    main_module.app.dependency_overrides[main_module.get_session] = get_test_session
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("ENVIRONMENT", "test")

    with TestClient(main_module.app) as client:
        yield client

    # Cleanup
    main_module.app.dependency_overrides.clear()
    main_module.engine = original_engine
