# Alfred User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [User Management](#user-management)
5. [Team Management](#team-management)
6. [API Usage](#api-usage)
7. [Credit Reallocation](#credit-reallocation)
8. [Dashboard Features](#dashboard-features)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

Alfred is an enterprise AI Credit Governance Platform that helps B2B organizations manage shared API credit pools. When companies purchase bulk API quotas from OpenAI, Anthropic, Azure, or Google, Alfred provides the missing governance layer: user quotas, team budgets, vacation reallocation, approval workflows, and efficiency tracking.

> **Note**: Alfred requires enterprise/API-level accounts with shared credit pools. Consumer subscriptions ($20/month) cannot be managed.

### Key Features

- **Credit Pool Governance**: Allocate enterprise credits to users and teams
- **Real-time Analytics**: Track usage, costs, and efficiency metrics
- **Budget Reallocation**: Admins can redistribute credits between users
- **Vacation Mode**: Automatically release idle quotas to team pool
- **Priority Overrides**: Emergency bypass for critical projects
- **Privacy Mode**: Prevent logging of sensitive requests
- **Multi-Provider Support**: Works with 100+ LLM providers via LiteLLM

### Supported Providers

| Category | Providers |
|----------|-----------|
| **Public APIs** | OpenAI (GPT-4o, o1), Anthropic (Claude 3.5), Google (Gemini 1.5 Pro) |
| **Enterprise Cloud** | Azure OpenAI, AWS Bedrock, Google Vertex AI |
| **Self-Hosted** | vLLM (Llama 3.1, Mixtral), TGI, Ollama |

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- PostgreSQL (production) or SQLite (development)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/alfred.git
cd alfred
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r dev/backend/requirements/requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example configuration
cp dev/backend/config/.env.example .env

# Edit .env with your settings
# At minimum, add your LLM provider API keys:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

### Step 4: Initialize Database

```bash
# Run database migrations
alembic upgrade head
```

### Step 5: Build Frontend (Optional)

```bash
cd frontend
npm install
npm run build
cd ..
```

### Step 6: Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Installation

```bash
# Build and run with Docker Compose
cd docker
docker-compose up -d
```

---

## Quick Start

### Example Workflow

1. **Log in**: Use your API key to authenticate.
2. **Allocate Credits**: Admins can allocate credits to teams.
3. **Monitor Usage**: Use the dashboard to track usage in real-time.

### Visual Example

![Dashboard Screenshot](../images/dashboard.png)

### 1. Create Your First Admin User

```bash
# Using the seed script
python scripts/seed_data.py

# Or via API (after server is running)
curl -X POST http://localhost:8000/v1/admin/users \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "name": "Admin User", "personal_quota": 10000}'
```

Save the returned API key - it cannot be retrieved later!

### 2. Access the Dashboard

Open your browser and navigate to: `http://localhost:8000/static/`

Enter your API key to log in.

### 3. Create Additional Users

From the dashboard:
1. Click "Manage Users" in the sidebar
2. Click "Add User"
3. Fill in user details
4. Share the generated API key with the user

### 4. Start Using the API

Configure your application to use Alfred as the API endpoint:

```python
from openai import OpenAI

client = OpenAI(
    api_key="tp-your-api-key-here",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## User Management

### Creating Users

Users can be created through the dashboard or API:

**Dashboard:**
1. Navigate to "Manage Users"
2. Click "Add User"
3. Enter name, email, and quota
4. The API key is displayed once - save it securely

**API:**
```bash
curl -X POST http://localhost:8000/v1/admin/users \
  -H "X-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "name": "New User",
    "personal_quota": 5000
  }'
```

### User Status

- **Active**: Normal operation
- **On Vacation**: Shares quota with team members
- **Suspended**: Cannot make API requests

### Modifying Users

```bash
curl -X PUT http://localhost:8000/v1/admin/users/{user_id} \
  -H "X-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "personal_quota": 10000,
    "status": "active"
  }'
```

---

## Team Management

### Creating Teams

Teams allow shared quota pools among members:

**Dashboard:**
1. Navigate to "Manage Teams"
2. Click "Add Team"
3. Set team name and pool quota

**API:**
```bash
curl -X POST http://localhost:8000/v1/admin/teams \
  -H "X-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engineering",
    "description": "Software development team",
    "common_pool": 50000
  }'
```

### Adding Team Members

```bash
curl -X POST http://localhost:8000/v1/admin/teams/{team_id}/members/{user_id}?is_admin=false \
  -H "X-API-Key: your-admin-key"
```

### Team Pool Usage

When a user's personal quota is exhausted, they can draw from their team's shared pool. The pool is shared equally among all active team members.

---

## API Usage

### Making Requests

Alfred is fully compatible with the OpenAI API format:

```python
from openai import OpenAI

client = OpenAI(
    api_key="tp-your-api-key",
    base_url="http://your-alfred-server/v1"
)

# Chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
```

### Supported Models

Alfred supports any model available through LiteLLM, including:
- OpenAI: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- Anthropic: claude-3-opus, claude-3-sonnet, claude-3-haiku
- Google: gemini-pro, gemini-pro-vision
- And 100+ more providers

### Special Headers

| Header | Description | Example |
|--------|-------------|---------|
| `X-Privacy-Mode` | Prevents message logging | `X-Privacy-Mode: strict` |
| `X-Priority` | Priority level for request | `X-Priority: critical` |
| `X-Project-ID` | Associate with project | `X-Project-ID: project-123` |

### Checking Your Quota

```bash
curl http://localhost:8000/v1/users/me/quota \
  -H "Authorization: Bearer tp-your-api-key"
```

Response:
```json
{
  "personal_quota": 10000,
  "used_tokens": 3500,
  "available_quota": 6500,
  "team_pool_available": 15000
}
```

---

## Credit Reallocation

### Reallocating Credits

Admins and authorized users can reallocate credits from their allocated quota to others:

```bash
curl -X POST http://localhost:8000/v1/users/me/transfer \
  -H "Authorization: Bearer tp-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "colleague@company.com",
    "amount": 500,
    "reason": "Project deadline support"
  }'
