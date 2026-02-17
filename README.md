<p align="center">
  <img src="src/frontend/sidebar-big.png" alt="Alfred Logo" width="360"/>
</p>

<!--
  [AI GENERATED]
  Model: GitHub Copilot (GPT-5 mini)
  Logic: Rework the README hero and intro to improve scannability and match modern open-source presentation (inspired by the provided example).
  Why: The original README had useful content but lacked a prominent title, concise tagline, and quick highlights for new readers.
  Root Cause: missing hero and feature-summary structure.
  Context: Keep existing content and links; add a compact hero, badges, feature highlights, and a short Quick Start near the top.
  Model Suitability: GPT-5 mini is appropriate for formatting and copy improvements; for deeper architecture rewrites consider a larger model.
-->

<h1 align="center">Alfred — Enterprise AI Credit Governance Platform</h1>

<p align="center"><strong>One proxy. One dashboard. 100+ LLMs. Total control, compliance, and insight for your AI stack.</strong></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"/></a>
  <a href="https://github.com/features/actions"><img src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF.svg" alt="CI: GitHub Actions"/></a>
  <a href="https://coveralls.io/"><img src="https://img.shields.io/badge/coverage-unknown-lightgrey.svg" alt="Coverage"/></a></p>
<p align="center">
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-20232a?logo=react&logoColor=61dafb" alt="React"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
</p>

<p align="center">
Integrates with: 
<p align="center"> <a href="https://slack.com/"><img src="https://img.shields.io/badge/Slack-4A154B?logo=slack&logoColor=white" alt="Slack"></a>
  <a href="https://www.microsoft.com/en/microsoft-teams/group-chat-software"><img src="https://img.shields.io/badge/Microsoft%20Teams-6264A7?logo=microsoft-teams&logoColor=white" alt="Microsoft Teams"></a>
  <a href="https://telegram.org/"><img src="https://img.shields.io/badge/Telegram-2CA5E0?logo=telegram&logoColor=white" alt="Telegram"></a>
  <a href="https://www.whatsapp.com/"><img src="https://img.shields.io/badge/WhatsApp-25D366?logo=whatsapp&logoColor=white" alt="WhatsApp"></a>
</p>

<p align="center"><b>Quick highlights</b>: centralized quota & credit management · OpenAI-compatible proxy · real-time analytics · enterprise SSO & audit logging</p>

## Quick Start

