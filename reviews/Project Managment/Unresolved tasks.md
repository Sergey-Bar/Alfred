<!--
[AI GENERATED]
Logic: Consolidated all open/unfinished items from the Project Managment review files into a single actionable list.
Why: User requested merging the folder's files into three sorted outputs (Unresolved tasks, changelog, resolved tasks).
Root Cause: Multiple scattered review and planning documents containing outstanding defects and in-progress roadmap items.
Context: Sources: PLAN_TASKS_STATUS.md, Product Plan.md, PROJECT_CODE_REVIEW_DEFECTS.md, PROJECT_CODE_REVIEW.md, PROJECT_DEFECTS.md, PROJECT_OVERVIEW.md (merged 2026-02-16).
-->

# Unresolved Tasks

Source: consolidated from the Project Managment review files in this folder.

## Summary

- This document collects outstanding defects, in-progress roadmap items, and security / CI issues that require remediation.

## High-priority Defects (Backend)

- Test configuration issues (conftest.py path problems across test directories).
- Duplicate FastAPI app instantiation in `src/backend/app/main.py`.
- Outdated dependencies (rq, pytest-asyncio, pytest-cov, etc.) needing upgrades.
- Router stubs (data_enrichment, data_lineage) lack persistence; implement persistence or remove stubs.
- Database query optimization: replace multiple selects with joins in quota logic.
- Remove importing all routers at startup; implement lazy or conditional router registration to improve startup.
- Implement missing logging across modules; ensure consistent logging levels and formats.
- Fix mixed tabs/spaces, trailing whitespace, import ordering (ruff/flake8/ruff config updates as needed).

## High-priority Defects (Frontend)

- `exportCSV.js`: add user feedback for no-data, handle file errors, validate CSV compatibility.
- `usageAnalytics.js`, `metrics.js`, `dataQuality.js`, `dataLineage.js`: add robust API error handling and input validation; add pagination where appropriate.

## DevOps / CI / Security Issues

- CI workflows and devops defaults expose placeholder or weak credentials (workflows and docker-compose use `changeme`/`test_password`) — replace with repository secrets and required env validation.
- Documentation includes example keys/secrets: mark examples clearly and ensure no real secrets are ever included.
- Flaky healthcheck commands in Docker Compose: replace network calls with lightweight TCP checks or robust retry wrappers.
- Add CI secret-scan step and gate builds on high-confidence findings.

## Tests & QA

- Consolidate multiple test directories (`dev/QA/Backend`, `qa/QA/Backend`, `tests/`) and unify `pytest` configuration to avoid path confusion.
- Centralize test credentials in fixtures instead of scattered literals in E2E tests.
- Remove or gate debug `print()` statements; use logger with environment-controlled verbosity.

## Product / Roadmap Items (Not Started / In Progress)

- Prompt safety & content filtering (PII, secrets, injection detection).
- Data residency & sovereignty: geo-routing, provider compliance tags, audit trail.
- Shadow IT detection (browser extension, network monitoring).
- Predictive budget management (burn rate, forecasting, anomaly detection).
- Cost attribution & chargebacks (tagging, reports, project budgets).
- Response quality tracking and model benchmarking (A/B, cost/quality tradeoffs).
- Semantic caching, intelligent fallbacks, testing & staging improvements.
- Collaboration features: conversation sharing & review, ROI & impact measurement.
- Multi-tenancy/white-labeling, procurement/vendor workflows, advanced RBAC & delegation.

## Project Code Review Defects (Automated Findings)

- Remove plaintext credentials from CI and docker-compose; use `${{ secrets.NAME }}` or required envs.
- Centralize test credentials in a documented test fixture file.
- Remove stray debug prints; gate verbose logging.
- Standardize test folder layout and pytest configuration.

## Suggested Next Steps

1. Triage defects by priority and assign owners (security, backend, frontend, devops).
2. Add CI jobs to fail on placeholder secrets and run secret-scan tools.
3. Create issues for each high-priority backend and frontend defect with reproduction steps.
4. Consolidate test configuration and update CI to run unified test path.
5. Plan and schedule roadmap items into release cycles (owners + estimates).

---

_If you want these entries split into smaller per-area files or converted into GitHub issues automatically, I can do that next._
