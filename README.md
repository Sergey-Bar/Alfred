# TokenPool 🎯

**Open Source AI Token Quota Manager**

TokenPool is a FastAPI-based proxy server that manages AI token quotas across an organization. It features team-sharing during vacations, priority-based overrides, privacy modes, and efficiency tracking.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 💡 **An open source project by [Sergey Bar](https://www.linkedin.com/in/sergeybar/)** — Built with AI assistance to optimize resource sharing in organizations.

## ✨ Features

- **🔄 OpenAI-Compatible API**: Drop-in replacement for `/v1/chat/completions`
- **💰 Quota Management**: Personal and team-based token quotas in unified "Org-Credits"
- **🏖️ Vacation Sharing**: Automatically share up to 10% of team pool when members are on vacation
- **🚨 Priority Overrides**: Critical projects can bypass quota limits
- **🔒 Privacy Mode**: `X-Privacy-Mode: strict` header prevents message logging
- **📊 Efficiency Scoring**: Track completion/prompt token ratios with leaderboards
- **💵 Dynamic Pricing**: Unified cost mapping via LiteLLM for 100+ providers
- **✅ Manager Approvals**: Request additional quota with approval workflow
- **🔔 Multi-Platform Notifications**: Slack, Teams, Telegram, WhatsApp alerts

## ⚡ Quick Install

```bash
git clone https://github.com/AiTokenPool/tokenpool.git && cd tokenpool && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp config/.env.example .env
```

> 📚 **New to the project?** See the full [Installation Guide](docs/INSTALL.md) for detailed instructions, prerequisites, and troubleshooting.

## 🚀 Quick Start

### 1. Install & Configure

```bash
# Clone and setup
git clone https://github.com/AiTokenPool/tokenpool.git
cd tokenpool
python -m venv .venv && source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure (add your API keys)
cp config/.env.example .env
```

### 2. Run the Server

```bash
uvicorn app.main:app --reload
```

### 3. Verify

```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0"}
```

**API Docs**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Create a User

```bash
curl -X POST http://localhost:8000/v1/admin/users \
  -H "Content-Type: application/json" \
  -d '{"email": "developer@company.com", "name": "John Developer", "personal_quota": 5000}'
```

Response:
```json
{
  "api_key": "ab-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "message": "Store this API key securely - it cannot be retrieved later"
}
```

### 2. Make a Chat Completion Request

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer ab-xxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

### 3. Enable Privacy Mode

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer ab-xxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "X-Privacy-Mode: strict" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Confidential question..."}]
  }'
```

When `X-Privacy-Mode: strict` is set, only token counts are logged—**not** the messages or responses.

### 4. Set Critical Priority

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer ab-xxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "X-Project-Priority: critical" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Urgent production issue..."}]
  }'
```

### 5. Set Vacation Status

```bash
curl -X PUT "http://localhost:8000/v1/users/me/status?status=on_vacation" \
  -H "Authorization: Bearer ab-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

This enables team members to use up to 10% of the shared pool while you're away.

## 🔔 Notifications

TokenPool can send alerts to multiple platforms:

| Platform | Events Supported |
|----------|-----------------|
| Slack | Quota warnings, approvals, vacation status |
| Microsoft Teams | All events with Adaptive Cards |
| Telegram | All events with rich formatting |
| WhatsApp | All events (requires Business API) |

**Quick Setup (Slack example):**

```env
# Add to your .env file
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00.../B00.../xxx
NOTIFICATIONS_ENABLED=true
```

> 📚 **Full setup instructions**: See [Notifications Guide](docs/NOTIFICATIONS.md) for detailed setup for all platforms.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         TokenPool                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   FastAPI    │───▶│    Quota     │───▶│   LiteLLM    │      │
│  │   Gateway    │    │   Manager    │    │    Proxy     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                    │               │
│         │                   │                    ▼               │
│         │                   │           ┌──────────────┐        │
│         │                   │           │  OpenAI      │        │
│         │                   │           │  Anthropic   │        │
│         │                   │           │  Gemini      │        │
│         │                   │           │  100+ more   │        │
│         │                   │           └──────────────┘        │
│         │                   │                                    │
│         ▼                   ▼                                    │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                    PostgreSQL                         │      │
│  │  Users │ Teams │ Quotas │ Logs │ Leaderboard          │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 The Balancer Logic

When a request comes in, the quota is checked in this order:

```
1. Personal Quota Available?
   └─ YES → Use personal quota ✓
   └─ NO  → Continue...

2. Is Priority "Critical"?
   └─ YES → Bypass to Team Pool ✓
   └─ NO  → Continue...

