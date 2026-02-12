// Playwright configuration for smoke tests
const { devices } = require('@playwright/test');

/** @type {import('@playwright/test').PlaywrightTestConfig} */
module.exports = {
    testDir: './playwright/tests',
    timeout: 30 * 1000,
    expect: {
        timeout: 5000
    },
    use: {
        headless: true,
        baseURL: process.env.STAGING_URL || 'http://localhost:5173',
        viewport: { width: 1280, height: 720 }
    },
    projects: [
        { name: 'chromium', use: { ...devices['Desktop Chrome'] } }
    ]
};
