# Alfred Architecture

Technical architecture overview for Alfred AI Credit Governance Platform.

## Table of Contents

- [Overview](#overview)
- [Three-Layer Architecture](#three-layer-architecture)
- [Architecture Diagram](#architecture-diagram)
- [The Balancer Logic](#the-balancer-logic)
- [Credit Normalizer](#credit-normalizer)
- [Implementation Approaches](#implementation-approaches)

---

## Overview

Alfred implements a **three-layer architecture** designed for enterprise-grade AI governance:

1. **Proxy Gateway** (The Gatekeeper) - Request interception and quota enforcement
2. **Ledger System** (The Bank) - Credit ownership and transaction tracking
3. **SDK/Authentication** (The Passport) - User identity and key management

---

## Three-Layer Architecture

### Layer 1: Proxy Gateway (The Gatekeeper)

```
User/Application → Alfred Proxy → LLM Provider (OpenAI, Azure, Bedrock, etc.)
```

Instead of calling AI providers directly, applications call Alfred's OpenAI-compatible endpoint. Alfred:

- **Intercepts** requests and counts tokens in the prompt
- **Verifies** user quota before forwarding to the provider
- **Logs** usage and calculates costs in real-time

### Layer 2: Ledger System (The Bank)

```
PostgreSQL/SQLite → Users │ Teams │ Quotas │ Transactions │ Audit Log
```

A database tracks the "ownership" of credits via atomic transactions:

- **User quotas**: Individual credit balances debited on each request
- **Team pools**: Shared budgets for departments/projects
- **Transfer log**: Audit trail for all credit reallocations
- **Real-time sync**: Permissions updated immediately on the Proxy Layer

### Layer 3: SDK/Authentication (The Passport)

```
Alfred API Key (tp-xxx...) → Identifies user → Applies quota rules
```

Enterprise developers use Alfred API keys instead of direct provider keys:

- Single authentication layer for all providers
- Centralized key management (rotate without app changes)
- User identity tied to usage tracking

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  ALFRED                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────────────┐    │
│  │   FastAPI      │───▶│   Quota        │───▶│   LiteLLM Proxy        │    │
│  │   Gateway      │    │   Manager      │    │   (100+ providers)     │    │
│  │   (Layer 1)    │    │   (Layer 2)    │    │                        │    │
│  └────────────────┘    └────────────────┘    └────────────────────────┘    │
│         │                     │                          │                   │
│         │                     │              ┌───────────┴───────────┐      │
│         │                     │              ▼           ▼           ▼      │
│         │                     │        ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│         │                     │        │ OpenAI  │ │ Azure   │ │ AWS     │  │
│         │                     │        │ Claude  │ │ OpenAI  │ │Bedrock  │  │
│         │                     │        │ Gemini  │ │         │ │         │  │
│         │                     │        └─────────┘ └─────────┘ └─────────┘  │
│         │                     │              ▼           ▼           ▼      │
│         │                     │        ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│         │                     │        │  vLLM   │ │   TGI   │ │ Ollama  │  │
│         │                     │        │ (Llama) │ │(Mixtral)│ │ (local) │  │
│         │                     │        └─────────┘ └─────────┘ └─────────┘  │
│         │                     │                                              │
│         ▼                     ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      PostgreSQL / SQLite                               │  │
│  │   Users │ Teams │ Quotas │ Transactions │ Audit │ Leaderboard          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Balancer Logic

When a request comes in, Alfred's quota manager enforces governance in this order:

```
1. Authenticate & Identify User
   └─ Valid API key (tp-xxx)? → Continue
   └─ Invalid → Return 401

2. Estimate Token Cost
   └─ Count prompt tokens + estimated completion
   └─ Calculate cost via Credit Normalizer

3. Personal Quota Available?
   └─ YES → Debit personal quota ✓
   └─ NO  → Continue...

4. Is Priority "Critical"?
   └─ YES → Bypass to Team Pool ✓
   └─ NO  → Continue...

5. Any Team Members on Vacation?
   └─ YES → Use up to 10% of Team Pool ✓
   └─ NO  → Continue...

6. Return 403 Error
   └─ Include "Manager Approval" instructions
   └─ Notify admin via Slack/Teams/etc.
```

### Priority Override

When `X-Priority: critical` header is set, Alfred bypasses personal quota limits and draws from the team pool. This is designed for:

- Production incidents
- Customer escalations
- Time-sensitive deadlines

### Vacation Sharing

When a team member is on vacation, their unused quota is partially released to the team pool. Configuration:

```env
VACATION_SHARE_PERCENTAGE=10.0  # Max 10% of team pool from vacation credits
```

---

## Credit Normalizer

Alfred translates different provider costs into unified **Org-Credits**:

```python
# Formula: 1 USD = 100 Org-Credits
# Example: A $0.002 Azure call = 0.2 credits

Provider Cost → LiteLLM Pricing → USD → Org-Credits
```

### Pricing Table

| Provider | Model | Cost/1K tokens | Org-Credits/1K |
|----------|-------|----------------|----------------|
| OpenAI | GPT-4o | $0.005 | 0.5 |
| OpenAI | GPT-4o-mini | $0.00015 | 0.015 |
| OpenAI | o1 | $0.015 | 1.5 |
| Anthropic | Claude 3.5 Sonnet | $0.003 | 0.3 |
| Anthropic | Claude 3.5 Haiku | $0.00025 | 0.025 |
| Google | Gemini 1.5 Pro | $0.00125 | 0.125 |
| Azure | GPT-4 | $0.03 | 3.0 |
| AWS Bedrock | Claude via Bedrock | $0.008 | 0.8 |
| Self-Hosted | Llama 3.1 (vLLM) | ~$0.0001* | 0.01 |

*Self-hosted costs reflect compute, not API pricing

### Version-Locked Pricing

To prevent "token inflation" when model versions change, Alfred can lock pricing to **capability classes** rather than raw token counts:

```env
VERSION_LOCKED_PRICING_ENABLED=true
CAPABILITY_PRICING_MAP={"frontier_reasoning": 3.0, "standard_chat": 1.0, "fast_inference": 0.5}
```

This ensures departmental budgets aren't affected by provider-side tokenization changes.

---

## Implementation Approaches

Alfred supports multiple deployment strategies depending on enterprise needs:

### 1. SaaS Middleman (Recommended)

Alfred holds all provider API keys centrally and distributes access via internal "Alfred Tokens":

```
Employees → Alfred (tp-xxx keys) → OpenAI/Azure/Bedrock
```

**Pros:**
- Centralized control
- Key rotation without app changes
- Full audit trail

**Best for:** Startups to mid-size enterprises (up to 5,000 users)

### 2. Virtual Quota Approach

No actual tokens transfer between users; Alfred modifies rate limits in real-time:

```
User A: 1000 credits/day → User A on vacation → User A: 100, Team Pool: +900
```

**Pros:**
- Zero-copy efficiency
- Instant reallocation

**Best for:** High-frequency trading environments, real-time systems

### 3. Federated/Multi-Region

For Global 500 enterprises with data residency requirements:

```
US Alfred Instance ←→ EU Alfred Instance ←→ APAC Alfred Instance
         │                    │                      │
    US Azure OpenAI      EU Azure OpenAI        APAC Bedrock
```

**Pros:**
- Data sovereignty compliance
- Regional failover

**Best for:** Financial services, healthcare, government contractors

---

## Data Flow

### Request Flow

```
1. Client sends request to /v1/chat/completions
2. Middleware extracts API key, validates user
3. Quota Manager checks available balance
4. If approved:
   a. Request forwarded to LLM provider via LiteLLM
   b. Response streamed back to client
   c. Token usage calculated
   d. Credits debited from user balance
5. If denied:
   a. Return 429 with suggestion
   b. Send notification to admin (optional)
```

### Async Ledger (Low Latency Mode)

For latency-sensitive applications, Alfred can use soft-limit checking:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Request   │────▶│  Edge Cache │────▶│ LLM Provider│
│             │     │ (soft check)│     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           │ async
                           ▼
                    ┌─────────────┐
                    │   Ledger    │
                    │  (billing)  │
                    └─────────────┘
```

- **Soft check**: User has >0 credits? → Allow
- **Billing**: Debit actual cost after response
- **Throttle**: Mid-stream if balance depleted
- **Result**: 99% of requests feel instantaneous

---

## Project Structure

```
alfred/
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
├── docs/                   # Documentation
├── frontend/               # React admin dashboard
├── tests/                  # Test suite
├── requirements/           # Requirements folder
│   ├── requirements.txt        # Production dependencies
│   └── requirements-dev.txt    # Development dependencies
```

---

*See also: [API Reference](API.md) | [Providers](PROVIDERS.md) | [Deployment](DEPLOYMENT.md)*