1. Install backend dependencies and create a virtualenv:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements/requirements.txt
cp backend/config/.env.example .env
```

2. Run migrations and start the server:

```bash
alembic -c backend/config/alembic.ini upgrade head
uvicorn app.main:app --reload
```

Visit the dashboard at http://localhost:8000 and the API docs at http://localhost:8000/docs

---

## Table of Contents

- [Overview](#overview)
- [What Makes Alfred Unique?](#what-makes-alfred-unique)
- [Business Solutions](#business-solutions)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Platform Architecture](#platform-architecture-end-to-end-ai-governance-flow)
- [Backend](#backend)
- [Frontend](#frontend)
- [DevOps](#devops)
- [Tests](#tests)
- [Canonical Project Structure](#-canonical-project-structure-2026)
- [Get Started](#get-started)
- [License](#-license)
- [Author](#-author)
- [Community & Support](#community--support)
- [Project Review Summary](#-project-review-summary--recommendations-2026)

## Overview

## What Makes Alfred Unique?

Alfred stands apart from other AI governance and proxy solutions by offering:

- **True Multi-Provider Governance:** One platform to manage credits, quotas, and analytics across 100+ LLM providers—no vendor lock-in, no silos.
- **Enterprise-Grade Controls:** Fine-grained quota enforcement, vacation sharing, and priority overrides for teams, projects, and users.
- **Unified API Experience:** OpenAI-compatible endpoints and SDKs for seamless integration—no code rewrites required.
- **Real-Time, Actionable Analytics:** Instant dashboards, leaderboards, and alerts for spend, usage, and compliance—empowering proactive management.
- **Compliance by Design:** Automated audit logging, SSO, and policy enforcement built-in for peace of mind in regulated environments.
- **Extensible & Modular:** Easily integrates with Slack, Teams, Telegram, and more. Add new providers or custom logic with minimal effort.

Alfred is purpose-built for organizations that demand transparency, control, and agility in their AI operations—delivering a single source of truth for all LLM usage.

## Business Solutions

Alfred is trusted by enterprises, startups, and research teams to:

- Govern and optimize AI/LLM usage across teams and projects
- Enforce cost controls and prevent overages with real-time quota management
- Simplify compliance and audit for AI spend and data access
- Provide unified analytics and reporting for all LLM providers
- Accelerate onboarding and integration with OpenAI-compatible APIs

Alfred adapts to a wide range of business needs—from internal R&D to customer-facing AI products—delivering transparency, concd src/backendtrol, and peace of mind.

**Alfred** is an enterprise-grade AI credit governance platform. It acts as a FastAPI proxy, managing token quotas, analytics, and unified authentication for 100+ LLM providers. Alfred empowers organizations to control, monitor, and optimize their AI usage with confidence.

## Security & Protection

Alfred is built with enterprise-grade security and compliance in mind:

- **API Key & JWT Authentication:** Secure access for users, teams, and services
- **SSO Integration:** Enterprise SSO (OAuth, SAML, OIDC) for unified identity
- **Quota & Abuse Protection:** Rate limiting, quota enforcement, and anomaly detection
- **Audit Logging:** Immutable logs for all API activity and quota changes
- **Role-Based Access Control:** Fine-grained permissions for users, teams, and admins
- **Data Encryption:** All sensitive data encrypted at rest and in transit
- **Secret Management:** Environment variables and secret manager integration—no secrets in code
- **Compliance Automation:** Automated checks for usage, spend, and policy violations
- **Vulnerability Scanning:** Automated CI/CD scans for dependencies and containers

## Key Features

- Centralized quota and credit management for all LLM APIs
- Real-time analytics and usage dashboards
- Enterprise SSO and API key management
- OpenAI-compatible API proxy for seamless integration
- Automated compliance, audit logging, and reporting

## How It Works

1. **Request Interception:** All LLM API requests are routed through Alfred's FastAPI gateway.
2. **Quota Enforcement:** The quota manager checks user/team credits and enforces limits.
3. **Provider Proxy:** Requests are forwarded to the target LLM provider (e.g., OpenAI, Anthropic, Azure) via a unified proxy layer.
4. **Ledger Update:** Usage is logged in the ledger for real-time analytics, audit, and reporting.
5. **Dashboard & Alerts:** Admins and users access dashboards, leaderboards, and receive notifications for quota, spend, and compliance events.

## Platform Architecture: End-to-End AI Governance Flow

<p align="center"><b>Every request, every credit, every insight—fully governed, fully visible.</b></p>

```
┌──────────────┐      ┌──────────────────────┐      ┌───────────────┐      ┌────────────┐      ┌───────────────┐
│ 👤 User /    │─────▶│ 🚦 Alfred FastAPI    │─────▶│ 🔒 Quota      │─────▶│ 🤖 LLM     │─────▶│ 🌐 Provider   │
│   Service    │      │     Proxy            │      │    Manager    │      │   Proxy    │      │     API       │
└──────────────┘      └──────────────────────┘      └───────────────┘      └────────────┘      └───────────────┘
                                 │
                                 │
                                 ▼
                      ┌──────────────────────┐
                      │ 📊 Ledger &          │
                      │   Analytics          │
                      └──────────────────────┘
                                 │
                                 ▼
                      ┌──────────────────────┐
                      │ 📈 Dashboard &       │
                      │   Alerts             │
                      └──────────────────────┘
