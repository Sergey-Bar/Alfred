# Frequently Asked Questions

Common questions about Alfred AI Credit Governance Platform.

## Table of Contents

- [General](#general)
- [Technical](#technical)
- [Enterprise](#enterprise)
- [Security & Privacy](#security--privacy)
- [Troubleshooting](#troubleshooting)

---

## General

### What is Alfred?

Alfred is an open-source enterprise AI Credit Governance Platform. It helps organizations manage shared AI API credit pools, providing:

- User and team quota management
- Real-time usage tracking
- Credit reallocation between users
- Multi-provider support (OpenAI, Anthropic, Azure, etc.)

### Who is Alfred for?

Alfred is designed for **B2B enterprises** that:
- Have enterprise/API-level AI accounts with shared credit pools
- Need to allocate AI budgets across teams and users
- Require audit trails and governance for AI spend

> **Note**: Consumer subscriptions ($20/month ChatGPT Plus) cannot be managed by Alfred.

### Is Alfred open source?

Yes! Alfred is MIT-licensed and free to use. See [LICENSE](../LICENSE) for details.

---

## Technical

### Q1: How can Alfred manage "Token Inflation" caused by model updates?

**Problem**: A newer version of a model might use more tokens for the same prompt (e.g., GPT-4.5 tokenizes differently than GPT-4).

**Solution: Version-Locked Unit Pricing**

Alfred fixes the "Alfred Credit" cost to the **capability** rather than raw token count, insulating departmental budgets from provider-side backend changes.

```
┌─────────────────────────────────────────────────────────────┐
│                Version-Locked Pricing                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Capability Class: "Frontier Reasoning"                     │
│  ├─ GPT-4 (v1)        → 3.0 credits/1K tokens               │
│  ├─ GPT-4 Turbo (v2)  → 3.0 credits/1K tokens  (same!)     │
│  └─ GPT-4.5 (v3)      → 3.0 credits/1K tokens  (same!)     │
│                                                              │
│  If GPT-4.5 uses 20% more tokens for same prompt:           │
│  ├─ Raw cost increase: +20%                                 │
│  └─ Alfred cost increase: 0% (absorbed by platform)         │
│                                                              │
│  Budget Impact: ZERO                                         │
└─────────────────────────────────────────────────────────────┘
```

**Configuration:**
```env
VERSION_LOCKED_PRICING_ENABLED=true
CAPABILITY_PRICING_MAP={"frontier_reasoning": 3.0, "standard_chat": 1.0}
```

---

### Q2: How can we implement "Token-Aware Caching" to save costs?

**Problem**: Multiple employees asking the same question (e.g., "Summarize the Q3 Earnings Report") results in redundant API calls.

**Solution: Semantic Global Cache**

Alfred maintains a semantic similarity cache. If two employees ask semantically equivalent questions, Alfred returns the cached result, charging the second user 0 credits (or a small "Access Fee").

```
┌─────────────────────────────────────────────────────────────┐
│                  Semantic Cache Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User A: "Summarize Q3 earnings"                            │
│  └─ Cache MISS → LLM call → 2,500 tokens → 7.5 credits     │
│                                                              │
│  User B: "Give me a summary of Q3 earnings report"          │
│  └─ Semantic similarity: 94% (threshold: 90%)               │
│  └─ Cache HIT → Return cached response → 0 credits          │
│                                                              │
│  User C: "What were Q3 profits?"                            │
│  └─ Semantic similarity: 72% (below threshold)              │
│  └─ Cache MISS → LLM call → 1,800 tokens → 5.4 credits     │
│                                                              │
│  Monthly Savings: ~30% on enterprise knowledge queries      │
└─────────────────────────────────────────────────────────────┘
```

**Configuration:**
```env
SEMANTIC_CACHE_ENABLED=true
SEMANTIC_CACHE_SIMILARITY_THRESHOLD=0.90
SEMANTIC_CACHE_TTL_HOURS=24
CACHE_ACCESS_FEE_CREDITS=0.1
```

---

### How does Alfred calculate costs?

Alfred uses a **Credit Normalizer** that converts all provider costs to unified "Org-Credits":

```
Formula: 1 USD = 100 Org-Credits
Example: A $0.002 API call = 0.2 credits
```

This allows unified budgeting across OpenAI, Anthropic, Azure, and self-hosted models.

### Can I use Alfred with self-hosted models?

Yes! Alfred supports:
- **vLLM** - High-performance inference server
- **TGI** - HuggingFace Text Generation Inference
- **Ollama** - Easy local deployment

```env
VLLM_API_BASE=http://gpu-server:8000/v1
OLLAMA_API_BASE=http://localhost:11434
```

---

## Enterprise

### Q3: How do we handle "Multi-Tenant Security" for SaaS deployment?

**Problem**: If Alfred is deployed as SaaS rather than on-premise, how do we ensure complete data isolation between enterprise clients?

**Solution: Isolated Vaulting with TEE**

Each enterprise client gets a dedicated, hardware-isolated encryption enclave (Trusted Execution Environment) where their API keys and ledger records are stored. This ensures Alfred (the provider) can **never** access client data.

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

**Configuration:**
```env
MULTI_TENANT_MODE=true
TEE_PROVIDER=azure_confidential
ENCLAVE_ATTESTATION_ENABLED=true
CLIENT_DATA_ISOLATION=strict
```

---

### Can Alfred integrate with our HR system?

Yes! Alfred supports automatic user provisioning based on job level:

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
RBAC_DEFAULT_QUOTAS={"junior": 50000, "mid": 100000, "senior": 250000}
```

### Does Alfred support SSO?

Yes! Alfred integrates with:
- Azure AD (Entra ID)
- Okta
- Google Workspace
- Keycloak
- Any OIDC-compliant provider

---

## Security & Privacy

### Is my data secure?

Alfred is designed with enterprise security in mind:

- **API keys** are stored securely (optionally in HashiCorp Vault)
- **Privacy Mode** prevents logging of sensitive requests
- **Audit trails** for all actions
- **MFA** for high-value transfers
- **TEE isolation** for multi-tenant deployments

### Can I prevent message logging?

Yes! Use the `X-Privacy-Mode: strict` header:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer tp-xxx" \
  -H "X-Privacy-Mode: strict" \
  -d '{"model": "gpt-4o", "messages": [...]}'
```

Or enable org-wide:
```env
FORCE_STRICT_PRIVACY=true
```

### What compliance standards does Alfred support?

Alfred is designed to support:
- SOC 2 Type II
- HIPAA
- GDPR
- ISO 27001

---

## Troubleshooting

### API requests are failing with 429 errors

This means you've hit a rate limit or quota limit:

1. **Rate limit**: Too many requests per minute
   - Solution: Implement backoff/retry logic

2. **Quota limit**: Credit balance exhausted
   - Solution: Request more credits from team pool or admin

### How do I rotate API keys?

1. Generate new key in admin dashboard
2. Update applications with new key
3. Revoke old key

The old key remains valid until explicitly revoked, allowing zero-downtime rotation.

### LDAP sync isn't working

Check:
1. `LDAP_ENABLED=true`
2. `LDAP_SERVER` URL is accessible from Alfred server
3. `LDAP_BIND_DN` and `LDAP_BIND_PASSWORD` are correct
4. `LDAP_USER_FILTER` matches your AD schema

Test manually:
```bash
ldapsearch -x -H ldap://ad.company.com:389 \
  -D "CN=alfred-svc,OU=ServiceAccounts,DC=company,DC=com" \
  -w "password" \
  -b "DC=company,DC=com" \
  "(objectClass=user)"
```

### Dashboard shows no data

1. Ensure the backend is running: `curl http://localhost:8000/health`
2. Check frontend is built: `cd frontend && npm run build`
3. Verify database migrations ran: `alembic -c config/alembic.ini upgrade head`

---

## Still need help?

- 📖 **Documentation**: [docs/](.)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-org/alfred/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/your-org/alfred/discussions)
- 👤 **Author**: [Sergey Bar](https://www.linkedin.com/in/sergeybar/)

---

*See also: [User Guide](USER_GUIDE.md) | [API Reference](API.md) | [Security](SECURITY.md)*
