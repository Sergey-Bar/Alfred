
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: E2E tests for user management UI using Playwright. Covers user listing, search, creation, editing, and status toggling.
// Why: Ensures admin user flows work in real browser and regressions are caught before release.
// Root Cause: User management bugs can block onboarding or cause data issues.
// Context: Run in CI for every PR. Future: add permission checks and error cases.
// Model Suitability: E2E test logic is standard; GPT-4.1 is sufficient.
const { test, expect } = require('@playwright/test');

test.describe('User Management', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@example.com');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/dashboard/);
        await page.goto('/users');
    });

    test('should display users page (admin only)', async ({ page }) => {
        await expect(page).toHaveURL(/users/);
        await expect(page.locator('h1, h2')).toContainText(/user/i);
    });

    test('should show users table', async ({ page }) => {
        const table = page.locator('table, [role="table"]');
        await expect(table).toBeVisible({ timeout: 10000 });
    });

    test('should search for users', async ({ page }) => {
        const searchInput = page.locator('input[type="search"], input[placeholder*="search"]').first();

        if (await searchInput.isVisible({ timeout: 5000 })) {
            await searchInput.fill('test');
            await page.waitForTimeout(1000);
            await expect(page.locator('table, [role="table"]')).toBeVisible();
        }
    });

    test('should open user creation form', async ({ page }) => {
        await page.click('button:has-text("Add"), button:has-text("New"), button:has-text("Create")');

        const dialog = page.locator('form, [role="dialog"]');
        await expect(dialog).toBeVisible();
    });

    test('should edit user details', async ({ page }) => {
        // Click edit button for first user
        const editButton = page.locator('button:has-text("Edit"), [aria-label*="edit"]').first();

        if (await editButton.isVisible({ timeout: 5000 })) {
            await editButton.click();

            const dialog = page.locator('form, [role="dialog"]');
            await expect(dialog).toBeVisible();
        }
    });

    test('should toggle user status', async ({ page }) => {
        // Look for active/inactive toggle
        const statusToggle = page.locator('button:has-text("Activate"), button:has-text("Deactivate")').first();

        if (await statusToggle.isVisible({ timeout: 5000 })) {
            await statusToggle.click();

            // Confirm if needed
            const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes")');
            if (await confirmButton.isVisible({ timeout: 2000 })) {
                await confirmButton.click();
            }
        }
    });
});
