# QA Directory Structure

All tests for the Alfred project are now organized under this directory for better maintainability and clarity.

## Directory Organization

```
qa/
├── Backend/                    # Backend Python tests
│   ├── conftest.py            # Shared pytest fixtures
│   ├── __init__.py            # Package marker
│   ├── Unit/                  # Unit tests
│   │   ├── test_api.py              # API endpoint tests
│   │   ├── test_api_contracts.py    # API contract/schema tests
│   │   ├── test_config.py           # Configuration tests
│   │   ├── test_middleware.py       # Middleware tests
│   │   ├── test_quota.py            # Quota management tests
│   │   └── test_vacation_sharing.py # Vacation/token sharing tests
│   ├── Integration/           # Integration tests
│   │   └── test_integration.py      # Cross-component integration
│   └── Performance/           # Performance/benchmark tests
│       └── test_query_benchmarks.py # Database query performance
│
├── Frontend/                   # Frontend JavaScript tests
│   └── README.md              # Explains frontend test location
│   └── (Tests located in: src/frontend/src/__tests__/)
│       ├── App.test.jsx            # Main App component tests
│       └── Skeleton.test.jsx       # Skeleton component tests
│
├── E2E/                       # End-to-end tests (Playwright)
│   ├── login.spec.js              # Login flow tests
│   ├── dashboard.spec.js          # Dashboard tests
│   ├── transfers.spec.js          # Token transfer tests
│   ├── approvals.spec.js          # Approval workflow tests
│   ├── users.spec.js              # User management tests
│   ├── teams.spec.js              # Team management tests
│   ├── profile.spec.js            # User profile tests
│   ├── integrations.spec.js       # Integration settings tests
│   └── smoke.spec.js              # Critical path smoke tests
│
└── results/                   # Test output and artifacts (gitignored)
    ├── coverage/              # Code coverage reports
    ├── test-results/          # Test execution results
    └── html/                  # HTML test reports
```

## Running Tests

### Backend Tests

Run all backend tests:
```bash
# From project root
pytest qa/Backend -v

# Run specific category
pytest qa/Backend/Unit -v
pytest qa/Backend/Integration -v
pytest qa/Backend/Performance -v

# Run with coverage
pytest qa/Backend --cov=src/backend/app --cov-report=html
```

### Frontend Unit Tests

**Note**: Frontend tests remain in `src/frontend/src/__tests__/` (co-located with source code) for better module resolution and following React/Vite best practices.

```bash
# From dev/frontend
npm run test:unit

# Watch mode
npm run test:unit -- --watch

# With coverage
npm run test:unit -- --coverage
```

### E2E Tests (Playwright)

```bash
# From dev/frontend
npm run test:e2e

# Run specific browsers
npm run test:e2e -- --project=chromium
npm run test:e2e -- --project=firefox

# Headed mode (see browser)
npm run test:e2e -- --headed

# Debug mode
npm run test:e2e -- --debug
```

## Test Categories

### Unit Tests
- **Backend/Unit/**: Fast, isolated tests for individual functions/classes
- **Frontend/Unit/**: React component rendering and behavior tests
- **Characteristics**: No external dependencies, fast execution, high coverage

### Integration Tests
- **Backend/Integration/**: Tests multiple components working together
- **Characteristics**: Database connections, API calls between modules

### Performance Tests
- **Backend/Performance/**: Benchmark tests to catch performance regressions
- **Characteristics**: Time assertions, large datasets, query optimization validation

### E2E Tests
- **E2E/**: Full user workflows from UI to database
- **Characteristics**: Real browser, full application stack, user perspective

## CI/CD Integration

Tests run automatically on:
- **Push to main/develop**: All test suites
- **Pull requests**: All test suites
- **Test order**: Lint → Backend tests → Frontend tests → E2E tests → Docker build

See `.github/workflows/ci.yml` for full CI configuration.

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Pytest configuration, testpaths: `qa/Backend` |
| `playwright.config.js` | Playwright E2E test configuration |
| `vitest.config.js` | Vitest unit test configuration for frontend |

## Adding New Tests

### Backend Test
1. Choose category: Unit, Integration, or Performance
2. Create `test_*.py` file in appropriate directory
3. Import fixtures from `../conftest.py`
4. Follow existing naming conventions

### Frontend Test  
1. Create `*.test.jsx` in `Frontend/Unit/`
2. Import test utilities from `setupTests.js`
3. Use React Testing Library patterns

### E2E Test
1. Create `*.spec.js` in `E2E/`
2. Follow Page Object Model pattern (optional)
3. Use descriptive test names
4. Include setup/teardown for test iso (✅ Moved)
- `src/frontend/src/__tests__/` → Remains in place (co-located with source)
- `qa/Tests/` → `qa/E2E/` (✅ Moved)

Old `backend/tests/` directorywas reorganized from:
- `backend/tests/` → `qa/Backend/`
- `src/frontend/src/__tests__/` → `qa/Frontend/Unit/`
- `qa/Tests/` → `qa/E2E/`

Old directories kept for backward compatibility (can be removed after verification).

## Best Practices

1. **Keep tests fast**: Unit tests < 100ms, Integration < 1s, E2E < 30s
2. **Isolate tests**: Each test should be independent
3. **Use fixtures**: Share setup code via conftest.py or setupTests.js
4. **Descriptive names**: Test names should explain what they verify
5. **Coverage targets**: Aim for 80%+ coverage on business logic
6. **Performance benchmarks**: Update benchmarks when optimizing queries

## Test Status

- ✅ Backend Unit Tests: 63 passing
- ✅ Backend Integration Tests: 8 passing
- ✅ Backend Performance Tests: 6 passing
- ✅ Frontend Unit Tests: 4 passing
- ⏳ E2E Tests: Ready to run (40+ scenarios)

Total: **77 passing tests** across all categories
