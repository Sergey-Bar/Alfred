<p align="center">
  <img src="dev/frontend/sidebar-big.png" alt="Alfred Logo" width="400"/>
</p>

# Alfred 🦇

**Open Source Enterprise AI Credit Governance Platform**

Alfred is a FastAPI-based proxy server that manages AI token quotas across an organization. It provides unified credit governance for 100+ LLM providers including OpenAI, Anthropic, Azure, AWS Bedrock, and self-hosted models.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Key Features

- **🔄 OpenAI-Compatible API** - Drop-in replacement for `/v1/chat/completions`
- **💰 Unified Credit Governance** - Personal and team quotas across all providers
- **🏖️ Vacation Sharing** - Auto-release idle quotas to team pool
- **🚨 Priority Overrides** - Critical projects bypass individual limits
- **🔒 Privacy Mode** - `X-Privacy-Mode: strict` prevents message logging
- **📊 Efficiency Tracking** - Leaderboards and analytics
- **🔐 Enterprise SSO** - LDAP, Okta, Azure AD, SCIM 2.0
- **🏦 Liquidity Pool** - Rollover unused credits instead of expiring
- **🔧 VS Code Extension** - Manage tokens directly from your editor

## 🛠️ Project Governance

### Project Lead
- Sergey Bar is the sole project lead and approves all changes.

### AI Usage Policy
- Any AI-generated code, documentation, or configuration must include a comment specifying:
  - **Model Name**: e.g., GPT-4.1, GPT-5.1-Codex
  - **Logic/Reasoning**: Why the change was made
  - **Root Cause**: What problem it solves
  - **Context**: For future improvements
- Manual edits by Sergey Bar do not require this comment.

### Contribution Policy
- Only Sergey Bar can approve and merge changes to the main branch.
- External contributions require explicit review and approval.

## ⚡ Quick Install

```bash
git clone https://github.com/your-org/alfred.git && cd alfred && python -m venv .venv && source .venv/bin/activate && pip install -r dev/backend/requirements/requirements.txt && cp dev/backend/config/.env.example .env
```

## 🚀 Quick Start

```bash
# 1. Configure (add your API keys to .env)
nano .env

# 2. Run migrations
alembic -c dev/backend/config/alembic.ini upgrade head

# 3. Start server
uvicorn app.main:app --reload

# 4. Verify
curl http://localhost:8000/health
```

**Dashboard**: http://localhost:8000 | **API Docs**: http://localhost:8000/docs

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

**Project Lead:** Sergey Bar

---

*Found a bug? Have a feature request? [Open an issue!](https://github.com/AlfredDev/alfred/issues)*

