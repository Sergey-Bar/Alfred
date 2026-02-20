
const { test, expect } = require('@playwright/test');

test.describe('Dashboard', () => {
    test.beforeEach(async ({ page }) => {
        // Login before each test
        await page.goto('/login');
        await page.fill('input[type="email"]', 'test@example.com');
        await page.fill('input[type="password"]', 'password123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/dashboard/);
    });

    test('should display dashboard with main components', async ({ page }) => {
        await expect(page.locator('nav')).toBeVisible();
        await expect(page.locator('main')).toBeVisible();
    });

    test('should show user stats and metrics', async ({ page }) => {
        // Check for dashboard cards/stats
        const statsCards = page.locator('[class*="stat"], [class*="card"], [class*="metric"]');
        await expect(statsCards.first()).toBeVisible({ timeout: 10000 });
    });

    test('should navigate to different sections', async ({ page }) => {
        // Test navigation
        await page.click('a[href*="transfers"], nav >> text=/transfers/i');
        await expect(page).toHaveURL(/transfers/);

        await page.click('a[href*="approvals"], nav >> text=/approvals/i');
        await expect(page).toHaveURL(/approvals/);
    });

    test('should display activity log', async ({ page }) => {
        // Look for activity log component
        const activityLog = page.locator('[class*="activity"], [class*="log"]').first();
        await expect(activityLog).toBeVisible({ timeout: 10000 });
    });
});
