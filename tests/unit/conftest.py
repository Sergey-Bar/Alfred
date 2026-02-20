"""Adapter conftest for top-level unit tests that re-exports shared fixtures."""

import os
import sys
from pathlib import Path

# Ensure test DB is configured before fixtures create engines
_tmp_dir = Path(".pytest_tmp")
_tmp_dir.mkdir(exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir / 'test.db'}")
os.environ.setdefault("ENVIRONMENT", "test")

# ensure repo root on path for imports
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tests.fixtures.shared_fixtures import *  # noqa: F401,F403
