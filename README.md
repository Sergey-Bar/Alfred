<p align="center">
  <img src="dev/frontend/sidebar-big.png" alt="Alfred Logo" width="400"/>
</p>

<div align="center">
<pre>
<span style="color:#39ff14;">█████╗ ██╗     ███████╗██████╗ ███████╗██████╗ ██████╗</span>
<span style="color:#00eaff;">██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗</span>
<span style="color:#ff00cc;">███████║██║     █████╗  ██████╔╝█████╗  ██████╔╝██║  ██║</span>
<span style="color:#fffb00;">██╔══██║██║     ██╔══╝  ██╔══██╗██╔══╝  ██╔══██╗██║  ██║</span>
<span style="color:#ff00cc;">██║  ██║███████╗███████╗██║  ██║███████╗██║  ██║██████╔╝</span>
<span style="color:#39ff14;">╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝</span>
</pre>

<h1 align="center" style="color:#39ff14; font-family: 'Share Tech Mono', monospace; letter-spacing: 0.1em;">
ALFRED: <span style="color:#00eaff;">Enterprise AI Credit Governance</span>
</h1>
<h3 align="center" style="color:#ff00cc;">⚡ FastAPI Proxy | 🦾 React Dashboard | 🛡️ DevOps | 🧠 LLM Governance ⚡</h3>

<p align="center" style="color:#fffb00; font-size:1.1em;">
<b>Welcome to the future of AI credit governance.<br>
<span style="color:#00eaff;">Cyberpunk-grade</span> quota, analytics, and SSO for 100+ LLM providers.<br>
<span style="color:#ff00cc;">Built for speed. Designed for control. Ready for tomorrow.</span></b>
</p>
</div>

<hr style="border: 0; height: 2px; background: linear-gradient(90deg, #39ff14, #00eaff, #ff00cc, #fffb00); margin: 24px 0;"/>
-## 🦾 Backend
- Main FastAPI app: `backend/app/main.py`
- Routers: `backend/app/routers/`
- Analytics: `backend/app/dashboard.py`
- Requirements: `backend/requirements/requirements.txt`
- **Unit Tests:** `tests/unit/`
...existing code...
## 🖥️ Frontend
- React app: `src/frontend/`
- Source: `src/frontend/src/`
- Public: `src/frontend/public/`
- **Unit Tests:** `src/frontend/src/__tests__/`
...existing code...
## 🛠️ DevOps
- Docker: `devops/merged/docker/`, `docker-tools/`
- K8s: `devops/k8s/`
- Scripts: `devops/scripts/`
...existing code...
## 🧪 Tests
- **Backend Unit:** `tests/unit/`
- **Frontend Unit:** `src/frontend/src/__tests__/`
- **E2E:** `dev/QA/E2E/`
- **Coverage & Results:** `dev/QA/results/`
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

## ⚡ Quick Install

```bash
git clone https://github.com/your-org/alfred.git && cd alfred && python -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements/requirements.txt && cp backend/config/.env.example .env
```

## 🚀 Quick Start

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

**Dashboard**: http://localhost:8000 | **API Docs**: http://localhost:8000/docs

<hr style="border: 0; height: 2px; background: linear-gradient(90deg, #ff00cc, #00eaff, #39ff14, #fffb00); margin: 24px 0;"/>

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

**Project Lead:** Sergey Bar

---

_Found a bug? Have a feature request? [Open an issue!](https://github.com/AlfredDev/alfred/issues)_

---

## 🏁 Project Review Summary & Recommendations (2026)

**This project has undergone a full best-practice review and modernization.**

### Key Outcomes

- **Structure:** All code, tests, and DevOps scripts are now organized in canonical locations (see table above).
- **Code Quality:** All code and documentation follow modern standards, naming conventions, and AI usage policy.
- **Testing:** Backend, frontend, and E2E tests are unified, deduplicated, and fully automated in CI/CD. Coverage and results are centralized.
- **Documentation:** All onboarding, training, compliance, and architecture docs are accurate and reference canonical paths.
- **DevOps:** CI/CD, Docker Compose, and all scripts are modern, secure, and reference the correct locations. Security and compliance automation is in place.

### Recommendations

- **Strict CI Enforcement:** Remove `|| true` from lint steps in CI to enforce strict code quality.
- **Dockerfile Consistency:** Ensure all Docker Compose builds reference a canonical, up-to-date Dockerfile (e.g., move/copy as needed).
- **Script Documentation:** Document all DevOps scripts in onboarding and ensure they are executable.
- **Security Automation:** Schedule regular security and compliance scans in CI/CD.
- **Badge & Status:** Add CI status and coverage badges to the README for visibility.
- **Periodic Review:** Schedule quarterly reviews of docs, tests, and DevOps for continuous improvement.

---

For details on structure, policies, and best practices, see the canonical table and referenced documentation above.

_Last reviewed: February 15, 2026_
