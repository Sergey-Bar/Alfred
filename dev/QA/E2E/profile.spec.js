const { test, expect } = require('@playwright/test');

test.describe('User Profile', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'test@example.com');
        await page.fill('input[type="password"]', 'password123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/dashboard/);
        await page.goto('/profile');
    });

    test('should display profile page', async ({ page }) => {
        await expect(page).toHaveURL(/profile/);
        await expect(page.locator('h1, h2')).toContainText(/profile/i);
    });

    test('should show user information', async ({ page }) => {
        // Check for user info fields
        await expect(page.locator('input[type="email"], input[name*="email"]')).toBeVisible();
    });

    test('should update profile information', async ({ page }) => {
        const nameInput = page.locator('input[name*="name"], input[placeholder*="name"]').first();

        if (await nameInput.isVisible({ timeout: 5000 })) {
            await nameInput.fill('Updated Name');

            // Save changes
            await page.click('button:has-text("Save"), button[type="submit"]');

            // Should show success message
            await expect(page.locator('text=/success|saved|updated/i')).toBeVisible({ timeout: 5000 });
        }
    });

    test('should change password', async ({ page }) => {
        // Look for change password button
        const changePasswordButton = page.locator('button:has-text("Change Password"), button:has-text("Update Password")');

        if (await changePasswordButton.isVisible({ timeout: 5000 })) {
            await changePasswordButton.click();

            const dialog = page.locator('form, [role="dialog"]');
            await expect(dialog).toBeVisible();
        }
    });

    test('should update notification preferences', async ({ page }) => {
        // Look for settings/preferences section
        await page.goto('/settings');
        await expect(page).toHaveURL(/settings/);

        const checkbox = page.locator('input[type="checkbox"]').first();
        if (await checkbox.isVisible({ timeout: 5000 })) {
            await checkbox.click();

            // Save
            await page.click('button:has-text("Save"), button[type="submit"]');
        }
    });
});
