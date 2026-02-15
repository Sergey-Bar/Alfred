# Alfred Backend Testing Guide

## Running Backend Unit/Integration Tests

**Best Practice:**
Always run backend tests from the `src/backend` directory so that `app` is importable as a package. This ensures all imports like `from app.logic` work reliably and matches CI/CD expectations.

### Example: Run Quota/SSO/JWT Enforcement Tests

```sh
cd src/backend
pytest ../../dev/QA/Backend/Unit/test_quota.py -v
```

### Run All Backend Unit Tests

```sh
cd src/backend
pytest ../../dev/QA/Backend/Unit -v
```

### Run All Backend Integration Tests

```sh
cd src/backend
pytest ../../dev/QA/Backend/Integration -v
```

## Why?

- This approach avoids brittle sys.path hacks and matches Python packaging standards.
- Ensures all `from app.*` imports resolve for both local and CI runs.

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'app'`, make sure you are running pytest from the `src/backend` directory.
- Do not add sys.path hacks to test files; use the correct working directory instead.

---

For more, see the main project README and dev/QA/TEST_INVENTORY.md.
