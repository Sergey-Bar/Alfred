# Alfred Security Guide

Security features, guardrails, and compliance information.

## Table of Contents

- [Overview](#overview)
- [Authentication & Authorization](#authentication--authorization)
- [Transfer Security](#transfer-security)
- [Output Guardrails](#output-guardrails)
- [Anomaly Detection](#anomaly-detection)
- [Privacy Features](#privacy-features)
- [Multi-Tenant Security](#multi-tenant-security)
- [Secrets Management](#secrets-management)
- [Audit & Compliance](#audit--compliance)

---

## Overview

Alfred is designed with enterprise security requirements in mind:

- **Defense in Depth**: Multiple layers of security controls
- **Zero Trust**: Every request authenticated and authorized
- **Privacy by Design**: Sensitive data handling built into the architecture
- **Compliance Ready**: SOC2, HIPAA, GDPR-compatible design

---

## Authentication & Authorization

### API Key Authentication

Alfred API keys are prefixed with `tp-` for easy identification:

```bash
Authorization: Bearer tp-xxxxxxxxxxxxxxxx
```

**Key Features:**
- Cryptographically secure random generation
- Per-user key binding
- Automatic invalidation on user deactivation
- Key rotation without application changes

**Configuration:**
```env
API_KEY_PREFIX=tp-
API_KEY_LENGTH=32
```

### SSO/JWT Authentication

For enterprise deployments, Alfred supports JWT tokens from identity providers:

```bash
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

**Supported Providers:**
- Azure AD (Entra ID)
- Okta
- Google Workspace
- Keycloak
- Any OIDC-compliant provider

### Session Tokens (JIT)

Short-lived session tokens for enhanced security:

```env
SESSION_TOKEN_TTL_MINUTES=15
```

- Tokens expire after 15 minutes (configurable)
- Automatic refresh on activity
- Immediate revocation on logout/deactivation

---

## Transfer Security

### MFA for High-Value Transfers

Require additional authentication for large credit transfers:

```env
MFA_REQUIRED_THRESHOLD=10000.0    # Credits
```

When a transfer exceeds this threshold:
1. User prompted for MFA challenge
2. Transfer held pending verification
3. Notification sent to security team

### Transfer Limits

```env
MAX_DAILY_TRANSFER_AMOUNT=100000.0   # Max credits per day
TRANSFER_COOLDOWN_SECONDS=60          # Between transfers to same user
```

### Project ID Requirement

All transfers require a valid project ID for attribution:

```json
{
  "recipient_email": "colleague@company.com",
  "amount": 5000,
  "project_id": "PROJ-2026-AI-SEARCH",  // Required
  "reason": "Sprint deadline"
}
```

---

## Output Guardrails

Protect against prompt injection and token abuse:

### Max Output Enforcement

Limit output tokens when using transferred credits:

```env
MAX_OUTPUT_TOKENS_TRANSFERRED=4096
```

This prevents malicious prompts from generating massive outputs to drain credits.

### Semantic Scrutiny Engine

Detect and terminate abusive patterns:

```env
ENABLE_SEMANTIC_SCRUTINY=true
LOOP_DETECTION_THRESHOLD=3
```

**Detection Patterns:**
- Repetitive output loops
- Nonsensical token sequences
- Unusually long completions

**Behavior:**
- Stream terminated after threshold exceeded
- User notified
- Incident logged for review

### Rate Limiting

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_BURST=20
```

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Chat Completions | 1000/min | Per user |
| Transfers | 20/hour | Per user |
| Admin Operations | 100/min | Per API key |
| SCIM Provisioning | 500/hour | Per tenant |

---

## Anomaly Detection

AI-driven detection of unusual usage patterns:

```env
ANOMALY_DETECTION_ENABLED=true
ANOMALY_ALERT_THRESHOLD=3.0    # Standard deviations
```

### Detection Algorithms

1. **Statistical Analysis**: Flag usage exceeding 3σ from user's baseline
2. **Temporal Patterns**: Unusual time-of-day activity
3. **Behavioral Fingerprinting**: Deviation from established patterns

### Automated Responses

| Anomaly Level | Response |
|---------------|----------|
| Low | Alert to security team |
| Medium | Require re-authentication |
| High | Automatic suspension pending review |

### "Pump and Dump" Detection

Detect patterns of rapid credit accumulation followed by immediate usage:

```
┌─────────────────────────────────────────────────┐
│  User: suspicious@company.com                    │
│                                                  │
│  Pattern Detected:                              │
│  12:00 - Received 50,000 credits from User A    │
│  12:01 - Received 50,000 credits from User B    │
│  12:02 - Used 95,000 credits (single request)   │
│                                                  │
│  ⚠️ ALERT: Potential credit laundering          │
│  Status: Auto-suspended                         │
└─────────────────────────────────────────────────┘
```

---

## Privacy Features

### Privacy Mode

Prevent message logging for sensitive requests:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer tp-xxx" \
  -H "X-Privacy-Mode: strict" \
  -d '{"model": "gpt-4o", "messages": [...]}'
```

When `X-Privacy-Mode: strict`:
- Prompts and responses NOT logged
- Only metadata stored (tokens, cost, timestamp)
- Full audit compliance maintained

### Organization-Wide Privacy

```env
FORCE_STRICT_PRIVACY=false    # Force for all requests
MASK_PII_IN_LOGS=true         # Redact PII in log messages
```

### Data Retention

Configurable retention policies:
- Request metadata: Configurable (default 90 days)
- Full request logs: Never stored in privacy mode
- Audit logs: 7 years for compliance

---

## Multi-Tenant Security

For SaaS deployments, complete data isolation between enterprise clients:

### Isolated Vaulting with TEE

```env
MULTI_TENANT_MODE=true
TEE_PROVIDER=azure_confidential    # Options: azure_confidential, aws_nitro, gcp_confidential
ENCLAVE_ATTESTATION_ENABLED=true
CLIENT_DATA_ISOLATION=strict
```

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                Multi-Tenant Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Client A   │  │  Client B   │  │  Client C   │          │
│  │  (Acme Co)  │  │  (Beta Inc) │  │  (Gamma LLC)│          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌─────────────────────────────────────────────────┐        │
│  │              Alfred Control Plane               │        │
│  │         (routing, rate limiting, billing)       │        │
│  └─────────────────────────────────────────────────┘        │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐            │
│  │  TEE A    │    │  TEE B    │    │  TEE C    │            │
│  │ (SGX/SEV) │    │ (SGX/SEV) │    │ (SGX/SEV) │            │
│  │           │    │           │    │           │            │
│  │ • API Keys│    │ • API Keys│    │ • API Keys│            │
│  │ • Ledger  │    │ • Ledger  │    │ • Ledger  │            │
│  │ • Logs    │    │ • Logs    │    │ • Logs    │            │
│  └───────────┘    └───────────┘    └───────────┘            │
│                                                              │
│  Isolation Guarantees:                                       │
│  ✓ Hardware-enforced memory isolation                       │
│  ✓ Encrypted at rest AND in memory                          │
│  ✓ Alfred operators cannot access client enclaves           │
│  ✓ Attestation reports for compliance audits                │
└─────────────────────────────────────────────────────────────┘
```

---

## Secrets Management

### HashiCorp Vault Integration

```env
VAULT_ENABLED=true
VAULT_ADDR=https://vault.company.com:8200
VAULT_TOKEN=your-vault-token
```

**Managed Secrets:**
- LLM provider API keys
- Database credentials
- SSO client secrets
- SCIM tokens

### Key Rotation

- Automatic rotation support via Vault
- Zero-downtime rotation
- Audit trail for all key changes

---

## Audit & Compliance

### Audit Logging

Every action is logged:

```json
{
  "timestamp": "2026-02-12T10:30:00Z",
  "event": "credit.transfer",
  "actor": "user-123",
  "target": "user-456",
  "details": {
    "amount": 5000,
    "project_id": "PROJ-2026-AI-SEARCH"
  },
  "ip_address": "10.0.0.50",
  "user_agent": "python-requests/2.28.0"
}
```

### Privacy-Preserving Audits

Verify compliance without accessing sensitive data:

```
┌─────────────────────────────────────────────────────────────┐
│ Audit ID: AUD-2026-02-12-001                                │
│                                                              │
│ Audited Entity: Engineering Team                            │
│ Period: Jan 1 - Jan 31, 2026                                │
│                                                              │
│ Findings (ZK-Proofs):                                       │
│ ✓ Total spend within budget allocation                      │
│ ✓ No single user exceeded 150% of average                   │
│ ✓ All transfers had valid project IDs                       │
│ ✗ 3 transfers lacked manager approval (flagged)             │
│                                                              │
│ Note: Individual prompts/responses NOT accessible           │
└─────────────────────────────────────────────────────────────┘
```

### Compliance Standards

Alfred is designed to support:

| Standard | Status | Notes |
|----------|--------|-------|
| SOC 2 Type II | Ready | Audit trail, access controls |
| HIPAA | Ready | PHI handling, BAA support |
| GDPR | Ready | Data residency, right to erasure |
| ISO 27001 | Ready | Security controls framework |
| FedRAMP | Planned | Government cloud deployment |

### Data Residency

For regulated industries:

```env
# Federated deployment for data sovereignty
US_ALFRED_INSTANCE=https://us.alfred.company.com
EU_ALFRED_INSTANCE=https://eu.alfred.company.com
APAC_ALFRED_INSTANCE=https://apac.alfred.company.com
```

---

## Security Best Practices

### Deployment Checklist

- [ ] Use HTTPS in production
- [ ] Configure SSO instead of API keys for users
- [ ] Enable MFA for high-value transfers
- [ ] Set appropriate rate limits
- [ ] Enable anomaly detection
- [ ] Configure audit log retention
- [ ] Use Vault for secrets management
- [ ] Regular security audits

### Environment Hardening

```env
# Production security settings
DEBUG=false
CORS_ORIGINS=["https://your-domain.com"]
FORCE_STRICT_PRIVACY=false
MASK_PII_IN_LOGS=true
SESSION_TOKEN_TTL_MINUTES=15
MFA_REQUIRED_THRESHOLD=10000.0
ANOMALY_DETECTION_ENABLED=true
```

---

*See also: [Enterprise Features](ENTERPRISE.md) | [API Reference](API.md) | [Deployment](DEPLOYMENT.md)*
