## [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Ensures src/backend is in sys.path for all test modules, so 'from app.*' works.
# Why: Fixes ModuleNotFoundError for 'app' in all test contexts.
# Root Cause: Pytest may not set sys.path to package root when running from outside src/backend.
# Context: This is safe and robust for monorepo and CI/CD.
# Model Suitability: Standard import fix; GPT-4.1 is sufficient.
from __future__ import annotations

import importlib.util
import logging
import os
import sys
from pathlib import Path

import pytest

# keep sys.path behavior so 'app' imports work in CI and local runs
src_backend_dir = Path(__file__).parent.parent.parent / "src" / "backend"
if src_backend_dir.exists():
    if str(src_backend_dir) not in sys.path:
        sys.path.insert(0, str(src_backend_dir))

logger = logging.getLogger(__name__)
logger.debug("sys.path: %s", sys.path)

# Use a shared fixtures module for core fixtures (load by path so `tests` need not be
# an importable package when running pytest from repo root).
# Locate repository root by finding the `tests` directory, then load shared_fixtures.py
repo_root = Path(__file__).resolve()
while repo_root and not (repo_root / "tests").exists():
    if repo_root.parent == repo_root:
        break
    repo_root = repo_root.parent
shared_path = repo_root / "tests" / "fixtures" / "shared_fixtures.py"
spec = importlib.util.spec_from_file_location("tests.shared_fixtures", str(shared_path))
shared = importlib.util.module_from_spec(spec)
assert spec and spec.loader is not None
spec.loader.exec_module(shared)

# Re-export shared fixtures so pytest discovers them (admin_api_key, test_user, etc.)
try:
    from tests.fixtures.shared_fixtures import *  # noqa: F401,F403
except Exception:
    # If import fails, keep using `shared` module references directly
    pass

# Use an in-memory DB URL; adapters can override via env
_tmp_dir = Path(".pytest_tmp")
_tmp_dir.mkdir(exist_ok=True)
# Use file-based SQLite for test isolation instead of shared in-memory
_test_unique_id = os.getpid()
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_tmp_dir / f'test_{_test_unique_id}.db'}")
# Ensure the application will pick up the test DB at import time
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture(scope="function")
def engine():
    """Adapter engine that avoids StaticPool connection issues.

    Uses a unique file-based SQLite DB per test to avoid detached connection
    errors with StaticPool. The file is cleaned up after the test.
    """
    import uuid
    from sqlalchemy.pool import NullPool
    
    # Use a unique file per test to avoid connection sharing issues
    unique_db = _tmp_dir / f"test_{uuid.uuid4().hex[:8]}.db"
    unique_db_url = f"sqlite:///{unique_db}"
    
    # Use NullPool to avoid connection caching issues
    from sqlmodel import create_engine
    engine = create_engine(
        unique_db_url,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )
    
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
        from sqlmodel import SQLModel

        # Prefer the public setter so the module's proxy is updated correctly
        try:
            _app_db.set_engine(engine)
        except Exception:
            # Fallback for older code paths that expect direct assignment
            _app_db.engine = engine

        # Reset create_all guard and ensure schema exists on the injected engine
        try:
            _app_db._tables_created = False
        except Exception:
            pass
        try:
            SQLModel.metadata.create_all(_app_db.get_engine())
        except Exception:
            pass
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
    
    # Clean up the unique DB file
    try:
        if unique_db.exists():
            unique_db.unlink()
    except Exception:
        pass


@pytest.fixture(scope="function")
def test_client(engine, monkeypatch):
    """Create FastAPI test client with isolated database (adapter-specific)."""
    import app.main as main_module
    # Also import dependencies module so we can override its get_session dependency
    try:
        import app.dependencies as app_dependencies
    except Exception:
        app_dependencies = None
    from fastapi.testclient import TestClient
    from sqlmodel import Session

    # Create an app instance wired to the test engine so all internals use it
    test_app = main_module.create_app(engine=engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    # Override session provider used by the app and by dependency modules
    try:
        test_app.dependency_overrides[main_module.get_session] = get_test_session
    except Exception:
        pass
    if app_dependencies is not None:
        try:
            test_app.dependency_overrides[app_dependencies.get_session] = get_test_session
        except Exception:
            pass
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("ENVIRONMENT", "test")

    # Ensure the application's engine has tables created for the test run
    try:
        import app.database as _app_db  # type: ignore
        from sqlmodel import SQLModel

        try:
            import app.models  # noqa: F401
        except Exception:
            pass
        # Ensure the app is using the same engine instance and create tables
        try:
            _app_db.set_engine(engine)
        except Exception:
            try:
                _app_db.engine = engine
            except Exception:
                pass
        SQLModel.metadata.create_all(_app_db.get_engine())
    except Exception:
        pass

    with TestClient(test_app) as client:
        yield client
    test_app.dependency_overrides.clear()
