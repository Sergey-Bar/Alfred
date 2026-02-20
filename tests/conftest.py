"""Top-level conftest that exposes shared fixtures.

This file loads `tests/fixtures/shared_fixtures.py` by path and injects
its public symbols into the conftest module namespace so pytest can
discover fixtures without requiring `tests` to be an importable package.
"""

# Ensure test DB env is set before importing or loading fixtures so engines point to same DB
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

# Create a file-backed test DB and set env vars before loading fixtures
_tmp_dir = Path(".pytest_tmp")
_tmp_dir.mkdir(exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir / 'test.db'}")
os.environ.setdefault("ENVIRONMENT", "test")

#           the engine used by pytest fixtures, causing "no such table" errors.
#          import the app.
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool

# Build an engine compatible with SQLite file-backed tests and cross-thread use
TEST_DB = os.environ["DATABASE_URL"]
engine = create_engine(
	TEST_DB,
	connect_args={"check_same_thread": False},
	poolclass=StaticPool,
)

# Inject engine into the application's database module so app/TestClient use same DB
try:
	from src.backend.app import database as app_db

	app_db.set_engine(engine)
	# Ensure schema exists on the injected engine
	SQLModel.metadata.create_all(app_db.get_engine())
except Exception:
	# If the app database module isn't importable yet, continue; shared fixtures
	# will also create tables when necessary.
	pass

# Ensure application package import works (so tests can `import app`)
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src" / "backend"))

# Load shared_fixtures.py by path and inject public symbols into this module
shared_path = Path(__file__).parent / "fixtures" / "shared_fixtures.py"
spec = importlib.util.spec_from_file_location("tests.shared_fixtures", str(shared_path))
shared = importlib.util.module_from_spec(spec)
assert spec and spec.loader is not None
spec.loader.exec_module(shared)

# Export public names (except private/dunder)
for name, val in vars(shared).items():
	if not name.startswith("_"):
		globals()[name] = val
