import { expect, test } from '@playwright/test';

test.describe('Cross-Browser & Device Smoke & A11y Test', () => {
    const devices = [
        { name: 'Desktop', viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 },
        { name: 'iPhone 12', viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)' },
        { name: 'Pixel 5', viewport: { width: 393, height: 851 }, deviceScaleFactor: 2.75, userAgent: 'Mozilla/5.0 (Linux; Android 11; Pixel 5)' }
    ];
    for (const browserType of ['chromium', 'firefox', 'webkit']) {
        for (const device of devices) {
            test(`Homepage loads in ${browserType} on ${device.name}`, async ({ page, browserName }) => {
                test.skip(browserName !== browserType, `Only run in ${browserType}`);
                await page.setViewportSize(device.viewport);
                if (device.userAgent) await page.setUserAgent(device.userAgent);
                // Simulate low-end device throttling
                await page.route('**/*', route => {
                    setTimeout(() => route.continue(), 200); // 200ms artificial latency
                });
                await page.goto('/');
                await expect(page).toHaveTitle(/Alfred/);
                // Automated accessibility check (axe-core)
                const { violations } = await page.evaluate(async () => {
                    // Dynamically load axe-core
                    if (!window.axe) {
                        await new Promise(resolve => {
                            const script = document.createElement('script');
                            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.4.1/axe.min.js';
                            script.onload = resolve;
                            document.head.appendChild(script);
                        });
                    }
                    return window.axe.run();
                });
                expect(violations, `A11y violations: ${JSON.stringify(violations, null, 2)}`).toHaveLength(0);
            });
        }
    }
});
