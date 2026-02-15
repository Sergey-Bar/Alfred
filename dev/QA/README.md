# Alfred QA Test Suite

This directory contains all End-to-End (E2E) tests and test results for the Alfred application. This is the canonical location for E2E Playwright specs and results.

## Directory Structure

```
Dev/QA/
├── E2E/             # E2E Playwright test specifications (canonical)
│   ├── login.spec.js
│   ├── dashboard.spec.js
│   ├── transfers.spec.js
│   ├── approvals.spec.js
│   ├── users.spec.js
│   ├── teams.spec.js
│   ├── profile.spec.js
│   ├── integrations.spec.js
│   └── smoke.spec.js
└── results/         # Test execution results (canonical)
    ├── html/        # HTML reports
    ├── test-results/# Screenshots, videos, traces
    ├── coverage/    # Code coverage reports
    └── results.json # JSON test results
```

**Location**: `dev/QA/E2E/` (canonical)

## Test Suites

### Core Functionality Tests

- **login.spec.js** - Authentication and login flow
- **dashboard.spec.js** - Main dashboard functionality
- **transfers.spec.js** - Credit transfer operations
- **approvals.spec.js** - Approval request management
- **users.spec.js** - User management (admin)
- **teams.spec.js** - Team management
- **profile.spec.js** - User profile and settings
- **integrations.spec.js** - Third-party integrations (Slack, Teams, etc.)

### Health Checks

- **smoke.spec.js** - Basic smoke tests for critical paths

## Running Tests

### Prerequisites

```bash
cd dev/frontend
npm install
```

### Run All E2E Tests

```bash
npm run test:e2e
```

### Run Specific Test Suite

```bash
npx playwright test Tests/login.spec.js
```

### Run Tests in UI Mode

```bash
npx playwright test --ui
```

### Run Tests in Headed Mode (Watch Browser)

```bash
npx playwright test --headed
```

### Run Tests on Specific Browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Viewing Results

### HTML Report

After running tests, open the HTML report:

```bash
npx playwright show-report ../QA/results/html
```

### Test Results

- **HTML Report**: `Dev/QA/results/html/index.html`
- **JSON Results**: `Dev/QA/results/results.json`
- **Screenshots**: `Dev/QA/results/test-results/<test-name>/`
- **Videos**: `Dev/QA/results/test-results/<test-name>/video.webm`
- **Traces**: `Dev/QA/results/test-results/<test-name>/trace.zip`

## Configuration

Playwright configuration is in `dev/frontend/playwright.config.js`:

- Test timeout: 30 seconds
- Screenshots: On failure only
- Videos: Retained on failure
- Traces: Retained on failure
- Browsers: Chromium, Firefox, WebKit

## CI/CD Integration

Tests run automatically on:

- Pull requests to `main` and `develop` branches
- Pushes to `main` and `develop` branches

Results are uploaded as GitHub Actions artifacts.

## Writing New Tests

1. Create a new spec file in `Dev/QA/Tests/`
2. Follow the naming convention: `<feature>.spec.js`
3. Use descriptive test names
4. Include proper assertions
5. Handle async operations with `await`
6. Clean up test data when needed

### Example Test Structure

```javascript
const { test, expect } = require("@playwright/test");

test.describe("Feature Name", () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto("/login");
    // ... login steps
  });

  test("should perform specific action", async ({ page }) => {
    // Arrange
    await page.goto("/feature");

    // Act
    await page.click("button#action");

    // Assert
    await expect(page.locator("#result")).toHaveText("Expected");
  });
});
```

## Best Practices

1. **Use data-testid attributes** for stable selectors
2. **Avoid hard-coded waits** - use Playwright's auto-waiting
3. **Clean up after tests** - reset state when needed
4. **Use Page Object Model** for complex pages
5. **Keep tests independent** - each test should run standalone
6. **Test real user scenarios** - not just happy paths
7. **Handle flakiness** - use proper waiting strategies

## Debugging Tests

### Debug Mode

```bash
npx playwright test --debug
```

### Trace Viewer

```bash
npx playwright show-trace ../QA/results/test-results/<test-name>/trace.zip
```

### Generate Tests

Use Playwright codegen to generate tests:

```bash
npx playwright codegen http://localhost:5173
```

## Troubleshooting

### Tests Failing Locally

1. Ensure backend is running: `cd backend && uvicorn app.main:app`
2. Ensure frontend is running: `cd dev/frontend && npm run dev`
3. Check browser installations: `npx playwright install`

### Timeout Errors

- Increase timeout in `playwright.config.js`
- Check for slow network requests
- Verify selectors are correct

### Flaky Tests

- Add explicit waits: `await page.waitForSelector('#element')`
- Use `waitForLoadState('networkidle')`
- Check for race conditions

## Contact

For questions about tests, contact the QA team or see [CONTRIBUTING.md](../../docs/CONTRIBUTING.md).
