import sys
from pathlib import Path

# Ensure `src/backend` is importable before importing app modules
p = Path(__file__).resolve()
root = p
# Climb parents until we find repository root (pyproject.toml) or src/backend
while root.parent != root:
    if (root / "pyproject.toml").exists() or (root / "src" / "backend").exists():
        break
    root = root.parent

src_backend_dir = root / "src" / "backend"
if not src_backend_dir.exists():
    # Fallback: repository layout in this workspace places repo root four levels up
    try:
        root = Path(__file__).resolve().parents[4]
        src_backend_dir = root / "src" / "backend"
    except Exception:
        pass
if not src_backend_dir.exists():
    # Try a set of likely candidates (cwd, common parent depths, and known workspace path)
    candidates = [
        Path.cwd(),
        Path(__file__).resolve().parents[4],
        Path(__file__).resolve().parents[5],
        Path("C:/Projects/Alfred"),
    ]
    for c in candidates:
        candidate_src = c / "src" / "backend"
        if candidate_src.exists():
            src_backend_dir = candidate_src
            break

if src_backend_dir.exists() and str(src_backend_dir) not in sys.path:
    sys.path.insert(0, str(src_backend_dir))

# Ensure repository root is on sys.path so `tests` package imports work
try:
    repo_root = root
    if repo_root.exists() and str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
except Exception:
    pass

# Final fallback: ensure known workspace root is on sys.path (developer machine path)
workspace_fallback = Path("C:/Projects/Alfred")
if workspace_fallback.exists() and str(workspace_fallback) not in sys.path:
    sys.path.insert(0, str(workspace_fallback))

# Ensure tests run against a stable test DB and set before any app imports
try:
    import os

    _tmp_dir = Path(".pytest_tmp")
    _tmp_dir.mkdir(exist_ok=True)
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir / 'unit_test.db'}")
    os.environ.setdefault("ENVIRONMENT", "test")
except Exception:
    pass

# [AI GENERATED]
# Model: GitHub Copilot (GPT-5 mini)
# Logic: Create and inject a reusable test Engine into the application so TestClient and fixtures share the same DB.
# Why: Prevent "no such table" errors due to import-time engine creation on a different DB.
# Root Cause: Some tests import app modules before fixtures set DATABASE_URL; injecting the Engine ensures a single engine instance.
# Context: This must be executed before any `import app` or TestClient creation in tests.
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from importlib import import_module

TEST_DB = os.environ.get("DATABASE_URL")
try:
    engine = create_engine(
        TEST_DB,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Attempt to inject into app.database if available
    try:
        _app_db = import_module("app.database")
        try:
            _app_db.set_engine(engine)
        except Exception:
            _app_db.engine = engine
        try:
            _app_db._tables_created = False
        except Exception:
            pass
        try:
            SQLModel.metadata.create_all(_app_db.get_engine())
        except Exception:
            pass
    except Exception:
        # app not importable yet; it's fine, adapters will attempt again
        pass
except Exception:
    pass

import logging

# Fallback lightweight logging for tests (avoid importing app logging before path is ready)
logging.basicConfig(level=logging.DEBUG)

# Re-export shared fixtures for consistency
from tests.fixtures.shared_fixtures import *  # noqa: F401,F403
