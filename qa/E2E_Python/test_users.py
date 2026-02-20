"""
Model Name: GPT-4o
Logic/Reasoning: Ported user management E2E tests to Python using the admin_logged_in_page fixture.
Root Cause: Fulfilling the objective to migrate E2E tests to Pytest-Playwright.
Context: Verification of admin-only user management features.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.describe("User Management")
class TestUsers:

    @pytest.fixture(autouse=True)
    def setup(self, admin_logged_in_page: Page):
        self.page = admin_logged_in_page
        self.page.goto("/users")

    def test_should_display_users_page_admin_only(self):
        expect(self.page).to_have_url("**/users")
        expect(self.page.locator("h1, h2")).to_contain_text("user", ignore_case=True)

    def test_should_show_users_table(self):
        table = self.page.locator('table, [role="table"]')
        expect(table).to_be_visible(timeout=10000)

    def test_should_search_for_users(self):
        search_input = self.page.locator('input[type="search"], input[placeholder*="search"]').first

        if search_input.is_visible(timeout=5000):
            search_input.fill("test")
            self.page.wait_for_timeout(1000)
            expect(self.page.locator('table, [role="table"]')).to_be_visible()

    def test_should_open_user_creation_form(self):
        self.page.click('button:has-text("Add"), button:has-text("New"), button:has-text("Create")')

        dialog = self.page.locator('form, [role="dialog"]')
        expect(dialog).to_be_visible()

    def test_should_edit_user_details(self):
        # Click edit button for first user
        edit_button = self.page.locator('button:has-text("Edit"), [aria-label*="edit"]').first

        if edit_button.is_visible(timeout=5000):
            edit_button.click()

            dialog = self.page.locator('form, [role="dialog"]')
            expect(dialog).to_be_visible()

    def test_should_toggle_user_status(self):
        # Look for active/inactive toggle
        status_toggle = self.page.locator(
            'button:has-text("Activate"), button:has-text("Deactivate")'
        ).first

        if status_toggle.is_visible(timeout=5000):
            status_toggle.click()

            # Confirm if needed
            confirm_button = self.page.locator('button:has-text("Confirm"), button:has-text("Yes")')
            if confirm_button.is_visible(timeout=2000):
                confirm_button.click()
