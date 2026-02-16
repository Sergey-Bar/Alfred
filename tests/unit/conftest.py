import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

"""
Pytest configuration for top-level unit tests.
Ensures 'app' module is importable by patching sys.path to include backend/.
Provides fixtures for database session, test_user, and test_team.
"""

import pytest
from app.models import Team, User, UserStatus
from sqlmodel import Session, SQLModel, create_engine

# In-memory SQLite for fast, isolated tests using SQLModel
engine = create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def session():
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as db:
        yield db
    SQLModel.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(session):
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
    return user


@pytest.fixture(scope="function")
def test_team(session):

    team = Team(name="Test Team", vacation_share_percentage=10.0, common_pool=1000.0, used_pool=0.0)
    session.add(team)
    session.commit()
    return team
