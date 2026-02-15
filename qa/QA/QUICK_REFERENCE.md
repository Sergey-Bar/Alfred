# Quick Test Reference

## 🚀 Quick Start

### Install Dependencies

```bash
cd dev/frontend
npm install
```

### Install Playwright Browsers

```bash
npx playwright install
```

## 🧪 Running Tests (Canonical Structure)

### Unit Tests (Frontend)

```bash
# Run all frontend unit tests
npm run test:unit

# Run in watch mode
npm run test:unit -- --watch

# Run with coverage (output: dev/QA/results/coverage)
npm run test:unit -- --coverage
```

### Unit Tests (Backend)

```bash
# Run all backend unit tests
pytest tests/unit -v

# Run with coverage (output: dev/QA/results/coverage)
pytest --cov=backend/app tests/unit
```

### E2E Tests

```bash
# Run all E2E tests (Playwright)
npm run test:e2e

# Run specific test file
npx playwright test E2E/login.spec.js

# Run in UI mode (interactive)
npx playwright test --ui
```

# Run in headed mode (see browser)

npx playwright test --headed

# Run on specific browser

npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Debug mode

npx playwright test --debug

````


## 🗂️ Results & Coverage (Canonical)

- HTML reports: `dev/QA/results/html/`
- Screenshots, videos, traces: `dev/QA/results/test-results/`
- Code coverage: `dev/QA/results/coverage/`
- JSON results: `dev/QA/results/results.json`

### Unit Test Coverage
```bash
# Coverage report location
dev/QA/results/coverage/index.html
````

### E2E Test Reports

```bash
# Show HTML report
npx playwright show-report ../QA/results/html

# Show trace for failed test
npx playwright show-trace ../QA/results/test-results/<test-name>/trace.zip
```

## 🔧 Debugging

### Generate Test Code

```bash
# Record actions as test code
npx playwright codegen http://localhost:5173
```

### Inspector

```bash
# Step through test with debugger
npx playwright test --debug
```

### Trace Viewer

```bash
# View test execution trace
npx playwright show-trace path/to/trace.zip
```

## 📁 File Locations

| Type         | Location                       |
| ------------ | ------------------------------ |
| Unit Tests   | `dev/frontend/src/__tests__/`  |
| E2E Tests    | `dev/QA/Tests/`                |
| Test Results | `dev/QA/results/`              |
| HTML Reports | `dev/QA/results/html/`         |
| Coverage     | `dev/QA/results/coverage/`     |
| Screenshots  | `dev/QA/results/test-results/` |

## 🎯 Test Suites

| Suite                | Tests | Description              |
| -------------------- | ----- | ------------------------ |
| login.spec.js        | 4     | Authentication flows     |
| dashboard.spec.js    | 4     | Dashboard functionality  |
| transfers.spec.js    | 5     | Credit transfers         |
| approvals.spec.js    | 5     | Approval requests        |
| users.spec.js        | 6     | User management          |
| teams.spec.js        | 4     | Team management          |
| profile.spec.js      | 4     | User profile             |
| integrations.spec.js | 5     | Third-party integrations |
| smoke.spec.js        | 6     | Smoke tests              |

## ⚡ CI/CD

Tests run automatically on:

- ✅ Pull requests to `main` / `develop`
- ✅ Pushes to `main` / `develop`

### CI Workflow Jobs

1. `lint` - Code quality checks
2. `test-backend` - Backend unit tests
3. `test-frontend` - Frontend unit tests
4. `test-e2e` - E2E tests (after backend + frontend)
5. `docker-build` - Build image (after all tests)

### Artifacts

- Test results retained for 7 days
- Download from GitHub Actions → Artifacts

## 🐛 Common Issues

### Tests Timeout

```bash
# Increase timeout in playwright.config.js
timeout: 60 * 1000  # 60 seconds
```

### Browser Not Found

```bash
# Reinstall browsers
npx playwright install --with-deps
```

### Port Already in Use

```bash
# Change port in playwright.config.js
webServer: {
    command: 'npm run dev',
    port: 5174  # Different port
}
```

### Flaky Tests

- Add explicit waits: `await page.waitForSelector('#element')`
- Use `waitForLoadState('networkidle')`
- Check for race conditions

## 📚 Documentation

- [Full QA README](./README.md)
- [Test Summary](./TEST_SUMMARY.md)
- [Playwright Docs](https://playwright.dev)
- [Vitest Docs](https://vitest.dev)

---

**Need Help?** Check [dev/QA/README.md](./README.md) for detailed documentation.