```

Alfred is designed for security, scalability, and extensibility—making it the ideal solution for organizations managing multiple AI providers and strict compliance requirements.

## Backend

Core API and business logic:

- Main FastAPI app: `backend/app/main.py`
- Routers: `backend/app/routers/`
- Analytics: `backend/app/dashboard.py`
- Requirements: `backend/requirements/requirements.txt`
- **Unit Tests:** `tests/unit/`

## Frontend

User dashboard and UI:

- React app: `src/frontend/`
- Source: `src/frontend/src/`
- Public: `src/frontend/public/`
- **Unit Tests:** `src/frontend/src/__tests__/`

## DevOps

Deployment, orchestration, and automation:

- Docker: `devops/merged/docker/`, `docker-tools/`
- K8s: `devops/k8s/`
- Scripts: `devops/scripts/`

## Tests

Automated test coverage:

- **Backend Unit:** `tests/unit/`
- **Frontend Unit:** `src/frontend/src/__tests__/`
- **E2E:** `dev/QA/E2E/`
- **Coverage & Results:** `dev/QA/results/`

---

<hr style="border: 0; height: 2px; background: linear-gradient(90deg, #ff00cc, #00eaff, #39ff14, #fffb00); margin: 24px 0;"/>

# 🗂️ Canonical Project Structure (2026)

| Area           | Canonical Path              |
| -------------- | --------------------------- |
| Backend        | backend/app/                |
| Backend Tests  | tests/unit/                 |
| Frontend       | src/frontend/               |
| Frontend Tests | src/frontend/src/**tests**/ |
| E2E Tests      | dev/QA/E2E/                 |
| DevOps Docker  | devops/merged/docker/       |
| DevOps Scripts | devops/scripts/             |
| Coverage       | dev/QA/results/coverage/    |
| Test Results   | dev/QA/results/             |

All documentation, onboarding, and training materials should reference these canonical locations.
...existing code...

---

### 👤 Project Lead

- Sergey Bar is the sole project lead and approves all changes.

### 🤖 AI Usage Policy

- Any AI-generated code, documentation, or configuration must include a comment specifying:
  - **Model Name**: e.g., GPT-4.1, GPT-5.1-Codex
  - **Logic/Reasoning**: Why the change was made
  - **Root Cause**: What problem it solves
  - **Context**: For future improvements
- Manual edits by Sergey Bar do not require this comment.

### 📝 Contribution Policy

- Only Sergey Bar can approve and merge changes to the main branch.
- External contributions require explicit review and approval.

<hr style="border: 0; height: 2px; background: linear-gradient(90deg, #39ff14, #00eaff, #ff00cc, #fffb00); margin: 24px 0;"/>

## Get Started

### Quick Install

```bash
git clone https://github.com/your-org/alfred.git && cd alfred
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements/requirements.txt
cp backend/config/.env.example .env
```

### Quick Start

```bash
# 1. Configure (add your API keys to .env)
nano .env

# 2. Run migrations
alembic -c backend/config/alembic.ini upgrade head

# 3. Start server
uvicorn app.main:app --reload

# 4. Verify
curl http://localhost:8000/health
```

**Dashboard:** http://localhost:8000 &nbsp;|&nbsp; **API Docs:** http://localhost:8000/docs

<hr style="border: 0; height: 2px; background: linear-gradient(90deg, #ff00cc, #00eaff, #39ff14, #fffb00); margin: 24px 0;"/>

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

**Project & Program Lead:** Sergey Bar

## Community & Support

- [Open an Issue](https://github.com/AlfredDev/alfred/issues)
- [Discussions](https://github.com/AlfredDev/alfred/discussions)
- [Feature Requests](https://github.com/AlfredDev/alfred/issues/new?labels=enhancement)
- [Security Policy](https://github.com/your-org/alfred/security/policy)

---

_Found a bug? Have a feature request? [Open an issue!](https://github.com/AlfredDev/alfred/issues)_

---

_Last reviewed: February 16, 2026_
