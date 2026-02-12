<p align="center">
  <img src="static/Logo.png" alt="Alfred Logo" width="200"/>
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

## ⚡ Quick Install

```bash
git clone https://github.com/your-org/alfred.git && cd alfred && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp config/.env.example .env
```

## 🚀 Quick Start

```bash
# 1. Configure (add your API keys to .env)
nano .env

# 2. Run migrations
alembic -c config/alembic.ini upgrade head

# 3. Start server
uvicorn app.main:app --reload

# 4. Verify
curl http://localhost:8000/health
```

**Dashboard**: http://localhost:8000 | **API Docs**: http://localhost:8000/docs

## 📖 Make a Request

```bash
# Create a user
curl -X POST http://localhost:8000/v1/admin/users \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@company.com", "name": "Developer", "personal_quota": 100000}'

# Use the API key from response
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer tp-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello!"}]}'
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Installation](docs/Install.md) | Detailed setup instructions |
| [API Reference](docs/API.md) | Complete API documentation |
| [Architecture](docs/ARCHITECTURE.md) | System design and data flow |
| [Providers](docs/PROVIDERS.md) | Supported LLM providers |
| [Enterprise](docs/ENTERPRISE.md) | SSO, LDAP, HRIS, Liquidity Pool |
| [Security](docs/SECURITY.md) | Guardrails, auditing, compliance |
| [Deployment](docs/DEPLOYMENT.md) | Docker, Kubernetes, production |
| [Notifications](docs/NOTIFICATIONS.md) | Slack, Teams, Telegram setup |
| [Dashboard](docs/DASHBOARD.md) | Admin UI customization |
| [User Guide](docs/USER_GUIDE.md) | End-user documentation |
| [FAQ](docs/FAQ.md) | Common questions |
| [Roadmap](docs/ROADMAP.md) | Product roadmap |
| [Contributing](docs/CONTRIBUTING.md) | Contribution guidelines |

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         ALFRED                               │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐   ┌────────────┐   ┌────────────────────┐  │
│  │  FastAPI   │──▶│   Quota    │──▶│  LiteLLM Proxy     │  │
│  │  Gateway   │   │  Manager   │   │  (100+ providers)  │  │
│  └────────────┘   └────────────┘   └────────────────────┘  │
│        │                │                    │              │
│        ▼                ▼                    ▼              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PostgreSQL: Users │ Teams │ Quotas │ Transactions  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔌 Supported Providers

| Category | Providers |
|----------|-----------|
| **Public APIs** | OpenAI (GPT-4o, o1), Anthropic (Claude 3.5), Google (Gemini) |
| **Enterprise Cloud** | Azure OpenAI, AWS Bedrock, Google Vertex AI |
| **Self-Hosted** | vLLM (Llama 3.1), TGI (Mixtral), Ollama |

## 🐳 Docker

```bash
cd docker && docker-compose up -d
```

## 🧪 Testing

```bash
pytest tests/ -v --cov=app
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

**Project Lead:** [![LinkedIn](https://img.shields.io/badge/Sergey_Bar-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sergeybar/)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with Pydantic
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API

---

*Found a bug? Have a feature request? [Open an issue!](https://github.com/your-org/alfred/issues)*
