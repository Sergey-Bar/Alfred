# Market Standard Practices (Required)

- **CI/CD Integration:** Automate testing, deployment, rollback, and monitoring for all code and AI changes. Use pipelines to enforce quality gates and compliance checks.
- **Incident Response & Recovery:** Maintain playbooks for handling AI failures, bugs, and compliance incidents. Include rollback, escalation, and communication procedures.
- **Model Versioning & Lifecycle:** Track, upgrade, and deprecate AI models with clear versioning, compatibility, and migration strategies.
- **Responsible AI & Ethics:** Implement bias mitigation, explainability, and ethical review for AI-generated code and decisions. Document risk assessments and mitigation steps.
- **User Feedback & Continuous Learning:** Collect and analyze user feedback to improve AI and workflows. Integrate feedback loops into development and release cycles.
- **Onboarding & Training:** Provide onboarding checklists for new contributors, covering access, security, documentation review, and project conventions.
- **Metrics & KPIs:** Define and monitor key performance indicators for code quality, AI accuracy, velocity, coverage, and compliance.
# Best Handshake Practices: AI ↔ AI & Human ↔ Human

## AI ↔ AI Model Handshake
- **Interoperability:** Ensure models use standardized API contracts, data formats, and versioning for seamless integration.
- **Clear Protocols:** Define explicit handoff points, error handling, and fallback logic between models (e.g., primary/secondary, ensemble, escalation).
- **Audit & Trace:** Log all inter-model interactions, including model version, input/output, and decision rationale for traceability.
- **Performance Monitoring:** Continuously monitor latency, accuracy, and reliability of model-to-model handshakes; automate alerts for anomalies.
- **Fallback/Escalation:** If a model fails or produces uncertain results, escalate to a more advanced model or human reviewer as needed.
- **Security:** Validate and sanitize all data exchanged between models to prevent injection or propagation of errors.

## Human ↔ Human Handshake
- **Clear Roles:** Define responsibilities and review checkpoints for each participant in the workflow.
- **Documentation:** Maintain transparent logs of decisions, code reviews, and rationale for changes.
- **Feedback Loops:** Establish regular feedback and retrospective sessions to improve collaboration and process.
- **Escalation Paths:** Set clear escalation procedures for unresolved issues, blockers, or critical decisions.
- **Knowledge Sharing:** Use internal wiki, runbooks, and learning events to ensure knowledge transfer and onboarding.
- **Security & Compliance:** Ensure all handoffs comply with security, privacy, and regulatory requirements.

# Best Practices for AI-Driven Development Projects

When AI is the primary developer, follow these best practices to ensure quality, maintainability, and transparency:

- **AI-Generated Code Marking:** Every AI-generated or AI-modified code block must include a comment header with model name, logic/reasoning, root cause, context, and model suitability (see Project Rulebook).
- **Human-in-the-Loop Review:** All AI-generated code, documentation, and configuration changes must be reviewed by a human (project lead or designated reviewer) before merging to main.
- **Comprehensive Documentation:** Document all major changes, rationale, and AI involvement in the changelog and code_review folder. Maintain clear API contracts and architectural diagrams.
- **Automated & Manual Testing:** Use automated tests (unit, integration, E2E) for all features. Supplement with manual exploratory testing, especially for edge cases and compliance scenarios.
- **Security & Compliance:** Review dependencies for security and license compliance. Never commit credentials or sensitive data. Automate vulnerability scans and compliance checks.
- **Transparency & Traceability:** Maintain clear logs of AI-generated changes, including model version and reasoning. Enable traceability for all code and configuration changes.
- **Continuous Improvement:** Regularly update AI instructions, test coverage, and documentation based on feedback and evolving requirements. Schedule periodic audits of AI-generated code for quality and compliance.
- **Model Selection:** Prefer the most advanced model for critical logic. Use standard/premium models for production, compliance, and mission-critical workflows.
- **Fallback & Escalation:** If AI cannot resolve an issue, escalate to a human reviewer or project lead for guidance and resolution.

# Alfred Copilot Instructions

> **Alfred** is an enterprise AI credit governance platform—a FastAPI proxy that manages token quotas across 100+ LLM providers with unified credit governance, analytics, and enterprise SSO.

---

## Architecture & Big Picture
- **Three-layer design:**
	1. **Proxy Gateway (FastAPI):** Request interception, quota enforcement, OpenAI-compatible API.
	2. **Ledger System:** Tracks credits, transactions, quotas, and audit logs (PostgreSQL/SQLite).
	3. **SDK/Auth:** API key and SSO/JWT management for users/teams.
- **Data flow:** Requests → Gateway → Quota Manager → LLM Proxy (LiteLLM) → Provider → Ledger update.
- **Key files:**
	- `src/backend/app/main.py` (FastAPI app, router registration)
	- `src/backend/app/dashboard.py` (analytics/reporting endpoints)
	- `src/backend/app/routers/` (modular API routers)
	- `src/frontend/` (React dashboard, Vite, Playwright)
	- `dev/QA/` (all tests: backend, frontend, E2E)
	- `docs/architecture.md` (system diagram, data flow, deployment)

