## [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Ensures src/backend is in sys.path for all test modules, so 'from app.*' works.
# Why: Fixes ModuleNotFoundError for 'app' in all test contexts.
# Root Cause: Pytest may not set sys.path to package root when running from outside src/backend.
# Context: This is safe and robust for monorepo and CI/CD.
# Model Suitability: Standard import fix; GPT-4.1 is sufficient.
import os
import sys
from pathlib import Path
import logging

import pytest

# keep sys.path behavior so 'app' imports work in CI and local runs
src_backend_dir = Path(__file__).parent.parent.parent / "src" / "backend"
if src_backend_dir.exists():
    if str(src_backend_dir) not in sys.path:
        sys.path.insert(0, str(src_backend_dir))

logger = logging.getLogger(__name__)
logger.debug("sys.path: %s", sys.path)

# Use a shared fixtures module for core fixtures
from tests.fixtures import shared_fixtures as shared  # noqa: E402

# Use an in-memory DB URL; adapters can override via env
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture(scope="function")
def engine():
    """Adapter engine that uses StaticPool to match previous behavior.

    This overrides the default `engine` fixture from `shared_fixtures`.
    """
    engine = shared.make_engine(TEST_DATABASE_URL, static_pool=True)
    # Import models to register metadata if available
    try:
        import app.models  # noqa: F401
    except Exception:
        pass

    # create metadata and patch app database engine if present
    try:
        SQLModel = shared.SQLModel
        SQLModel.metadata.create_all(engine)
    except Exception:
        pass

    try:
        import app.database as _app_db  # type: ignore

        _app_db.engine = engine
    except Exception:
        pass

    yield engine

    try:
        SQLModel = shared.SQLModel
        SQLModel.metadata.drop_all(engine)
    except Exception:
        pass
    try:
        engine.dispose()
    except Exception:
        pass


@pytest.fixture(scope="function")
def test_client(engine, monkeypatch):
    """Create FastAPI test client with isolated database (adapter-specific)."""
    import app.main as main_module
    from fastapi.testclient import TestClient
    from sqlmodel import Session

    original_engine = getattr(main_module, "engine", None)
    main_module.engine = engine

    def get_test_session():
        with Session(engine) as session:
            yield session

    main_module.app.dependency_overrides[main_module.get_session] = get_test_session
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("ENVIRONMENT", "test")

    with TestClient(main_module.app) as client:
        yield client

    main_module.app.dependency_overrides.clear()
    if original_engine is not None:
        main_module.engine = original_engine
