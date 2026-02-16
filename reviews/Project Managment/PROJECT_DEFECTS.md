# Alfred Project Defects (as of February 16, 2026)

This file lists all known defects, bugs, and improvement areas identified in the most recent code review. For full rationale and context, see reviews/PROJECT_CODE_REVIEW.md.

---

## Backend

- Test configuration issues (conftest.py path problems)
- Redundant FastAPI app instantiation in src/backend/app/main.py
- Outdated dependencies (rq, pytest-asyncio, pytest-cov, etc.)
- Router stubs (data_enrichment, data_lineage) lack persistence or are unused
- Linting violations: unused imports (F401), unsorted imports (I001), trailing whitespace (W291), tabs instead of spaces (W191)
- Database queries in src/backend/app/logic.py not optimized (should use joins)
- All routers imported at startup (performance overhead)
- Incomplete error handling in routers and core logic
- Incomplete test coverage for core logic and router stubs
- Logging not implemented in all modules
- Duplicate Prometheus instrumentator setup in src/backend/app/main.py
- In-memory storage in routers (not production-ready)
- alias_router reference may not exist in src/backend/app/routers/governance.py
- Hardcoded paths in static file serving
- Mixed tabs and spaces, trailing whitespace in test files
- E402 violations (imports not at top) in tests/unit/conftest.py
- Multiple test directories with inconsistent configuration
- Dependency version pinning (ruff in backend/config/requirements-dev.txt)
- Inconsistent type hints in some files

## Frontend

- exportCSV.js: No user feedback for no data, BOM may cause CSV parser issues, no error handling for file download
- usageAnalytics.js: No API error handling, hardcoded period
- metrics.js: No API error handling, no pagination/filtering for large datasets
- dataQuality.js: No API error handling, no dataset validation
- dataLineage.js: No API error handling, no dataset validation, traceDataOrigin assumes dataset exists

## DevOps & CI/CD

- Minor automation improvements possible

## Documentation & Compliance

- Needs onboarding checklist and more AI code comment examples
- Needs more automation and evidence/reporting formats for compliance

## General

- Periodic audit of AI-generated code recommended
- Collect/analyze user feedback for continuous improvement
- Prefer advanced models for critical logic/compliance
- Maintain transparent logs for all major changes/decisions

---

For detailed explanations and file references, see reviews/PROJECT_CODE_REVIEW.md.
