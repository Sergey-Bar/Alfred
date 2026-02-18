"""Adapter conftest that re-exports shared fixtures for core unit tests."""

import sys
from pathlib import Path

# Ensure repository root on sys.path for imports
repo_root = Path(__file__).resolve().parents[5]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tests.fixtures.shared_fixtures import *  # noqa: F401,F403
