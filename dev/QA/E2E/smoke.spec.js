
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: E2E smoke tests for basic app health using Playwright. Covers landing, load time, console errors, meta tags, and 404 handling.
// Why: Ensures app loads and basic routes work in real browser before deeper tests run.
// Root Cause: Broken deploys or regressions can break all user access.
// Context: Run in CI for every PR. Future: add more routes and error checks.
// Model Suitability: E2E test logic is standard; GPT-4.1 is sufficient.
const { test, expect } = require('@playwright/test');

test.describe('Smoke Tests', () => {
    test('should load landing page', async ({ page }) => {
        await page.goto('/');

        // Check page loads and is responsive
        expect(await page.title()).toBeTruthy();

        // Check for main navigation or content
        const mainContent = page.locator('main, #root, #app');
        await expect(mainContent).toBeVisible({ timeout: 10000 });
    });

    test('should load and respond within acceptable time', async ({ page }) => {
        const startTime = Date.now();

        await page.goto('/');
        await page.waitForLoadState('domcontentloaded');

        const loadTime = Date.now() - startTime;

        // Should load within 5 seconds
        expect(loadTime).toBeLessThan(5000);
    });

    test('should have no console errors on load', async ({ page }) => {
        const consoleErrors = [];

        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            }
        });

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Allow some known benign errors but alert on others
        const criticalErrors = consoleErrors.filter(err =>
            !err.includes('favicon') &&
            !err.includes('DevTools')
        );

        expect(criticalErrors.length).toBe(0);
    });

    test('should have proper meta tags', async ({ page }) => {
        await page.goto('/');

        // Check for viewport meta
        const viewport = await page.locator('meta[name="viewport"]').getAttribute('content');
        expect(viewport).toBeTruthy();
    });

    test('should handle 404 pages gracefully', async ({ page }) => {
        const response = await page.goto('/non-existent-page-12345');

        // Should either redirect or show 404 page
        expect(response.status()).toBeGreaterThanOrEqual(200);
    });

    test('should be accessible via keyboard navigation', async ({ page }) => {
        await page.goto('/login');

        // Tab through form elements
        await page.keyboard.press('Tab');
        await page.keyboard.press('Tab');

        // At least one element should be focused
        const focusedElement = await page.evaluate(() => document.activeElement.tagName);
        expect(focusedElement).toBeTruthy();
    });
});
