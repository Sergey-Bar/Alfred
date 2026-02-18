"""Adapter conftest that re-exports shared fixtures for core unit tests."""

import os
import sys
from pathlib import Path

# Ensure repository root on sys.path for imports
repo_root = Path(__file__).resolve().parents[5]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Set test DB early so shared fixtures and app use same DB when imported
_tmp_dir = Path(repo_root) / ".pytest_tmp"
_tmp_dir.mkdir(exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir / 'test.db'}")
os.environ.setdefault("ENVIRONMENT", "test")

from tests.fixtures.shared_fixtures import *  # noqa: F401,F403
