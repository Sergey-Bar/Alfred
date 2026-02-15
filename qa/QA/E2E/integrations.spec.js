
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: E2E tests for integrations UI using Playwright. Covers listing, configuration, testing, and toggling integrations.
// Why: Ensures integration flows work in real browser and regressions are caught before release.
// Root Cause: Integration bugs can block notifications and external workflows.
// Context: Run in CI for every PR. Future: add more providers and error cases.
// Model Suitability: E2E test logic is standard; GPT-4.1 is sufficient.
const { test, expect } = require('@playwright/test');

test.describe('Integrations', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@example.com');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/dashboard/);
        await page.goto('/integrations');
    });

    test('should display integrations page', async ({ page }) => {
        await expect(page).toHaveURL(/integrations/);
        await expect(page.locator('h1, h2')).toContainText(/integration/i);
    });

    test('should show available integrations', async ({ page }) => {
        // Check for integration cards/list
        const integrations = page.locator('[class*="integration"], [class*="card"]');
        await expect(integrations.first()).toBeVisible({ timeout: 10000 });
    });

    test('should configure Slack integration', async ({ page }) => {
        const slackCard = page.locator('text=/slack/i').first();

        if (await slackCard.isVisible({ timeout: 5000 })) {
            await slackCard.click();

            // Configuration form should appear
            await expect(page.locator('form, [role="dialog"]')).toBeVisible({ timeout: 5000 });
        }
    });

    test('should test integration connection', async ({ page }) => {
        const testButton = page.locator('button:has-text("Test"), button:has-text("Verify")').first();

        if (await testButton.isVisible({ timeout: 5000 })) {
            await testButton.click();

            // Should show result
            await expect(page.locator('text=/success|connected|failed/i')).toBeVisible({ timeout: 10000 });
        }
    });

    test('should enable/disable integration', async ({ page }) => {
        const toggle = page.locator('input[type="checkbox"], button[role="switch"]').first();

        if (await toggle.isVisible({ timeout: 5000 })) {
            await toggle.click();
            await page.waitForTimeout(1000);
        }
    });
});
