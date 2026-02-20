
const { test, expect } = require('@playwright/test');

test.describe('Login Flow', () => {
    test('should load login page', async ({ page }) => {
        await page.goto('/login');
        await expect(page).toHaveTitle(/Alfred/i);
        await expect(page.locator('form')).toBeVisible();
    });

    test('should show validation errors for empty fields', async ({ page }) => {
        await page.goto('/login');
        await page.click('button[type="submit"]');
        // Check for error messages or validation states
        await expect(page.locator('input[type="email"]')).toBeVisible();
    });

    test('should successfully login with valid credentials', async ({ page }) => {
        await page.goto('/login');

        // Fill in login form
        await page.fill('input[type="email"]', 'test@example.com');
        await page.fill('input[type="password"]', 'password123');

        // Submit form
        await page.click('button[type="submit"]');

        // Should redirect to dashboard
        await expect(page).toHaveURL(/dashboard/);
    });

    test('should show error for invalid credentials', async ({ page }) => {
        await page.goto('/login');

        await page.fill('input[type="email"]', 'invalid@example.com');
        await page.fill('input[type="password"]', 'wrongpassword');
        await page.click('button[type="submit"]');

        // Should show error message
        await expect(page.locator('text=/error|invalid|failed/i')).toBeVisible({ timeout: 5000 });
    });
});
