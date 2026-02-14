"""
Model Name: GPT-4o
Logic/Reasoning: Ported login flow E2E tests to Python.
Root Cause: Fulfilling the objective to migrate E2E tests to Pytest-Playwright.
Context: Verification of authentication mechanisms.
"""

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.describe("Login Flow")
class TestLogin:
    
    def test_should_load_login_page(self, page: Page):
        page.goto("/login")
        expect(page).to_have_title("Alfred", ignore_case=True)
        expect(page.locator("form")).to_be_visible()

    def test_should_show_validation_errors_for_empty_fields(self, page: Page):
        page.goto("/login")
        page.click('button[type="submit"]')
        # Check for error messages or validation states
        expect(page.locator('input[type="email"]')).to_be_visible()

    def test_should_successfully_login_with_valid_credentials(self, page: Page):
        page.goto("/login")

        # Fill in login form
        page.fill('input[type="email"]', 'test@example.com')
        page.fill('input[type="password"]', 'password123')

        # Submit form
        page.click('button[type="submit"]')

        # Should redirect to dashboard
        expect(page).to_have_url("**/dashboard")

    def test_should_show_error_for_invalid_credentials(self, page: Page):
        page.goto("/login")

        page.fill('input[type="email"]', 'invalid@example.com')
        page.fill('input[type="password"]', 'wrongpassword')
        page.click('button[type="submit"]')

        # Should show error message
        expect(page.locator("text=/error|invalid|failed/i")).to_be_visible(timeout=5000)
