# Bugs & Improvement Backlog

> Discovered during Sprint implementation sessions 9-10.
> Items are listed by severity — address in order.

---

## 🔴 Critical / Blocking

### BUG-001: Pre-existing test failure — `test_create_user_duplicate_email`

- **File:** [qa/Backend/Unit/test_api.py](qa/Backend/Unit/test_api.py)
- **Issue:** SQLAlchemy `StaticPool` detached instance error. The test's second CREATE call reuses a detached ORM object from a prior session.
- **Impact:** Blocks CI pipeline (exits with failure).
- **Fix:** Adjust conftest fixture to use a fresh session per test, or ensure the duplicate check queries the DB rather than compare detached objects.

---

## 🟠 High Priority

### BUG-002: Slack handlers use placeholder data

- **Files:** [src/backend/app/routers/slack_app.py](src/backend/app/routers/slack_app.py) (lines ~600-720)
- **Issue:** `_handle_forecast_command`, `_handle_top_users_command`, and `send_slack_daily_digest` return hardcoded demo data with `# TODO: replace with DB query` comments.
- **Impact:** Commands will always return fake numbers in production.
- **Fix:** Wire to actual `WalletTransaction` / `AuditLog` queries.

### BUG-003: Analytics handlers return empty data

- **File:** [services/gateway/handler/analytics.go](services/gateway/handler/analytics.go)
- **Issue:** `DailyCostAggregation` and `ExportCostCSV` return empty arrays with `// NOTE: integrate with ClickHouse` placeholders.
- **Impact:** Dashboard analytics pages show no data.
- **Fix:** Implement ClickHouse query integration or at minimum read from the analytics pipeline's in-memory aggregates.

### IMP-001: Frontend pages use hardcoded demo data

- **Pages:** AuditLog.jsx, Experiments.jsx, ApiKeyManagement.jsx
- **Issue:** These 3 pages display realistic-looking fake data that never refreshes. No live API calls.
- **Impact:** Users see stale demo numbers; edits don't persist.
- **Fix:** Wire each page to its corresponding backend endpoint.

---

## 🟡 Medium Priority

### IMP-002: Admin config visible to non-admin users

- **File:** Settings.jsx
- **Issue:** Admin configuration panel (Slack webhooks, SSO, etc.) is visible to all authenticated users.
- **Fix:** Conditionally render the admin section based on `user.role === 'admin'`.

### IMP-003: No accessibility focus trapping in modals

- **Files:** All dialog/modal components (DeleteConfirmDialog, transfer dialogs, etc.)
- **Issue:** No `aria-modal`, no focus trap, no ESC-to-close.
- **Fix:** Wrap modal content in a focus-trap component or use Radix/HeadlessUI Dialog.

### IMP-004: Hardcoded version string

- **File:** Settings.jsx footer
- **Issue:** Version displayed is a hardcoded string rather than read from `package.json` or an API.
- **Fix:** Import version from `package.json` or expose a `/version` API endpoint.

### IMP-005: Go code untested locally

- **Issue:** Go is not installed on the dev machine. All gateway Go code written across sessions 1-10 has never been compiled or tested locally.
- **Impact:** Typos, import path mismatches, or interface mismatches won't be caught until CI.
- **Fix:** Install Go 1.21+, run `go build ./...` and `go vet ./...` in `services/gateway/`.

### IMP-006: Billing reconciliation needs DB wiring

- **File:** [src/backend/app/billing_reconciliation.py](src/backend/app/billing_reconciliation.py)
- **Issue:** `run_monthly_reconciliation()` has a TODO for querying actual ledger data.
- **Fix:** Implement the SQL query against `WalletTransaction` table and register a `/v1/admin/reconciliation` endpoint.

---

## 🟢 Low Priority / Nice-to-Have

### IMP-007: k6 load test import from jslib

- **File:** [qa/Performance/load_test.js](qa/Performance/load_test.js)
- **Issue:** Uses `import { textSummary } from 'https://jslib.k6.io/...'` which requires internet. Should be vendored.
- **Fix:** Download and commit the k6-summary module locally.

### IMP-008: Grafana dashboard metric names need validation

- **File:** [devops/grafana/alfred-gateway-dashboard.json](devops/grafana/alfred-gateway-dashboard.json)
- **Issue:** Prometheus metric names in queries (e.g., `alfred_gateway_requests_total`) are based on the Metrics registry but the actual metric names emitted haven't been confirmed.
- **Fix:** After deploying metrics.go, compare emitted metric names with dashboard queries.

### IMP-009: Splunk/Datadog/PagerDuty not wired into main.go

- **Files:** observability/datadog.go, pagerduty.go, splunk.go
- **Issue:** Integration modules are created but not registered in `main.go` startup.
- **Fix:** Add env-var-gated initialization in `main.go` (e.g., `DD_ENABLED=true`, `PAGERDUTY_ROUTING_KEY`, `SPLUNK_HEC_URL`).

### IMP-010: SLA balancer and geo-router not wired into proxy handler

- **Files:** routing/sla_balancer.go, routing/geo_router.go
- **Issue:** The balancer and geo-router are self-contained modules not yet integrated into the request path.
- **Fix:** Call `SLABalancer.SelectProvider()` and `GeoRouter.Apply()` from the proxy handler before forwarding.

---

## Summary

| Severity  | Count  |
| --------- | ------ |
| Critical  | 1      |
| High      | 3      |
| Medium    | 6      |
| Low       | 4      |
| **Total** | **14** |
