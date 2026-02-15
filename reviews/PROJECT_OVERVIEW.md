# Alfred Project Overview

Alfred is an enterprise AI Credit Governance Platform designed to help organizations manage, allocate, and monitor shared API credit pools for large language model (LLM) providers such as OpenAI, Anthropic, Azure, and Google. It provides a governance layer for user quotas, team budgets, vacation reallocation, approval workflows, and efficiency tracking, making it ideal for B2B environments with complex credit management needs.

## Key Features
- **Credit Pool Governance:** Allocate and track enterprise credits for users and teams.
- **Real-time Analytics:** Monitor usage, costs, and efficiency metrics.
- **Budget Reallocation:** Admins can redistribute credits between users and teams.
- **Vacation Mode:** Automatically releases idle quotas to the team pool.
- **Priority Overrides:** Emergency bypass for critical projects.
- **Privacy Mode:** Prevents logging of sensitive requests.
- **Multi-Provider Support:** Works with 100+ LLM providers via LiteLLM integration.
- **Extensible API:** OpenAI-compatible endpoints for easy integration.


## Architecture & Recent Improvements
- **Three-Layer Design:**
  1. Proxy Gateway for request interception and quota enforcement
  2. Ledger System for credit ownership and transaction tracking
  3. SDK/Authentication for user identity and key management
- **Modular Backend:** Built with Python (FastAPI, SQLModel, Alembic)
- **Modern Frontend:** Built with React and Vite
- **DevOps Ready:** Docker, Kubernetes, CI/CD, and Helm charts

### Recent Roadmap Progress (Feb 2026)
- All moderate-complexity items from the roadmap have been scaffolded and documented:
  - GitOps onboarding docs and API ([docs/gitops_onboarding.md](../docs/gitops_onboarding.md))
  - Docker Compose unification ([docs/docker_compose_unification.md](../docs/docker_compose_unification.md))
  - Dockerfile path consistency ([docs/dockerfile_path_consistency.md](../docs/dockerfile_path_consistency.md))
  - Multi-region/sharding strategies ([docs/multi_region_sharding.md](../docs/multi_region_sharding.md))
- See the [changelog](changelog.md) for rationale, root cause, and future context for each improvement.

## Monitoring & Alerting
- **Prometheus & Grafana:** Metrics are exposed via /metrics and can be scraped by Prometheus. Dashboards in Grafana provide real-time visibility into API usage, quota consumption, error rates, and system health.
- **Alerting:** Alertmanager is configured to notify on quota exhaustion, high error rates, and abnormal latency. Slack and email integrations are available for critical alerts.
- **Recommendations:**
  - Expand alert coverage to include SSO/OAuth failures, integration outages, and background job failures.
  - Add synthetic monitoring tools like Pingdom or Checkly for health checks of all integrations and SSO endpoints.
  - Document runbooks for common alert scenarios and escalation procedures.

## Visual Regression Testing
- **Current State:**
  - E2E tests are implemented using Playwright for user flows and UI validation.
- **Recommendations:**
  - Integrate visual regression testing tools such as Percy or Chromatic for Storybook to catch unintended UI changes.
  - Automate visual diff checks in CI for all major user flows and component stories.
  - Maintain a baseline of approved UI snapshots and review diffs as part of the PR process.
  - Document the process for updating and reviewing visual baselines.

## How to Present Alfred
- **Target Audience:** Enterprise IT, AI platform teams, and decision-makers managing LLM usage at scale.
- **Demo Focus:**
  - Show the dashboard with real-time quota and usage analytics
  - Demonstrate credit reallocation and approval workflows
  - Highlight integration with multiple LLM providers
  - Emphasize security, audit logging, and compliance features
- **Key Value Props:**
  - Centralized governance for AI credit usage
  - Cost control and efficiency
  - Seamless integration with existing workflows
  - Scalable for organizations of any size

## AI Model Suitability Review
- **Policy:** Periodically review the AI models used for code generation, documentation, and advanced reasoning tasks to ensure optimal results and cost-effectiveness.
- **Process:**
  - At least once per quarter, evaluate the current models (e.g., GPT-4.1, Claude 3, Gemini 1.5, Llama 3) against project needs and industry benchmarks.
  - For critical business logic, prefer the most advanced model available (see RULEBOOK).
  - For documentation, policy, or summarization, consider models with strong natural language capabilities (e.g., Claude 3, GPT-4 Turbo).
  - For large-scale codebase analysis, use models with large context windows (e.g., Gemini 1.5).
  - Document any model changes and rationale in the changelog and RULEBOOK.
- **Guidance:**
  - If a model is found to be suboptimal for a given task, note this in code comments and suggest a better alternative.
  - Stay informed about new model releases and major updates from OpenAI, Anthropic, Google, and Meta.
  - Involve both AI and human reviewers in the evaluation process for high-impact changes.
  - **Update:** Include GPT-5 and Claude 4 in the next evaluation cycle.

## Test Coverage Improvement Plan
- **Goal:** Increase automated test coverage to 80%+ (industry standard) across backend, frontend, and extension.
- **Backend (Python):**
  - Identify untested modules and functions using coverage reports (e.g., pytest-cov).
  - Add unit tests for edge cases, error handling, and integration points (SSO, integrations, notifications).
  - Expand integration and performance tests for API endpoints and background jobs.
- **Frontend (React):**
  - Use Jest and React Testing Library to cover all components, hooks, and context logic.
  - Add tests for error boundaries, loading states, and user flows.
  - Increase E2E coverage with Playwright for critical user journeys.
- **VS Code Extension (TypeScript):**
  - Add unit and integration tests for API client, command palette, and webview logic.
  - Mock API responses and test error scenarios.
- **Process:**
  - Track coverage in CI and fail builds if coverage drops below target.
  - Add a coverage badge to the README for visibility.
  - Review and update tests as new features are added.
- **Milestones:**
  - **Q1:** Achieve 60% coverage for backend and frontend.
  - **Q2:** Reach 70% coverage across all components.
  - **Q3:** Attain 80%+ coverage and maintain it.
- **Resources:**
  - See `tests/`, `frontend/src/__tests__/`, and `extension/src/test/` for current test suites.
  - Use coverage tools: pytest-cov, coverage.py, Jest, Playwright, nyc (for TypeScript).

---

For more details, see the [user guide](../docs/user_guide.md) and [API documentation](../docs/api.md) in the `docs/` folder.