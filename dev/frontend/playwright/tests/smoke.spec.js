const { test, expect } = require('@playwright/test');

test.describe('smoke', () => {
    test('app loads and returns 200', async ({ page, baseURL }) => {
        const url = baseURL || process.env.STAGING_URL || 'http://localhost:5173';
        const response = await page.goto(url, { waitUntil: 'domcontentloaded' });
        // If navigation returned a response, assert it's not an error
        if (response) {
            expect(response.status()).toBeLessThan(400);
        } else {
            // Some hosts may redirect or not return a response for SPA; assert DOM loads
            await expect(page.locator('body')).toBeVisible();
        }
    });
});
