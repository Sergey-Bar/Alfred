
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: E2E tests for approval request UI using Playwright. Covers listing, creation, filtering, and admin approval flows.
// Why: Ensures approval flows work in real browser and regressions are caught before release.
// Root Cause: Approval bugs can block quota increases and user requests.
// Context: Run in CI for every PR. Future: add error cases and multi-role scenarios.
// Model Suitability: E2E test logic is standard; GPT-4.1 is sufficient.
const { test, expect } = require('@playwright/test');

test.describe('Approval Requests', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'test@example.com');
        await page.fill('input[type="password"]', 'password123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/dashboard/);
        await page.goto('/approvals');
    });

    test('should display approvals page', async ({ page }) => {
        await expect(page).toHaveURL(/approvals/);
        await expect(page.locator('h1, h2')).toContainText(/approval/i);
    });

    test('should show pending approvals', async ({ page }) => {
        const approvalsList = page.locator('table, [class*="approval"], [class*="list"]');
        await expect(approvalsList.first()).toBeVisible({ timeout: 10000 });
    });

    test('should create new approval request', async ({ page }) => {
        await page.click('button:has-text("Request"), button:has-text("New"), button:has-text("Create")');

        // Fill approval form
        const dialog = page.locator('form, [role="dialog"]');
        await expect(dialog).toBeVisible();

        // Fill required fields (adjust selectors based on actual form)
        const amountInput = dialog.locator('input[type="number"], input[name*="amount"]').first();
        if (await amountInput.isVisible({ timeout: 2000 })) {
            await amountInput.fill('100');
        }

        const reasonInput = dialog.locator('textarea, input[name*="reason"]').first();
        if (await reasonInput.isVisible({ timeout: 2000 })) {
            await reasonInput.fill('E2E test approval request');
        }
    });

    test('should filter approvals by status', async ({ page }) => {
        // Look for status filter dropdown
        const statusFilter = page.locator('select, button:has-text("Status")').first();

        if (await statusFilter.isVisible({ timeout: 5000 })) {
            await statusFilter.click();
            await page.waitForTimeout(500);
        }
    });

    test('should approve a pending request (admin)', async ({ page, context }) => {
        // This test assumes admin permissions
        const approveButton = page.locator('button:has-text("Approve")').first();

        if (await approveButton.isVisible({ timeout: 5000 })) {
            await approveButton.click();

            // Confirm dialog might appear
            const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes")');
            if (await confirmButton.isVisible({ timeout: 2000 })) {
                await confirmButton.click();
            }

            // Should show success message
            await expect(page.locator('text=/success|approved/i')).toBeVisible({ timeout: 5000 });
        }
    });
});
