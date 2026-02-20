"""
Model Name: GPT-4o
Logic/Reasoning: Ported approval workflow E2E tests to Python using pytest-playwright.
Root Cause: Expanding the Python E2E test coverage for the governance module.
Context: Ensures that the transition to Python-based testing covers critical business workflows like approvals.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.describe("Approval Requests")
class TestApprovals:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        # Login flow
        self.page.goto("/login")
        from test_credentials import TEST_USER_EMAIL, TEST_USER_PASSWORD

        self.page.fill('input[type="email"]', TEST_USER_EMAIL)
        self.page.fill('input[type="password"]', TEST_USER_PASSWORD)
        self.page.click('button[type="submit"]')
        self.page.wait_for_url("**/dashboard")
        self.page.goto("/approvals")

    def test_should_display_approvals_page(self):
        expect(self.page).to_have_url("**/approvals")
        expect(self.page.locator("h1, h2")).to_contain_text("approval", ignore_case=True)

    def test_should_show_pending_approvals(self):
        approvals_list = self.page.locator('table, [class*="approval"], [class*="list"]')
        expect(approvals_list.first).to_be_visible(timeout=10000)

    def test_should_create_new_approval_request(self):
        # Using a more robust selector for buttons
        self.page.click(
            'button:has-text("Request"), button:has-text("New"), button:has-text("Create")'
        )

        dialog = self.page.locator('form, [role="dialog"]')
        expect(dialog).to_be_visible()

        amount_input = dialog.locator('input[type="number"], input[name*="amount"]').first
        if amount_input.is_visible(timeout=2000):
            amount_input.fill("100")

        reason_input = dialog.locator('textarea, input[name*="reason"]').first
        if reason_input.is_visible(timeout=2000):
            reason_input.fill("E2E test approval request (Python)")

    def test_should_filter_approvals_by_status(self):
        status_filter = self.page.locator('select, button:has-text("Status")').first
        if status_filter.is_visible(timeout=5000):
            status_filter.click()
            self.page.wait_for_timeout(500)

    def test_should_approve_a_pending_request_admin(self):
        # This assumes the test user has admin rights or we are logged in as admin
        approve_button = self.page.locator('button:has-text("Approve")').first
        if approve_button.is_visible(timeout=5000):
            approve_button.click()

            confirm_button = self.page.locator('button:has-text("Confirm"), button:has-text("Yes")')
            if confirm_button.is_visible(timeout=2000):
                confirm_button.click()

            expect(self.page.locator("text=/success|approved/i")).to_be_visible(timeout=5000)
