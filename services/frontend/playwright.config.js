// Playwright configuration for E2E tests
import { devices } from '@playwright/test';

/** @type {import('@playwright/test').PlaywrightTestConfig} */
export default {
    testDir: '../QA/E2E',
    timeout: 30 * 1000,
    expect: {
        timeout: 5000
    },
    outputDir: '../QA/results/test-results',
    reporter: [
        ['html', { outputFolder: '../QA/results/html', open: 'never' }],
        ['json', { outputFile: '../QA/results/results.json' }],
        ['list']
    ],
    use: {
        headless: true,
        baseURL: process.env.BASE_URL || 'http://localhost:5173',
        viewport: { width: 1280, height: 720 },
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        trace: 'retain-on-failure'
    },
    projects: [
        { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
        { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
        { name: 'webkit', use: { ...devices['Desktop Safari'] } }
    ],
    webServer: {
        command: 'npm run dev',
        port: 5173,
        reuseExistingServer: !process.env.CI
    }
};
