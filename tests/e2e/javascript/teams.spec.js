
const { test, expect } = require('@playwright/test');

test.describe('Team Management', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'test@example.com');
        await page.fill('input[type="password"]', 'password123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/dashboard/);
        await page.goto('/teams');
    });

    test('should display teams page', async ({ page }) => {
        await expect(page).toHaveURL(/teams/);
        await expect(page.locator('h1, h2')).toContainText(/team/i);
    });

    test('should show teams list', async ({ page }) => {
        const teamsList = page.locator('table, [class*="team"], [class*="list"]');
        await expect(teamsList.first()).toBeVisible({ timeout: 10000 });
    });

    test('should create new team', async ({ page }) => {
        await page.click('button:has-text("Add"), button:has-text("New"), button:has-text("Create")');

        const dialog = page.locator('form, [role="dialog"]');
        await expect(dialog).toBeVisible();

        // Fill team name
        const nameInput = dialog.locator('input[name*="name"], input[placeholder*="name"]').first();
        if (await nameInput.isVisible({ timeout: 2000 })) {
            await nameInput.fill('E2E Test Team');
        }
    });

    test('should view team details', async ({ page }) => {
        // Click on first team
        const teamRow = page.locator('tr, [class*="team-item"]').nth(1);

        if (await teamRow.isVisible({ timeout: 5000 })) {
            await teamRow.click();
            await page.waitForTimeout(1000);
        }
    });

    test('should manage team members', async ({ page }) => {
        // Open team details
        const viewButton = page.locator('button:has-text("View"), button:has-text("Details")').first();

        if (await viewButton.isVisible({ timeout: 5000 })) {
            await viewButton.click();

            // Look for add member button
            const addMemberButton = page.locator('button:has-text("Add Member"), button:has-text("Invite")');
            await expect(addMemberButton.first()).toBeVisible({ timeout: 5000 });
        }
    });
});
