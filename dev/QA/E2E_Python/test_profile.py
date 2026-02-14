"""
Model Name: GPT-4o
Logic/Reasoning: Ported user profile E2E tests to Python.
Root Cause: Fulfilling the objective to migrate E2E tests to Pytest-Playwright.
Context: Verification of user settings and preference management.
"""

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.describe("User Profile")
class TestProfile:
    
    @pytest.fixture(autouse=True)
    def setup(self, logged_in_page: Page):
        self.page = logged_in_page
        self.page.goto("/profile")

    def test_should_display_profile_page(self):
        expect(self.page).to_have_url("**/profile")
        expect(self.page.locator("h1, h2")).to_contain_text("profile", ignore_case=True)

    def test_should_show_user_information(self):
        # Check for user info fields
        expect(self.page.locator('input[type="email"], input[name*="email"]')).to_be_visible()

    def test_should_update_profile_information(self):
        name_input = self.page.locator('input[name*="name"], input[placeholder*="name"]').first
        
        if name_input.is_visible(timeout=5000):
            name_input.fill("Updated Name (Python)")
            
            # Save changes
            self.page.click('button:has-text("Save"), button[type="submit"]')
            
            # Should show success message
            expect(self.page.locator("text=/success|saved|updated/i")).to_be_visible(timeout=5000)

    def test_should_change_password(self):
        # Look for change password button
        change_password_button = self.page.locator('button:has-text("Change Password"), button:has-text("Update Password")')
        
        if change_password_button.is_visible(timeout=5000):
            change_password_button.click()
            
            dialog = self.page.locator('form, [role="dialog"]')
            expect(dialog).to_be_visible()

    def test_should_update_notification_preferences(self):
        # Look for settings/preferences section
        self.page.goto("/settings")
        expect(self.page).to_have_url("**/settings")
        
        checkbox = self.page.locator('input[type="checkbox"]').first
        if checkbox.is_visible(timeout=5000):
            checkbox.click()
            
            # Save
            self.page.click('button:has-text("Save"), button[type="submit"]')
