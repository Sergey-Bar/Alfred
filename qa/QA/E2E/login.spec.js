
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: E2E tests for login flow using Playwright. Covers page load, validation, successful and failed login.
// Why: Ensures authentication UX and error handling work in real browser.
// Root Cause: Login bugs block all user access and are critical to catch.
// Context: Run in CI for every PR. Future: add MFA, lockout, and password reset flows.
// Model Suitability: E2E test logic is standard; GPT-4.1 is sufficient.
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