3. Any Team Members on Vacation?
   └─ YES → Use up to 10% of Team Pool ✓
   └─ NO  → Continue...

4. Return 403 Error
   └─ Include "Manager Approval" instructions
```

## 📊 API Endpoints

### Chat Completions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/chat/completions` | OpenAI-compatible chat completions |

### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/admin/users` | Create new user (returns API key) |
| GET | `/v1/users/me` | Get current user info |
| GET | `/v1/users/me/quota` | Get detailed quota status |
| PUT | `/v1/users/me/status` | Update status (active/vacation) |
| PUT | `/v1/users/me/privacy` | Update default privacy preference |

### Team Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/admin/teams` | Create new team |
| POST | `/v1/admin/teams/{id}/members/{user_id}` | Add user to team |
| GET | `/v1/teams/my-teams` | Get user's teams |

### Approvals
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/approvals` | Request quota increase |
| GET | `/v1/approvals/pending` | List pending requests (admins) |
| POST | `/v1/approvals/{id}/approve` | Approve request |
| POST | `/v1/approvals/{id}/reject` | Reject request |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/leaderboard` | Efficiency leaderboard |
| GET | `/v1/analytics/usage` | Usage analytics |

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone and setup
git clone https://github.com/AiTokenPool/tokenpool.git
cd tokenpool
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with live reload
uvicorn app.main:app --reload
```

### Code Style

We use:
- **Black** for formatting
- **isort** for import sorting
- **mypy** for type checking
- **ruff** for linting

```bash
# Format code
black app/
isort app/

# Type check
mypy app/

# Lint
ruff app/
```

### Pull Request Guidelines

1. **Fork** the repository
2. Create a **feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for new functionality
4. Ensure **all tests pass**: `pytest tests/`
5. **Format your code**: `black . && isort .`
6. **Commit** with descriptive message: `git commit -m "Add amazing feature"`
7. **Push** to your fork: `git push origin feature/amazing-feature`
8. Open a **Pull Request**

### Areas for Contribution

- 🔐 **Authentication**: OAuth2, SAML integration
- 📈 **Analytics**: More detailed usage dashboards
- 🌐 **Streaming**: Server-sent events support
- 📦 **Caching**: Response caching for identical prompts
- 🧪 **Testing**: Increase test coverage
- 📚 **Documentation**: More examples and tutorials
- 🔌 **Integrations**: Discord, Email, PagerDuty notifications

## 📁 Project Structure

```
tokenpool/
├── app/
│   ├── __init__.py         # Package initialization
│   ├── main.py             # FastAPI application & routes
│   ├── models.py           # SQLModel database models
│   ├── logic.py            # Business logic (quota, scoring)
│   ├── config.py           # Pydantic settings configuration
│   ├── middleware.py       # Rate limiting & request context
│   ├── exceptions.py       # Custom exception handlers
│   ├── logging_config.py   # Structured logging setup
│   └── integrations/       # Notification providers
│       ├── slack.py        # Slack webhooks
│       ├── teams.py        # MS Teams webhooks
│       ├── telegram.py     # Telegram Bot API
│       └── whatsapp.py     # WhatsApp Business API
├── alembic/
│   ├── env.py              # Migration environment
│   └── versions/           # Database migrations
├── config/
│   ├── alembic.ini         # Alembic configuration
│   └── .env.example        # Environment variable template
├── docker/
│   ├── Dockerfile          # Container configuration
│   └── docker-compose.yml  # Multi-container setup
├── docs/
│   ├── INSTALL.md          # Detailed installation guide
│   └── NOTIFICATIONS.md    # Notifications setup guide
├── tests/
│   ├── test_api.py         # API endpoint tests
│   ├── test_quota.py       # Quota logic tests
│   ├── test_config.py      # Configuration tests
│   ├── test_middleware.py  # Middleware tests
│   └── conftest.py         # Test fixtures
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md               # This file
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t tokenpool -f docker/Dockerfile .

# Run with docker-compose
cd docker && docker-compose up -d
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Project Lead & Vision:** [![LinkedIn](https://img.shields.io/badge/Sergey_Bar-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sergeybar/)

Built with the assistance of AI as part of a mission to optimize resource sharing in organizations.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with Pydantic
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API

---

**An Open Source Project by [![LinkedIn](https://img.shields.io/badge/Sergey_Bar-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sergeybar/)**

*Found a bug? Have a feature request? [Open an issue!](https://github.com/AiTokenPool/tokenpool/issues)*
# Tokenpool