## Developer Workflows
- **Backend:**
	- Install: `pip install -r src/backend/requirements/requirements-dev.txt`
	- Run: `cd src/backend && uvicorn app.main:app --reload`
	- Migrate: `alembic -c src/backend/config/alembic.ini upgrade head`
	- Test: `pytest dev/QA/Backend -v` (unit/integration/performance)
- **Frontend:**
	- Install: `cd src/frontend && npm install`
	- Unit tests: `npm run test:unit`
	- E2E: `npm run test:e2e` (Playwright, see `dev/QA/E2E/`)
- **CI/CD:**
	- All tests run on PRs and pushes via `.github/workflows/ci.yml` (lint → backend → frontend → E2E → Docker build)
- **DevOps:**
	- Local stack: `cd dev/devops/docker && docker compose up -d`
	- Monitoring: `/metrics` (Prometheus scrape), Grafana dashboards, Alertmanager rules in `dev/devops/README.md`

## Project Conventions & Patterns
- **API:** OpenAI-compatible `/v1/chat/completions`, plus admin, analytics, quota, and SCIM endpoints.
- **Routers:** All API endpoints are modularized in `src/backend/app/routers/` (e.g., `users.py`, `teams.py`, `governance.py`).
- **Testing:**
	- Backend: Pytest, SQLite in-memory, fixtures in `conftest.py`.
	- Frontend: Vitest + React Testing Library, tests co-located in `src/frontend/src/__tests__/`.
	- E2E: Playwright specs in `dev/QA/E2E/`.
	- Naming: `test_*.py` (backend), `*.test.jsx` (frontend), `*.spec.js` (E2E).
- **Coverage:** Reports in `dev/QA/results/coverage/`.
- **Docs:** API reference in `docs/guides/api.md`, architecture in `docs/architecture.md`.
- **Secrets:** Use `.env` (local), cloud secret manager (prod). Never commit secrets.

## Integration & Cross-Component Patterns
- **Quota logic:** See `dashboard.py`, `logic.py`, and `routers/proxy.py` for credit enforcement, vacation sharing, and priority overrides.
- **Frontend-backend:** React dashboard fetches analytics, leaderboard, and quota via `/dashboard/*` endpoints.
- **Notifications:** Integrations for Slack, Teams, Telegram, WhatsApp in `src/backend/app/integrations/`.
- **Test data:** Use fixtures in `dev/QA/Backend/conftest.py` for isolated, repeatable tests.

## Examples & References
- **Add a backend test:** Place in `dev/QA/Backend/Unit/`, import fixtures from `conftest.py`.
- **Add a frontend test:** Place in `src/frontend/src/__tests__/`, use RTL patterns.
- **Add an E2E test:** Place in `dev/QA/E2E/`, follow Playwright conventions.
- **API contract:** See `docs/guides/api.md` for request/response schemas.

For more, see: `dev/QA/README_STRUCTURE.md`, `dev/QA/TEST_INVENTORY.md`, and `docs/architecture.md`.

---

## Project Rulebook & AI Usage Policy
- **Project Lead:** Sergey Bar is the sole project lead and approves all changes. Only Sergey can merge to main.
- **AI-generated code:** Every AI-generated or AI-modified code block **MUST** include a comment header with:
  - Model name (e.g., GitHub Copilot, GPT-4.1)
  - Logic/reasoning for the change
  - Why and root cause
  - Context for future improvements
  - Suggest a better model if needed
- **This is mandatory for all code, documentation, and configuration changes made by AI.**
- **Manual edits by Sergey Bar do not require this comment.**
- **Changelog & Documentation:** All major changes must be documented in the changelog and code_review folder. Indicate if AI was used.
- **Security:** Review dependencies for security and license compliance. Never commit credentials or sensitive data.

## Model Selection Guidance
- **Free/Discounted models:** Use for routine tasks, prototyping, and documentation (e.g., GPT-4.1, GPT-4o, Claude Haiku 4.5).
- **Standard models:** Use for production code, architecture, and complex workflows (e.g., Claude Sonnet 4.5, Gemini 3 Pro, GPT-5.1-Codex).
- **Premium models:** Use for compliance, mission-critical, or high-stakes scenarios (e.g., Claude Opus 4.5).
- Prefer the most advanced model for critical logic.

### Example AI-Generated Comment
```js
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Implements error handling for API failures as recommended in code review.
// Why: Previous implementation did not handle network errors, causing user confusion.
// Root Cause: Missing try/catch around fetch call; error messages were not user-friendly.
// Context: This API is called from the VS Code extension status bar and must always show a clear error state.
// Model Suitability: For complex error handling patterns, GPT-4 Turbo or Claude 3 may provide more robust suggestions due to better reasoning capabilities.
```
