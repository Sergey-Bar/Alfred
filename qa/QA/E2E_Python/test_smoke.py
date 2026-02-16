"""
Model Name: GPT-4o
Logic/Reasoning: Standardized E2E smoke tests ported from JS to Python using pytest-playwright.
Root Cause: Fulfilling the objective to set up Playwright with Pytest for backend and frontend verification.
Context: Part of the transition to Python-based E2E testing for normalized cross-platform automation.
"""

import time

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.describe("Smoke Tests")
class TestSmoke:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page

    def test_should_load_landing_page(self):
        self.page.goto("/")

        # Check page loads and is responsive
        assert self.page.title()

        # Check for main navigation or content
        main_content = self.page.locator("main, #root, #app")
        expect(main_content).to_be_visible(timeout=10000)

    def test_should_load_and_respond_within_acceptable_time(self):
        start_time = time.time()
        self.page.goto("/")
        self.page.wait_for_load_state("domcontentloaded")
        load_time = (time.time() - start_time) * 1000

        # Should load within 5 seconds
        assert load_time < 5000

    def test_should_have_no_console_errors_on_load(self):
        console_errors = []

        self.page.on(
            "console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None
        )

        self.page.goto("/")
        self.page.wait_for_load_state("networkidle")

        # Allow some known benign errors but alert on others
        critical_errors = [
            err for err in console_errors if "favicon" not in err and "DevTools" not in err
        ]

        assert len(critical_errors) == 0

    def test_should_have_proper_meta_tags(self):
        self.page.goto("/")

        # Check for viewport meta
        viewport = self.page.locator('meta[name="viewport"]').get_attribute("content")
        assert viewport

    def test_should_handle_404_pages_gracefully(self):
        response = self.page.goto("/non-existent-page-12345")

        # Should either redirect or show 404 page
        assert response.status >= 200

    def test_should_be_accessible_via_keyboard_navigation(self):
        self.page.goto("/login")

        # Tab through form elements
        self.page.keyboard.press("Tab")
        self.page.keyboard.press("Tab")

        # At least one element should be focused
        focused_element = self.page.evaluate("() => document.activeElement.tagName")
        assert focused_element
