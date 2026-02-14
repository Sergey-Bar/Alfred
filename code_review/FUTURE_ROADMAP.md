# Alfred Project: Future Roadmap & Engineering Excellence

This document outlines the strategic technical debt reduction and feature enhancements required to move the Alfred platform from its current state to a "Production-Hardened" enterprise solution.

---

## 🏗️ Architectural Refactorings

### 1. Decouple `main.py` Monolith
*   **Description**: Split the 1800+ line `main.py` into domain-specific FastAPI Routers (`/auth`, `/users`, `/teams`, `/governance`). 
*   **Priority**: 🔴 **Highest** (Impacts maintainability and build speed).
*   **Recommended Model**: **Claude 3.5 Sonnet** or **GPT-4 Turbo** (Strong architectural reasoning).
*   **Testing**:
    *   **Regression**: Full E2E suite (`dev/QA/E2E/**`) to ensure route mappings remain identical.
    *   **Integrity**: Smoke test all middleware hooks (Rate Limiting, Security Headers).

### 2. Standardize Financial Precision in Dashboard
*   **Description**: The logic in `main.py` was fixed to use `Decimal`, but `dashboard.py` still uses floating-point aggregates and `float` response types, creating a possible drift in reporting.
*   **Priority**: 🔴 **High** (Critical for organizational trust and audit accuracy).
*   **Recommended Model**: **Claude 3 Opus** (Meticulous with data types).
*   **Testing**:
    *   **Drift Test**: Compare `OverviewStats` output against direct DB SQL aggregates for large datasets.
    *   **Snapshot**: Unit tests for `DashboardResponse` serialization.

---

## 📈 Observability & Scale

### 3. Metric Instrumentation
*   **Description**: `metrics.py` is defined but not integrated. Add Prometheus `labels` and `inc()` calls to the `chat_completions` endpoint and `QuotaManager` to track real-time token burn.
*   **Priority**: 🟠 **High** (Essential for SRE and capacity planning).
*   **Recommended Model**: **GitHub Copilot (GPT-4.1)** (Fast, routine instrumentation).
*   **Testing**:
    *   **Validation**: Verify `/metrics` endpoint exposes `alfred_llm_requests_total` after a simulated chat request.
    *   **Latency**: Check `Histogram` observations for provider response times.

### 4. Redis-Backed Distributed Rate Limiting
*   **Description**: Replace the `asyncio.Lock` + `dict` implementation with a Redis-backed state store to support horizontal pod scaling in Kubernetes.
*   **Priority**: 🟡 **Medium** (Required before multi-node production deployment).
*   **Recommended Model**: **Gemini 1.5 Pro** (Excellent for distributed system design patterns).
*   **Testing**:
    *   **Stress Test**: Run `k6` or `locust` against multiple instances of the backend to ensure the limit is shared globally.
    *   **Resilience**: Test behavior when Redis is temporarily unavailable (fail-open vs fail-closed).

---

## 💎 User Experience & Feature Parity

### 5. VS Code Sidebar Webview
*   **Description**: Implement a dedicated Sidebar view in the extension to allow users to view their transfer history, approvals, and efficiency ranking without using the Command Palette.
*   **Priority**: 🟡 **Medium** (Major usability win).
*   **Recommended Model**: **Claude 3.5 Sonnet** (Top-tier frontend/UI generation).
*   **Testing**:
    *   **Interactivity**: Verify message passing between the Sidebar (Webview) and the Extension Host (Backend calls).
    *   **Theming**: Ensure the UI respects VS Code's native theme (Dark/Light/High Contrast).

### 6. Real-time Approval Push (WebSockets)
*   **Description**: Implement a WebSocket layer to push quota replenishments to the client instantly, removing the rely on the 30s polling cycle.
*   **Priority**: 🔵 **Low** ("Quality of Life" improvement).
*   **Recommended Model**: **GPT-4 Turbo** (Reliable async pattern implementation).
*   **Testing**:
    *   **Connection Lifecycle**: Test auto-reconnect logic and heartbeats.
    *   **Propagation**: Trigger an approval in the dashboard and verify the VS Code status bar updates within <500ms.

---

## ✅ Summary of Recommendations

| Category | Task | Priority | Model |
| :--- | :--- | :--- | :--- |
| **Architecture** | Main Refactor | 🔴 High | Claude 3.5 |
| **Integrity** | Decimal Dashboard | 🔴 High | Claude 3 |
| **Visibility** | Metrics Wiring | 🟠 Med | Copilot |
| **Scaling** | Redis Rate Limit | 🟠 Med | Gemini 1.5 |
| **UX** | Sidebar Webview | 🟡 Low | Claude 3.5 |
| **Speed** | WebSocket Push | 🔵 Low | GPT-4 |

_This roadmap serves as the "Definitions of Done" for the next sprint of engineering work on the Alfred platform._
