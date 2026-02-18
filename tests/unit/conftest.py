"""Adapter conftest for top-level unit tests that re-exports shared fixtures."""

import sys
from pathlib import Path

# ensure repo root on path for imports
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tests.fixtures.shared_fixtures import *  # noqa: F401,F403
