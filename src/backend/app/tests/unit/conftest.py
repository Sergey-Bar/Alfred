"""Adapter conftest for backend unit tests.

This file re-exports shared fixtures from `tests.fixtures.shared_fixtures` and
keeps a small set of adapter helpers for local test runs.
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure repository root is on sys.path so `tests.fixtures` is importable
repo_root = Path(__file__).resolve().parents[5]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Ensure test DB env is set before importing `app` so the app's engine points at test DB
_tmp_dir = Path(repo_root) / ".pytest_tmp"
_tmp_dir.mkdir(exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir / 'test.db'}")
os.environ.setdefault("ENVIRONMENT", "test")

from app.main import app
from fastapi.testclient import TestClient

from tests.fixtures.shared_fixtures import *  # noqa: F401,F403


@pytest.fixture
def test_client():
    """Simple TestClient fixture for unit tests that don't need DB overrides."""
    return TestClient(app)
