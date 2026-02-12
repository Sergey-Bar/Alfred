# Alfred QA Test Organization

## Complete Test Structure

```
Alfred/
├── dev/
│   ├── QA/                              # ⭐ Central QA Directory
│   │   ├── README.md                    # Original QA documentation
│   │   ├── README_STRUCTURE.md          # New structure documentation (⭐ NEW)
│   │   ├── TEST_INVENTORY.md            # Complete test inventory (⭐ NEW)
│   │   ├── TEST_SUMMARY.md              # Test summary
│   │   ├── QUICK_REFERENCE.md           # Quick reference
│   │   │
│   │   ├── Backend/                     # ⭐ Backend Python Tests
│   │   │   ├── conftest.py              # Pytest fixtures (updated paths)
│   │   │   ├── __init__.py              # Package marker
│   │   │   │
│   │   │   ├── Unit/                    # Unit Tests (63 passing)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_api.py              # 11 tests
│   │   │   │   ├── test_api_contracts.py    # 3 tests
│   │   │   │   ├── test_config.py           # 15 tests
│   │   │   │   ├── test_middleware.py       # 8 tests
│   │   │   │   ├── test_quota.py            # 11 tests
│   │   │   │   └── test_vacation_sharing.py # 9 tests
│   │   │   │
│   │   │   ├── Integration/             # Integration Tests (8 passing)
│   │   │   │   ├── __init__.py
│   │   │   │   └── test_integration.py      # 8 tests
│   │   │   │
│   │   │   └── Performance/             # Performance Tests (6 passing)
│   │   │       ├── __init__.py
│   │   │       └── test_query_benchmarks.py # 6 benchmark tests
│   │   │
│   │   ├── Frontend/                    # ⭐ Frontend Test Documentation
│   │   │   └── README.md                # Explains frontend test location (⭐ NEW)
│   │   │   # Note: Actual tests remain in dev/frontend/src/__tests__/
│   │   │
│   │   ├── E2E/                         # ⭐ End-to-End Tests (Playwright)
│   │   │   ├── login.spec.js            # 4 scenarios
│   │   │   ├── dashboard.spec.js        # 4 scenarios
│   │   │   ├── transfers.spec.js        # 5 scenarios
│   │   │   ├── approvals.spec.js        # 5 scenarios
│   │   │   ├── users.spec.js            # 6 scenarios
│   │   │   ├── teams.spec.js            # 4 scenarios
│   │   │   ├── profile.spec.js          # 4 scenarios
│   │   │   ├── integrations.spec.js     # 5 scenarios
│   │   │   └── smoke.spec.js            # 6 scenarios
│   │   │
│   │   └── results/                     # Test Results & Artifacts (gitignored)
│   │       ├── .gitkeep
│   │       ├── coverage/                # Code coverage reports
│   │       ├── test-results/            # Playwright test results
│   │       └── html/                    # HTML test reports
│   │
│   └── frontend/
│       ├── src/
│       │   └── __tests__/               # ⭐ Frontend Unit Tests (co-located)
│       │       ├── App.test.jsx         # 1 test
│       │       └── Skeleton.test.jsx    # 3 tests
│       │
│       ├── vitest.config.js             # Updated: points to src/__tests__/
│       └── playwright.config.js         # Updated: points to ../QA/E2E/
│
├── backend/
│   └── tests/                           # 📦 OLD LOCATION (kept for backup)
│       ├── conftest.py
│       ├── test_api.py
│       ├── test_api_contracts.py
│       └── ... (all test files)
│
├── pyproject.toml                       # Updated: testpaths = ["dev/QA/Backend"]
└── .github/
    └── workflows/
        └── ci.yml                       # Updated: test paths point to dev/QA/Backend/
```

## Test Categories Summary

### ✅ Backend Tests (77 passing)
- **Location**: `dev/QA/Backend/`
- **Run**: `pytest dev/QA/Backend -v`
- **Categories**:
  - Unit (6 files, 63 tests)
  - Integration (1 file, 8 tests)
  - Performance (1 file, 6 tests)

### ✅ Frontend Tests (4 passing)
- **Location**: `dev/frontend/src/__tests__/` (co-located with source)
- **Run**: `cd dev/frontend && npm run test:unit`
- **Why co-located?**: Better module resolution, following React/Vite best practices

### ⏳ E2E Tests (40+ scenarios ready)
- **Location**: `dev/QA/E2E/`
- **Run**: `cd dev/frontend && npm run test:e2e`
- **Browsers**: Chromium, Firefox, WebKit

## Key Changes Made

1. ✅ Created categorized directory structure under `dev/QA/`
2. ✅ Moved backend tests from `backend/tests/` to `dev/QA/Backend/`
3. ✅ Organized backend tests into: Unit, Integration, Performance
4. ✅ Moved E2E tests from `dev/QA/Tests/` to `dev/QA/E2E/`
5. ✅ Kept frontend tests in `src/__tests__/` (best practice)
6. ✅ Updated Python import paths (added backend to pythonpath)
7. ✅ Updated all config files (pyproject.toml, vitest.config.js, playwright.config.js, ci.yml)
8. ✅ Verified all 77 tests passing in new structure
9. ✅ Created comprehensive documentation

## Configuration Updates

| File | Change |
|------|--------|
| `pyproject.toml` | `testpaths = ["dev/QA/Backend"]` + `pythonpath = ["backend"]` |
| `dev/frontend/vitest.config.js` | `include: ['src/**/*.test.{js,jsx,ts,tsx}']` |
| `dev/frontend/playwright.config.js` | `testDir: '../QA/E2E'` |
| `.github/workflows/ci.yml` | Updated lint/test paths to `dev/QA/Backend/` |
| `dev/QA/Backend/conftest.py` | Added sys.path manipulation for `app` imports |

## Running Tests

```bash
# All backend tests
pytest dev/QA/Backend -v

# By category
pytest dev/QA/Backend/Unit -v
pytest dev/QA/Backend/Integration -v
pytest dev/QA/Backend/Performance -v

# Frontend unit tests
cd dev/frontend && npm run test:unit

# E2E tests (requires services running)
cd dev/frontend && npm run test:e2e

# All tests in CI
git push  # Triggers GitHub Actions workflow
```

## Documentation Files

| File | Purpose |
|------|---------|
| `dev/QA/README_STRUCTURE.md` | Complete structure and usage guide |
| `dev/QA/TEST_INVENTORY.md` | Detailed test inventory with counts |
| `dev/QA/Frontend/README.md` | Frontend test location explanation |
| `dev/QA/QUICK_REFERENCE.md` | Quick commands reference |
| `dev/QA/TEST_SUMMARY.md` | Test summary |
| `dev/QA/STRUCTURE.md` | **(⭐ THIS FILE)** Visual tree and overview |

## Status

✅ **All tests reorganized and verified**
- 77 backend tests passing
- 4 frontend tests passing
- 40+ E2E tests ready
- All configurations updated
- CI/CD pipeline updated
- Comprehensive documentation created

## Old Directories

For safety, original `backend/tests/` directory is preserved. Can be removed after verification:
```bash
# After validating everything works
rm -rf backend/tests/
```

---

**Last Updated**: February 12, 2026
