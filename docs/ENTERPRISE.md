# Alfred Enterprise Features

Enterprise-grade features for large-scale AI credit governance.

## Table of Contents

- [Overview](#overview)
- [Enterprise Solutions](#enterprise-solutions)
  - [Liquidity Pool & Rollover](#liquidity-pool--rollover)
  - [Token-aware Guardrails](#token-aware-guardrails)
  - [ROI Attribution](#roi-attribution)
  - [Multi-Cloud Token Conversion](#multi-cloud-token-conversion)
- [Identity Integration](#identity-integration)
  - [Active Directory / LDAP](#active-directory--ldap)
  - [SSO Integration](#sso-integration)
  - [SCIM 2.0 Provisioning](#scim-20-provisioning)
  - [HR System Integration](#hr-system-integration)
- [Project-Based Features](#project-based-features)

---

## Overview

Alfred Enterprise provides advanced features for organizations with:

- 500+ AI users
- Multi-department budgets
- Compliance requirements (SOC2, HIPAA, GDPR)
- Integration with corporate identity systems

---

## Enterprise Solutions

### Liquidity Pool & Rollover

**Problem**: Enterprise budgets operate on monthly cycles. Unused tokens expire, leading to waste.

**Solution**: Company-wide reserve pool where unused credits roll over instead of expiring.

```
End of Month:
┌─────────────────┐     ┌──────────────────────┐
│ User A: 2000    │────▶│   Company Reserve    │
│ unused credits  │     │   (Rollover Pool)    │
└─────────────────┘     └──────────────────────┘
                                   │
Start of Next Month:               ▼
┌─────────────────┐     ┌──────────────────────┐
│ User B requests │◀────│  20% discount on     │
│ from reserve    │     │  reserve requests    │
└─────────────────┘     └──────────────────────┘
```

**Configuration:**
```env
LIQUIDITY_POOL_ENABLED=true
ROLLOVER_ENABLED=true
ROLLOVER_PERCENTAGE=50.0        # 50% of unused credits roll over
RESERVE_REQUEST_DISCOUNT=20.0   # Request from reserve at 20% discount
BILLING_CYCLE_DAY=1             # Monthly reset on 1st
```

**API Endpoints:**
- `GET /v1/liquidity/reserve` - View reserve balance
- `POST /v1/liquidity/request` - Request from reserve
- `POST /v1/admin/liquidity/rollover` - Manual rollover trigger

**Example Use Case:**
- A large enterprise with multiple departments uses the liquidity pool to ensure unused credits are not wasted. At the end of each month, unused credits are rolled over into a reserve pool.

---

### Token-aware Guardrails

**Problem**: Malicious prompts can force massive outputs to drain transferred credits.

**Solution**: Multi-layer protection against token abuse.

```
┌──────────────────────────────────────────────────────┐
│                  Alfred Proxy Layer                   │
├──────────────────────────────────────────────────────┤
│  1. Max-Output-Enforcer                              │
│     └─ Transferred credits → max_tokens = 4096      │
│                                                       │
│  2. Semantic Scrutiny Engine                         │
│     └─ Detect repetitive/nonsensical output          │
│     └─ Kill stream after 3 repetitions               │
│                                                       │
│  3. Anomaly Detection                                │
│     └─ Flag unusual usage patterns (3σ threshold)    │
│     └─ Auto-suspend + alert on "pump and dump"       │
└──────────────────────────────────────────────────────┘
```

**Configuration:**
```env
MAX_OUTPUT_TOKENS_TRANSFERRED=4096
ENABLE_SEMANTIC_SCRUTINY=true
LOOP_DETECTION_THRESHOLD=3
ANOMALY_DETECTION_ENABLED=true
ANOMALY_ALERT_THRESHOLD=3.0
```

**Example Use Case:**
- A team working on sensitive data uses token-aware guardrails to prevent excessive token usage and ensure compliance with security policies.

---

### ROI Attribution

**Problem**: Finance can't track if transferred credits generated value.

**Solution**: Project-linked wallets with metadata tagging.

```json
// Transfer Request
{
  "recipient_email": "engineer@company.com",
  "amount": 5000,
  "project_id": "PROJ-2026-AI-SEARCH",
  "reason": "Search algorithm optimization"
}
```

**Analytics Dashboard:**
```
┌────────────────────────────────────────────────────┐
│  Project: PROJ-2026-AI-SEARCH                      │
│  Credits Used: 47,500                              │
│  GitHub Commits: 127 (via integration)             │
│  Salesforce Leads: 34 (via integration)            │
│  Value-per-Credit: $0.23                           │
└────────────────────────────────────────────────────┘
```

**Configuration:**
```env
# GitHub Integration
GITHUB_TOKEN=ghp_...
GITHUB_ORG=your-company

# Salesforce Integration
SALESFORCE_ENABLED=true
SALESFORCE_INSTANCE_URL=https://company.salesforce.com
SALESFORCE_ACCESS_TOKEN=...
```

---

### Multi-Cloud Token Conversion

**Problem**: Azure tokens ≠ AWS Bedrock tokens ≠ OpenAI tokens.

**Solution**: Universal Token Standard (Alfred Credits).

```
Provider Costs → Alfred Credit Normalizer → Unified Credits

┌─────────────────────────────────────────────────────┐
│              Exchange Rate Table                     │
├───────────────┬────────────┬────────────────────────┤
│ Provider      │ 1K Tokens  │ Alfred Credits         │
├───────────────┼────────────┼────────────────────────┤
│ GPT-4o        │ $0.005     │ 0.5 credits           │
│ Claude 3.5    │ $0.003     │ 0.3 credits           │
│ Azure GPT-4   │ $0.03      │ 3.0 credits           │
│ Bedrock Llama │ $0.00099   │ 0.1 credits           │
│ vLLM (self)   │ ~$0.0001   │ 0.01 credits          │
└───────────────┴────────────┴────────────────────────┘

Formula: 1 USD = 100 Alfred Credits
```

---

## Identity Integration

### Active Directory / LDAP

Sync users and teams from corporate directory automatically.

**Configuration:**
```env
LDAP_ENABLED=true
LDAP_SERVER=ldap://ad.company.com:389
LDAP_BASE_DN=DC=company,DC=com
LDAP_BIND_DN=CN=alfred-svc,OU=ServiceAccounts,DC=company,DC=com
LDAP_BIND_PASSWORD=your-service-password
LDAP_USER_FILTER=(objectClass=user)
LDAP_GROUP_FILTER=(objectClass=group)
LDAP_SYNC_INTERVAL_MINUTES=60
```

**Features:**
- Automatic user provisioning on first login
- Team membership synced from AD groups
- Deactivate Alfred access when AD account disabled
- Custom attribute mapping

**API Endpoint:**
```bash
POST /v1/admin/sync/ldap

Response:
{
  "sync_id": "sync-001",
  "users_created": 12,
  "users_updated": 45,
  "users_deactivated": 3,
  "teams_synced": 8
}
```

---

### SSO Integration

Support for major identity providers.

**Supported Providers:**
- Okta
- Azure AD (Entra ID)
- Google Workspace
- Keycloak
- Any OIDC-compliant provider

**Configuration (Azure AD Example):**
```env
SSO_ENABLED=true
SSO_PROVIDER=azure_ad
SSO_CLIENT_ID=your-client-id
SSO_CLIENT_SECRET=your-client-secret
SSO_ISSUER_URL=https://login.microsoftonline.com/{tenant}/v2.0
SSO_SCOPES=openid profile email
```

**Configuration (Okta Example):**
```env
SSO_ENABLED=true
SSO_PROVIDER=okta
SSO_CLIENT_ID=your-client-id
SSO_CLIENT_SECRET=your-client-secret
SSO_ISSUER_URL=https://your-org.okta.com
```

---

### SCIM 2.0 Provisioning

Automated user lifecycle management from identity providers.

**Configuration:**
```env
SCIM_ENABLED=true
SCIM_BEARER_TOKEN=your-scim-token
```

**Endpoints:**
- `POST /scim/v2/Users` - Create user
- `GET /scim/v2/Users/{id}` - Get user
- `PATCH /scim/v2/Users/{id}` - Update user
- `DELETE /scim/v2/Users/{id}` - Deactivate user
- `POST /scim/v2/Groups` - Create team
- `PATCH /scim/v2/Groups/{id}` - Update team membership

**Custom Schema Extension:**
```json
{
  "urn:alfred:params:scim:schemas:extension:2.0:User": {
    "defaultQuota": 100000,
    "team": "engineering",
    "jobLevel": "senior"
  }
}
```

---

### HR System Integration

Auto-provision quotas based on job level from HRIS.

**Supported Systems:**
- Workday
- SAP SuccessFactors
- HiBob
- BambooHR
- Personio

**Configuration:**
```env
HRIS_ENABLED=true
HRIS_PROVIDER=workday
HRIS_API_URL=https://wd5-impl-services1.workday.com/ccx/service/
HRIS_API_KEY=your-api-key
HRIS_SYNC_INTERVAL_MINUTES=120
```

**Role-Based Quota Allocation:**
```env
RBAC_DEFAULT_QUOTAS={"junior": 50000, "mid": 100000, "senior": 250000, "lead": 500000, "executive": 1000000}
```

| Job Level | Daily Quota | Notes |
|-----------|-------------|-------|
| Junior | 50,000 | Standard limit |
| Mid | 100,000 | 2x junior |
| Senior | 250,000 | 5x junior |
| Lead | 500,000 | 10x junior |
| Executive | 1,000,000 | With approval bypass |

---

## Project-Based Features

### Priority Bursting

When assigned to high-priority Jira tickets, quotas auto-burst:

**Configuration:**
```env
PM_INTEGRATION_ENABLED=true
PM_PROVIDER=jira
PM_API_URL=https://company.atlassian.net
PM_API_TOKEN=your-jira-token
PM_HIGH_PRIORITY_BURST_MULTIPLIER=2.0
```

**Supported PM Tools:**
- Jira
- Asana
- Linear
- Monday.com

**Behavior:**
- User assigned to P0/P1 ticket → Quota multiplied by burst factor
- Automatic reset when ticket resolved
- Audit trail in Alfred dashboard

### Emergency Overdraft

Allow critical work to proceed even when quota depleted:

```env
OVERDRAFT_ENABLED=true
OVERDRAFT_LIMIT_MULTIPLIER=0.1     # 10% of quota as overdraft limit
OVERDRAFT_INTEREST_RATE=1.5        # Repaid from next cycle
```

**Behavior:**
- Automatically approved for P0 incidents
- Requires manager approval for other cases
- "Interest" deducted from next cycle's allocation

---

*See also: [Security](security.md) | [API Reference](api.md) | [Architecture](architecture.md)*