```

### Reallocation Rules

- Can only reallocate from your allocated quota
- Cannot exceed available balance
- All reallocations are logged for audit compliance
- Recipients receive notifications

---

## Dashboard Features

### Overview

The dashboard home shows:
- Total users and teams
- Token usage statistics
- Cost trends over time
- Model usage breakdown
- Efficiency leaderboard

### User Management

- View all users with quota and usage
- Create, edit, and delete users
- Set vacation status
- Assign admin privileges

### Team Management

- View teams with pool usage
- Create and manage teams
- Add/remove team members
- Monitor team efficiency

### Credit Reallocation

- View reallocation history
- Filter by date, user, or amount
- Export reallocation reports for auditing

### User Guide

Access the built-in user guide from the sidebar for quick reference while using the dashboard.

### Dark Mode

Toggle dark mode from the sidebar for comfortable viewing in low-light conditions.

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./alfred.db` |
| `ENVIRONMENT` | development/production | `production` |
| `DEBUG` | Enable debug mode | `false` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `NOTIFICATIONS_ENABLED` | Enable notifications | `true` |
| `SLACK_WEBHOOK_URL` | Slack webhook for alerts | - |

### Quota Settings

Configure organization-wide settings:

```python
# Default quotas
DEFAULT_PERSONAL_QUOTA = 1000  # tokens
DEFAULT_TEAM_POOL = 10000  # tokens

# Vacation sharing
VACATION_SHARE_PERCENTAGE = 10  # % of team pool

# Priority override limits
CRITICAL_OVERDRAFT_LIMIT = 5000  # max overdraft for critical priority
```

---

## Troubleshooting

### Common Issues

**Cannot log in to dashboard:**
- Ensure your API key is correct (starts with `tp-`)
- Check that the server is running
- Verify the API key hasn't been invalidated

**Quota exceeded errors:**
- Check your quota status: `GET /v1/users/me/quota`
- Request additional quota from your manager
- Consider priority override for critical requests

**Requests timing out:**
- Check your LLM provider API key configuration
- Verify network connectivity to LLM providers
- Check server logs for errors

**Database connection errors:**
- Verify DATABASE_URL is correct
- Ensure database server is running
- Check network/firewall settings

### Getting Help

- Check the [GitHub repository](https://github.com/yourusername/alfred) for issues
- Review server logs: `docker logs alfred-server`
- Contact your system administrator

---

## License

Alfred is open source software licensed under the MIT License.

