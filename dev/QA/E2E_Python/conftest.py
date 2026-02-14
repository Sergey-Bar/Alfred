"""
Model Name: GPT-4o
Logic/Reasoning: Configuration for pytest-playwright E2E tests.
Root Cause: Setting up base URL and common fixtures for Python E2E tests.
Context: Required to point Playwright to the local frontend and backend services.
"""

import pytest
from playwright.sync_api import Page

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
def logged_in_page(page: Page):
    """Fixture that logs in the user and returns the page."""
    page.goto("/login")
    page.fill('input[type="email"]', "test@example.com")
    page.fill('input[type="password"]', "password123")
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard")
    return page

@pytest.fixture
def admin_logged_in_page(page: Page):
    """Fixture that logs in as admin and returns the page."""
    page.goto("/login")
    page.fill('input[type="email"]', "admin@example.com")
    page.fill('input[type="password"]', "admin123")
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard")
    return page
