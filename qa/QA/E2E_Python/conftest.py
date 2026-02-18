"""
Model Name: GPT-4o
Logic/Reasoning: Configuration for pytest-playwright E2E tests.
Root Cause: Setting up base URL and common fixtures for Python E2E tests.
Context: Required to point Playwright to the local frontend and backend services.
"""

import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

# Ensure test DB env is set early so app imports use the test DB when E2E starts
try:
    import os

    _tmp_dir = Path(".pytest_tmp")
    _tmp_dir.mkdir(exist_ok=True)
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir / 'e2e_test.db'}")
    os.environ.setdefault("ENVIRONMENT", "test")
except Exception:
    pass

# Ensure repo root and `src/backend` are importable so shared fixtures resolve
root = Path(__file__).resolve()
while root.parent != root:
    if (root / "pyproject.toml").exists() or (root / "src" / "backend").exists():
        break
    root = root.parent
repo_root = root
src_backend = repo_root / "src" / "backend"
if src_backend.exists() and str(src_backend) not in sys.path:
    sys.path.insert(0, str(src_backend))
if repo_root.exists() and str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import shared fixtures so `test_credentials` is available to E2E tests
try:
    from tests.fixtures.shared_fixtures import test_credentials  # type: ignore
except Exception:
    # best-effort; E2E may run in different CI environment
    test_credentials = {}

# [AI GENERATED]
# Model: GitHub Copilot (GPT-5 mini)
# Logic: Create and inject a reusable test Engine into the application so E2E tests and the app share the same DB.
# Why: Prevent mismatches where the app starts against a different DB than tests expect.
# Root Cause: App may create an engine at import-time using environment vars; ensure a single injected Engine is used.
# Context: E2E test runs may start the app or expect it to be running; this helps when tests import app modules.
try:
    from sqlmodel import SQLModel, create_engine
    from sqlalchemy.pool import StaticPool
    from importlib import import_module

    TEST_DB = os.environ.get("DATABASE_URL")
    e_engine = create_engine(
        TEST_DB,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        _app_db = import_module("app.database")
        try:
            _app_db.set_engine(e_engine)
        except Exception:
            _app_db.engine = e_engine
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
    # If the application provides a factory, create a test app wired to the
    # injected engine so any helpers that import `app.main` can access a
    # configured app instance without triggering a separate engine creation.
    try:
        app_main = import_module("app.main")
        if hasattr(app_main, "create_app"):
            try:
                # Create but do not start the app; expose as module var for tests
                _e2e_app = app_main.create_app(engine=e_engine)
            except Exception:
                pass
    except Exception:
        pass
except Exception:
    pass


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, base_url):
    """Override browser context args to include base URL if needed."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }


def pytest_configure(config):
    """Set default base URL if not provided via command line."""
    if not config.getoption("--base-url"):
        config.option.base_url = "http://localhost:5173"


@pytest.fixture
def logged_in_page(page: Page, test_credentials):
    """Fixture that logs in the user and returns the page."""
    TEST_USER_EMAIL = test_credentials.get("TEST_USER_EMAIL", "test_user@example.com")
    TEST_USER_PASSWORD = test_credentials.get("TEST_USER_PASSWORD", "password")
    page.goto("/login")
    page.fill('input[type="email"]', TEST_USER_EMAIL)
    page.fill('input[type="password"]', TEST_USER_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard")
    return page


@pytest.fixture
def admin_logged_in_page(page: Page, test_credentials):
    """Fixture that logs in as admin and returns the page."""
    ADMIN_EMAIL = test_credentials.get("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = test_credentials.get("ADMIN_PASSWORD", "adminpass")
    page.goto("/login")
    page.fill('input[type="email"]', ADMIN_EMAIL)
    page.fill('input[type="password"]', ADMIN_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard")
    return page
