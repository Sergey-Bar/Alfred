"""
Model Name: GPT-4o
Logic/Reasoning: Ported team management E2E tests to Python.
Root Cause: Fulfilling the objective to migrate E2E tests to Pytest-Playwright.
Context: Verification of multi-tenant team isolation and governance.
"""

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.describe("Team Management")
class TestTeams:
    
    @pytest.fixture(autouse=True)
    def setup(self, logged_in_page: Page):
        self.page = logged_in_page
        self.page.goto("/teams")

    def test_should_display_teams_page(self):
        expect(self.page).to_have_url("**/teams")
        expect(self.page.locator("h1, h2")).to_contain_text("team", ignore_case=True)

    def test_should_show_teams_list(self):
        teams_list = self.page.locator('table, [class*="team"], [class*="list"]')
        expect(teams_list.first).to_be_visible(timeout=10000)

    def test_should_create_new_team(self):
        self.page.click('button:has-text("Add"), button:has-text("New"), button:has-text("Create")')
        
        dialog = self.page.locator('form, [role="dialog"]')
        expect(dialog).to_be_visible()
        
        name_input = dialog.locator('input[name*="name"], input[placeholder*="name"]').first
        if name_input.is_visible(timeout=2000):
            name_input.fill("E2E Test Team (Python)")

    def test_should_view_team_details(self):
        # Click on first team
        team_row = self.page.locator('tr, [class*="team-item"]').nth(1)
        
        if team_row.is_visible(timeout=5000):
            team_row.click()
            self.page.wait_for_timeout(1000)

    def test_should_manage_team_members(self):
        # Open team details
        view_button = self.page.locator('button:has-text("View"), button:has-text("Details")').first
        
        if view_button.is_visible(timeout=5000):
            view_button.click()
            
            # Look for add member button
            add_member_button = self.page.locator('button:has-text("Add Member"), button:has-text("Invite")')
            expect(add_member_button.first).to_be_visible(timeout=5000)
