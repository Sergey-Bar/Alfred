# Alfred API Reference

Complete API documentation for Alfred AI Credit Governance Platform.

## Table of Contents

- [Authentication](#authentication)
- [Chat Completions](#chat-completions)
- [User Management](#user-management)
- [Team Management](#team-management)
- [Credit Reallocation](#credit-reallocation)
- [Approvals](#approvals)
- [Liquidity Pool](#liquidity-pool)
- [Analytics](#analytics)
- [SCIM Provisioning](#scim-20-provisioning)
- [Admin Operations](#admin-operations)
- [Webhooks](#webhooks)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)

---

## Authentication

All API requests require authentication via API key or JWT token.

### API Key Authentication

```bash
curl -H "Authorization: Bearer tp-xxxxxxxxxxxxx" \
     http://localhost:8000/v1/users/me
```

### SSO/JWT Authentication

For SSO-enabled deployments, obtain a JWT token from your identity provider:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..." \
     http://localhost:8000/v1/users/me
```

---

## Chat Completions

### POST /v1/chat/completions

OpenAI-compatible chat completions endpoint. Drop-in replacement for OpenAI SDK.

**Request:**
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing."}
  ],
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token (API key or JWT) |
| `X-Privacy-Mode` | No | `strict` to disable logging |
| `X-Project-ID` | No | Project ID for cost attribution |
| `X-Priority` | No | `critical` for priority override |

**Response:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1707753600,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing is..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  },
  "alfred_usage": {
    "credits_charged": 0.525,
    "remaining_balance": 45000,
    "cost_usd": 0.00525
  }
}
```

---

## User Management

### POST /v1/admin/users

Create a new user (admin only).

**Request:**
```json
{
  "email": "developer@company.com",
  "name": "John Developer",
  "personal_quota": 100000,
  "team_id": "engineering"
}
```

**Response:**
```json
{
  "id": "user-123",
  "email": "developer@company.com",
  "api_key": "tp-xxxxxxxxxxxxxxxx",
  "personal_quota": 100000
}
```

### GET /v1/users/me

Get current user information and balance.

**Response:**
```json
{
  "id": "user-123",
  "email": "developer@company.com",
  "personal_quota": 100000,
  "used_quota": 45000,
  "remaining": 55000,
  "efficiency_score": 0.82,
  "team": {
    "id": "engineering",
    "name": "Engineering",
    "shared_pool": 500000
  }
}
```

### GET /v1/users/me/quota

Get detailed quota status.

### PUT /v1/users/me/status

Update user status (active/vacation).

**Request:**
```json
{
  "status": "vacation"
}
```

### PUT /v1/users/me/privacy

Update default privacy preference.

### PATCH /v1/admin/users/{user_id}/quota

Update user quota (admin only).

**Request:**
```json
{
  "personal_quota": 150000,
  "reason": "Q1 project allocation increase"
}
```

---

## Team Management

### POST /v1/admin/teams

Create a new team (admin only).

**Request:**
```json
{
  "name": "Data Science",
  "shared_pool": 500000
}
```

### POST /v1/admin/teams/{id}/members/{user_id}

Add user to team (admin only).

### GET /v1/teams/my-teams

Get teams the current user belongs to.

---

## Credit Reallocation

### POST /v1/users/me/transfer

Transfer credits to another user.

**Request:**
```json
{
  "recipient_email": "colleague@company.com",
  "amount": 5000,
  "project_id": "PROJ-2026-Q1-SEARCH",
  "reason": "Search algorithm optimization sprint",
  "notify_recipient": true
}
```

**Response:**
```json
{
  "transfer_id": "txn-456",
  "status": "completed",
  "from": "developer@company.com",
  "to": "colleague@company.com",
  "amount": 5000,
  "project_id": "PROJ-2026-Q1-SEARCH",
  "new_balance": 50000,
  "timestamp": "2026-02-12T10:30:00Z"
}
```

### GET /v1/users/me/transfers

Get transfer history.

**Query Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `limit` | 20 | Max results |
| `direction` | `both` | `incoming`, `outgoing`, or `both` |

**Response:**
```json
{
  "transfers": [
    {
      "id": "txn-456",
      "direction": "outgoing",
      "counterparty": "colleague@company.com",
      "amount": 5000,
      "project_id": "PROJ-2026-Q1-SEARCH",
      "timestamp": "2026-02-12T10:30:00Z"
    }
  ],
  "total": 12,
  "page": 1
}
```

---

## Approvals

### POST /v1/approvals

Request a quota increase.

**Request:**
```json
{
  "amount": 50000,
  "reason": "Sprint deadline requires additional capacity"
}
```

### GET /v1/approvals/pending

List pending approval requests (admin only).

### POST /v1/approvals/{id}/approve

Approve a request (admin only).

### POST /v1/approvals/{id}/reject

Reject a request (admin only).

**Request:**
```json
{
  "reason": "Budget constraints"
}
```

---

## Liquidity Pool

### GET /v1/liquidity/reserve

Get company reserve balance.

**Response:**
```json
{
  "company_reserve": 2500000,
  "available_for_request": 2000000,
  "held_for_rollover": 500000,
  "your_contribution_this_cycle": 15000,
  "discount_rate": 0.20
}
```

### POST /v1/liquidity/request

Request credits from the company reserve.

**Request:**
```json
{
  "amount": 10000,
  "project_id": "PROJ-2026-EMERGENCY",
  "reason": "Production incident response",
  "urgency": "critical"
}
```

**Response:**
```json
{
  "request_id": "liq-789",
  "status": "approved",
  "amount_requested": 10000,
  "amount_received": 10000,
  "discount_applied": 2000,
  "effective_cost": 8000,
  "new_balance": 60000,
  "approval_type": "auto_critical"
}
```

### POST /v1/admin/liquidity/rollover

Trigger manual rollover (admin only).

**Request:**
```json
{
  "dry_run": false,
  "rollover_percentage": 50
}
```

**Response:**
```json
{
  "rollover_id": "roll-2026-02",
  "dry_run": false,
  "credits_rolled_over": 1250000,
  "users_affected": 234,
  "new_reserve_balance": 3750000
}
```

---

## Analytics

### GET /v1/analytics/usage

Get usage analytics.

**Query Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `period` | `30d` | Time period (7d, 30d, 90d) |
| `group_by` | `team` | Grouping (team, user, model) |

**Response:**
```json
{
  "period": {"start": "2026-01-13", "end": "2026-02-12"},
  "total_credits_used": 4500000,
  "total_cost_usd": 45000,
  "by_team": [
    {
      "team": "engineering",
      "credits_used": 2000000,
      "users": 45,
      "avg_efficiency_score": 0.78
    },
    {
      "team": "data_science",
      "credits_used": 1500000,
      "users": 12,
      "avg_efficiency_score": 0.85
    }
  ],
  "by_model": [
    {"model": "gpt-4o", "credits": 2500000, "percentage": 55.5},
    {"model": "claude-3-5-sonnet", "credits": 1200000, "percentage": 26.7}
  ]
}
```

### GET /v1/leaderboard

Get efficiency leaderboard.

**Query Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `period` | `7d` | Time period |
| `limit` | 10 | Max results |

**Response:**
```json
{
  "period": "7d",
  "leaderboard": [
    {
      "rank": 1,
      "user": "alice@company.com",
      "efficiency_score": 0.94,
      "credits_used": 12000,
      "output_quality": "high"
    },
    {
      "rank": 2,
      "user": "bob@company.com",
      "efficiency_score": 0.91,
      "credits_used": 8500,
      "output_quality": "high"
    }
  ]
}
```

---

## SCIM 2.0 Provisioning

For automated user/team provisioning from identity providers.

### POST /scim/v2/Users

Create user via SCIM.

**Request:**
```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName": "newuser@company.com",
  "name": {
    "givenName": "New",
    "familyName": "User"
  },
  "emails": [
    {"value": "newuser@company.com", "primary": true}
  ],
  "urn:alfred:params:scim:schemas:extension:2.0:User": {
    "defaultQuota": 100000,
    "team": "engineering",
    "jobLevel": "senior"
  }
}
```

### POST /scim/v2/Groups

Provision team via SCIM.

**Request:**
```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
  "displayName": "Data Science Team",
  "members": [
    {"value": "user-123"},
    {"value": "user-456"}
  ],
  "urn:alfred:params:scim:schemas:extension:2.0:Group": {
    "sharedPool": 500000,
    "quotaPolicy": "proportional"
  }
}
```

---

## Admin Operations

### POST /v1/admin/sync/ldap

Trigger LDAP sync (admin only).

**Response:**
```json
{
  "sync_id": "sync-001",
  "status": "completed",
  "users_created": 12,
  "users_updated": 45,
  "users_deactivated": 3,
  "teams_synced": 8,
  "duration_ms": 2340
}
```

### POST /v1/admin/sync/hris

Trigger HR system sync (admin only).

---

## Webhooks

### POST /v1/admin/webhooks

Register a webhook endpoint.

**Request:**
```json
{
  "url": "https://your-app.com/alfred-webhook",
  "events": [
    "transfer.completed",
    "quota.depleted",
    "anomaly.detected",
    "approval.pending"
  ],
  "secret": "whsec_xxxxx"
}
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `transfer.completed` | Credit transfer completed |
| `quota.depleted` | User quota exhausted |
| `quota.warning` | User at 80%+ quota |
| `anomaly.detected` | Unusual usage pattern detected |
| `approval.pending` | New approval request |
| `approval.resolved` | Approval approved/rejected |

### Webhook Payload

```json
{
  "event": "quota.depleted",
  "timestamp": "2026-02-12T15:30:00Z",
  "data": {
    "user_id": "user-123",
    "email": "developer@company.com",
    "quota_type": "personal",
    "depleted_at": "2026-02-12T15:29:45Z"
  },
  "signature": "sha256=xxxxx"
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Personal quota exhausted. Request additional credits or use team pool.",
    "details": {
      "current_balance": 0,
      "requested": 1500,
      "suggestion": "Request from liquidity pool"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `QUOTA_EXCEEDED` | 429 | User quota exhausted |
| `TRANSFER_LIMIT` | 400 | Transfer exceeds daily limit |
| `INVALID_PROJECT` | 400 | Project ID not found |
| `MFA_REQUIRED` | 403 | High-value transfer needs MFA |
| `RATE_LIMITED` | 429 | Too many requests |
| `PROVIDER_ERROR` | 502 | Upstream LLM provider error |
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |

---

## Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Chat Completions | 1000/min | Per user |
| Transfers | 20/hour | Per user |
| Admin Operations | 100/min | Per API key |
| SCIM Provisioning | 500/hour | Per tenant |

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1707757200
```

---

## SDK Examples

### Python

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="tp-your-alfred-key"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
    extra_headers={"X-Project-ID": "PROJ-2026-AI"}
)
```

### JavaScript/TypeScript

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'tp-your-alfred-key',
});

const response = await client.chat.completions.create({
  model: 'gpt-4o',
  messages: [{ role: 'user', content: 'Hello!' }],
}, {
  headers: { 'X-Project-ID': 'PROJ-2026-AI' }
});
```

### cURL

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer tp-your-alfred-key" \
  -H "Content-Type: application/json" \
  -H "X-Project-ID: PROJ-2026-AI" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

*See also: [Architecture](ARCHITECTURE.md) | [Enterprise Features](ENTERPRISE.md) | [Security](SECURITY.md)*
