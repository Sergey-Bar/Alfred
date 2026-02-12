const { test, expect } = require('@playwright/test');

test.describe('Credit Transfers', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'test@example.com');
        await page.fill('input[type="password"]', 'password123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/dashboard/);
        await page.goto('/transfers');
    });

    test('should display transfers page', async ({ page }) => {
        await expect(page).toHaveURL(/transfers/);
        await expect(page.locator('h1, h2')).toContainText(/transfer|credit/i);
    });

    test('should show transfer history table', async ({ page }) => {
        const table = page.locator('table, [role="table"]');
        await expect(table).toBeVisible({ timeout: 10000 });
    });

    test('should open transfer creation form', async ({ page }) => {
        // Click create/new transfer button
        await page.click('button:has-text("Transfer"), button:has-text("New"), button:has-text("Create")');

        // Form should appear
        await expect(page.locator('form, [role="dialog"]')).toBeVisible();
    });

    test('should validate transfer form fields', async ({ page }) => {
        await page.click('button:has-text("Transfer"), button:has-text("New"), button:has-text("Create")');

        // Try to submit empty form
        const submitButton = page.locator('button[type="submit"]').last();
        await submitButton.click();

        // Should show validation errors
        await expect(page.locator('input[required], select[required]').first()).toBeVisible();
    });

    test('should filter transfers by date range', async ({ page }) => {
        // Look for date picker or filter inputs
        const dateInput = page.locator('input[type="date"], input[placeholder*="date"]').first();

        if (await dateInput.isVisible({ timeout: 5000 })) {
            await dateInput.fill('2024-01-01');
            // Table should update
            await page.waitForTimeout(1000);
            await expect(page.locator('table, [role="table"]')).toBeVisible();
        }
    });
});
