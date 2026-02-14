"""
Model Name: GPT-4o
Logic/Reasoning: Ported dashboard E2E tests to Python using the logged_in_page fixture.
Root Cause: Fulfilling the objective to migrate E2E tests to Pytest-Playwright.
Context: Verification of dashboard layout and navigation.
"""

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.describe("Dashboard")
class TestDashboard:
    
    def test_should_display_dashboard_with_main_components(self, logged_in_page: Page):
        expect(logged_in_page.locator("nav")).to_be_visible()
        expect(logged_in_page.locator("main")).to_be_visible()

    def test_should_show_user_stats_and_metrics(self, logged_in_page: Page):
        # Check for dashboard cards/stats
        stats_cards = logged_in_page.locator('[class*="stat"], [class*="card"], [class*="metric"]')
        expect(stats_cards.first).to_be_visible(timeout=10000)

    def test_should_navigate_to_different_sections(self, logged_in_page: Page):
        # Test navigation to transfers
        logged_in_page.click('a[href*="transfers"], nav >> text=/transfers/i')
        expect(logged_in_page).to_have_url("**/transfers")

        # Test navigation to approvals
        logged_in_page.click('a[href*="approvals"], nav >> text=/approvals/i')
        expect(logged_in_page).to_have_url("**/approvals")

    def test_should_display_activity_log(self, logged_in_page: Page):
        # Look for activity log component
        activity_log = logged_in_page.locator('[class*="activity"], [class*="log"]').first
        expect(activity_log).to_be_visible(timeout=10000)
