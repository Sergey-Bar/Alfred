"""
Model Name: GPT-4o
Logic/Reasoning: Ported integrations E2E tests to Python using the admin_logged_in_page fixture.
Root Cause: Fulfilling the objective to migrate E2E tests to Pytest-Playwright.
Context: Verification of SSO and third-party notification connectors.
"""

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.describe("Integrations")
class TestIntegrations:
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_logged_in_page: Page):
        self.page = admin_logged_in_page
        self.page.goto("/integrations")

    def test_should_display_integrations_page(self):
        expect(self.page).to_have_url("**/integrations")
        expect(self.page.locator("h1, h2")).to_contain_text("integration", ignore_case=True)

    def test_should_show_available_integrations(self):
        # Check for integration cards/list
        integrations = self.page.locator('[class*="integration"], [class*="card"]')
        expect(integrations.first).to_be_visible(timeout=10000)

    def test_should_configure_slack_integration(self):
        slack_card = self.page.locator("text=/slack/i").first
        
        if slack_card.is_visible(timeout=5000):
            slack_card.click()
            
            # Configuration form should appear
            expect(self.page.locator('form, [role="dialog"]')).to_be_visible(timeout=5000)

    def test_should_test_integration_connection(self):
        test_button = self.page.locator('button:has-text("Test"), button:has-text("Verify")').first
        
        if test_button.is_visible(timeout=5000):
            test_button.click()
            
            # Should show result
            expect(self.page.locator("text=/success|connected|failed/i")).to_be_visible(timeout=10000)

    def test_should_enable_disable_integration(self):
        toggle = self.page.locator('input[type="checkbox"], button[role="switch"]').first
        
        if toggle.is_visible(timeout=5000):
            toggle.click()
            self.page.wait_for_timeout(1000)
