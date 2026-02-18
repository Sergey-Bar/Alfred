# AI Orchestrator — Master Product Requirements Document

**The Enterprise AI Control & Economy Platform**

| Field | Value |
|-------|-------|
| Version | 3.0 — Master Edition |
| Status | Investor / Executive / Engineering Review |
| Owner | Product & Architecture |
| Date | February 2026 |
| Classification | Confidential |
| Document Type | Living PRD — updated each sprint |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Market Problem](#2-market-problem)
3. [Market Opportunity](#3-market-opportunity)
4. [Target Market & ICP](#4-target-market--icp)
5. [Competitive Landscape](#5-competitive-landscape)
6. [Product Vision](#6-product-vision)
7. [Product Architecture](#7-product-architecture)
8. [Core Product Capabilities](#8-core-product-capabilities)
9. [User Stories & Acceptance Criteria](#9-user-stories--acceptance-criteria)
10. [API Contract](#10-api-contract)
11. [Data Models & Schemas](#11-data-models--schemas)
12. [Error Handling & Edge Cases](#12-error-handling--edge-cases)
13. [Integration Catalog](#13-integration-catalog)
14. [Security & Compliance Posture](#14-security--compliance-posture)
15. [Infrastructure & Deployment](#15-infrastructure--deployment)
16. [Technical Module Breakdown](#16-technical-module-breakdown)
17. [Customer Journey & Onboarding](#17-customer-journey--onboarding)
18. [Go-To-Market Strategy](#18-go-to-market-strategy)
19. [Pricing & Business Model](#19-pricing--business-model)
20. [Competitive Differentiation](#20-competitive-differentiation)
21. [Success Metrics & KPIs](#21-success-metrics--kpis)
22. [Roadmap](#22-roadmap)
23. [Pilot & Beta Program](#23-pilot--beta-program)
24. [Risks & Mitigation](#24-risks--mitigation)
25. [Moat Strategy & Defensibility](#25-moat-strategy--defensibility)
26. [SLA Definitions & Breach Remediation](#26-sla-definitions--breach-remediation)
27. [Billing Reconciliation & Metering Accuracy](#27-billing-reconciliation--metering-accuracy)
28. [Support Tiers & Customer Success](#28-support-tiers--customer-success)
29. [Partner & Reseller Ecosystem](#29-partner--reseller-ecosystem)
30. [Open Source Strategy](#30-open-source-strategy)
31. [Team, Hiring & Execution Risk](#31-team-hiring--execution-risk)
32. [Long-Term Vision](#32-long-term-vision)
33. [Assumptions Log](#33-assumptions-log)
34. [Out of Scope](#34-out-of-scope-this-phase)
35. [Glossary](#35-glossary)

---

## 1. Executive Summary

AI Orchestrator is the enterprise AI control plane — providing unified governance, cost intelligence, and intelligent orchestration across all LLM providers. As organizations embed AI into every workflow, they require financial control, security enforcement, performance optimization, vendor independence, and measurable ROI. AI Orchestrator delivers all of this through a single programmable infrastructure layer.

> **North Star Metric:** Total AI Spend Managed Through Platform — measures adoption, trust, platform centrality, and drives revenue simultaneously.

> **Secondary Metric:** % of Customer AI Spend Optimized (cost savings delivered)

### Core Value Proposition

| Category | Impact | Mechanism |
|----------|--------|-----------|
| Cost Optimization | 25–60% reduction in token spend | Smart routing + semantic caching |
| Security | Centralized AI traffic enforcement | Firewall middleware + audit logs |
| Governance | Real-time budget control | Wallet system + policy engine |
| Resilience | Zero downtime on provider failure | Automatic multi-provider failover |
| ROI Visibility | Feature-level AI cost attribution | Usage classification + analytics |
| Developer Experience | Cost-aware AI workflows | IDE extensions + Slack integration |
| Compliance | Audit-ready AI operations | Immutable logs + policy enforcement |
| Vendor Freedom | No single-provider dependency | Multi-provider abstraction layer |

### One-Line Pitch
> "Reduce your AI spend by 30% in 7 days — without changing a single line of application code."

---

## 2. Market Problem

Enterprise AI adoption is accelerating rapidly, but governance maturity has not kept pace. Organizations are embedding LLMs into core workflows without the infrastructure to control, govern, or optimize that consumption. This creates five compounding problems:

### 1. Financial Chaos
- Unpredictable token consumption with no cost attribution per team, feature, or product line
- End-of-month bill shock from unchecked premium model overuse
- No mechanism to enforce budgets or trigger alerts before overspend occurs
- Finance teams cannot forecast or chargeback AI costs to business units
- Overuse of GPT-4 / Claude Opus for tasks that GPT-3.5 / Haiku could handle at 1/10th the cost

### 2. Security & Compliance Risk
- API key sprawl — each team manages its own keys with no central revocation
- Sensitive data, PII, and trade secrets transmitted in LLM prompts without detection
- Shadow AI — employees using personal API keys outside corporate governance
- No centralized audit trail for regulatory or legal discovery requirements
- No data residency enforcement — prompts may leave approved geographic regions

### 3. Vendor Lock-in
- Hard-coded SDK integrations make provider switching a multi-sprint engineering project
- No resilience when a single provider degrades, rate-limits, or changes pricing
- Limited negotiating leverage with providers when spend is fragmented
- Model-specific prompt engineering creates hidden migration costs

### 4. Zero ROI Visibility
- No link between AI spend and business value — revenue, conversion, or productivity
- No model performance benchmarking across providers for the same tasks
- No per-feature or per-product cost attribution
- Engineering and product teams cannot justify AI infrastructure investment to CFOs

### 5. Developer Friction
- Manual quota enforcement requires platform team intervention for every limit change
- Developers have no real-time cost feedback during development
- No intelligent guidance on which model to use for a given task type
- Switching providers requires SDK changes, testing, and redeployment

---

## 3. Market Opportunity

### Key Market Trends
- LLM usage expanding from pilots into mission-critical production workflows
- Multi-model strategies becoming standard — organizations use 3–5 providers on average
- CFO and FinOps teams taking direct ownership of AI spend approval cycles
- Compliance and data residency requirements becoming contractual obligations
- Enterprise AI infrastructure becoming a permanent, growing budget line item
- AI agent frameworks (LangGraph, AutoGen, CrewAI) multiplying token consumption 10–100x
- Regulatory pressure (EU AI Act, NIST AI RMF) requiring documented AI governance

### Market Sizing

| Segment | Definition | Estimated Size |
|---------|------------|----------------|
| TAM | Global enterprise AI API + model spend | $50B+ growing 40% YoY |
| SAM | Enterprises spending $20K–$500K/month on AI APIs | $8–12B addressable |
| SOM | Multi-provider enterprises with centralized platform teams | $1–2B near-term target |

> **Note:** Refine with primary research before Series A. Enterprise AI infra spend is projected to reach $200B+ by 2028 (directional, cross-referenced from Gartner, a16z, and IDC trend reports).

### Why Now
- LLM cost has become a P&L line item — CFOs are now asking questions
- Provider pricing is increasingly volatile — arbitrage is newly valuable
- The EU AI Act creates audit and governance obligations starting 2025–2026
- AI agent frameworks have caused a 10–50x increase in token consumption overnight for early adopters
- No dominant player has claimed the "AI FinOps" category yet

---

## 4. Target Market & ICP

### Primary ICP

Mid-to-large enterprises (200–5,000 employees) that:
- Spend $20K–$500K/month on AI APIs
- Use or plan to use multiple LLM providers
- Have had at least one "bill shock" moment from unexpected AI spend
- Require compliance readiness (SOC 2, GDPR, ISO 27001, HIPAA)
- Have a centralized platform, infrastructure, or FinOps team

### Buyer Personas

| Persona | Primary Pain | Trigger Event | What They Buy | Success Metric |
|---------|-------------|---------------|---------------|----------------|
| CTO / VP Engineering | Vendor risk, reliability, dev velocity | Provider outage or pricing spike | Resilience, routing, multi-provider abstraction | Zero downtime from provider failure |
| Head of Platform / FinOps | Cost chaos, no chargeback mechanism | Finance asks for AI cost breakdown | Wallet controls, dashboards, chargeback export | Cost per team visible within 24h |
| Security / Compliance Lead | Audit gaps, data leakage, shadow AI | Security incident or compliance audit | Firewall middleware, audit logs, SSO/SCIM | Zero unlogged AI requests |
| CFO / VP Finance | Unpredictable AI budget | AI spend exceeds approved budget | Budget forecasting, spend controls, ROI engine | AI budget variance <5% |
| Staff Engineer / Tech Lead | Integration complexity, switching cost | New provider evaluation | OpenAI-compatible API, provider abstraction | One-hour integration |
| Head of Product | No feature-level AI cost data | Pricing review for AI features | Usage classification, ROI scoring | Cost per feature tracked |

### Secondary ICP

AI-first SaaS companies (Series A–C) facing:
- Margin pressure from LLM costs eating into gross margin (target: AI infra <10% of ARR)
- Need for infrastructure abstraction to avoid provider-specific engineering debt
- Multi-cloud AI strategy for enterprise customer compliance requirements

### Anti-ICP (Do Not Sell To)
- Companies spending <$5K/month on AI (economics don't justify platform overhead)
- Purely consumer-facing apps with no enterprise compliance requirements
- Single-model, single-use-case deployments with no intent to expand

---

## 5. Competitive Landscape

AI Orchestrator operates in a new category: **Enterprise AI Financial Control + Orchestration Infrastructure**.

### Competitor Map

| Competitor | Category | Strengths | Key Weakness | Our Wedge |
|------------|----------|-----------|--------------|-----------|
| OpenAI Org Controls | Provider-native | Deep OpenAI integration | Single-provider only, no financial orchestration | Multi-provider + wallet economy |
| Anthropic Console | Provider-native | Claude-specific governance | Single-provider only | Same as above |
| Helicone | LLMOps / Observability | Easy setup, good logging | Monitor-only, no enforcement or budget control | We enforce, not just observe |
| LangSmith | LLMOps / Tracing | LangChain ecosystem integration | No budget control, no multi-provider routing | Financial control layer |
| Humanloop | Prompt management | Prompt versioning, evals | No cost governance, no traffic control | Full control plane |
| Portkey | AI Gateway | Routing + fallbacks | Limited financial governance depth | Wallet + economy engine |
| Kong AI Gateway | API Gateway | Enterprise API management | No LLM-native semantics or token economy | LLM-first design |
| AWS API Gateway | Cloud-native | AWS ecosystem integration | No AI-specific features | Provider-agnostic |
| Weights & Biases | ML Platform | Experiment tracking, evals | No cost control or traffic management | Complementary (integrate don't compete) |
| Datadog LLM Obs | Observability | Existing enterprise relationships | Observability-only, no control plane | Control + observe together |
| Scale AI | Data + Evals | Quality evaluation | No infra control, expensive | Integrate as eval partner |

### Category Definition

**You are NOT:**
- A logging tool
- An observability platform
- Just an API proxy
- A prompt engineering tool
- A model hosting platform

**You ARE:**
> **Enterprise AI Financial Control + Orchestration Infrastructure** — the programmable layer between applications and LLM providers that governs cost, enforces policy, optimizes routing, and measures ROI.

---

## 6. Product Vision

### Mission
To become the operating system for enterprise AI consumption — providing governance, cost intelligence, and intelligent orchestration across all LLM providers.

### Four Platform Roles

| Role | What It Means | Value |
|------|--------------|-------|
| AI Financial Control Layer | Enforce budgets, track spend, forecast, chargeback | CFO confidence in AI investment |
| Enterprise AI Governance Firewall | Policy enforcement, PII protection, audit trails | Security team approval |
| Multi-Provider LLM Traffic Controller | Smart routing, failover, caching | Engineering resilience + cost reduction |
| Internal AI Economy Engine | Wallet system, credit marketplace, chargeback | Organizational AI resource management |

### 3-Year Product Evolution

```
Year 1: AI Cost Control & Gateway
  → Centralize traffic, enforce budgets, achieve 30%+ savings

Year 2: AI Intelligence Layer
  → Optimize quality, predict spend, govern policy at scale

Year 3: Enterprise AI Operating System
  → Become the standard infrastructure layer for enterprise AI
```

---

## 7. Product Architecture

### High-Level Traffic Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                            │
│  IDE Extension │ App Backend │ Slack Bot │ Agent Framework  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / OpenAI-compatible API
┌──────────────────────────▼──────────────────────────────────┐
│                    AI GATEWAY (Go)                          │
│  Auth → Rate Limit → Request Tracing → SSE Streaming        │
└──────────────────────────┬──────────────────────────────────┘
                           │ gRPC
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌────────▼───────┐  ┌───────▼──────┐
│  SECURITY    │  │ ORCHESTRATION  │  │   METERING   │
│  MIDDLEWARE  │  │    ENGINE      │  │    ENGINE    │
│  (OPA/Go)   │  │    (Go)        │  │    (Go)      │
└───────┬──────┘  └────────┬───────┘  └───────┬──────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  PROVIDER CONNECTORS                        │
│  OpenAI │ Anthropic │ Gemini │ Cohere │ Mistral │ Self-Host  │
└─────────────────────────────────────────────────────────────┘

SUPPORTING SERVICES:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   WALLET &   │  │  ANALYTICS   │  │    ADMIN     │
│  ECONOMY     │  │     DB       │  │  DASHBOARD   │
│  (Postgres)  │  │ (ClickHouse) │  │ (Next.js)    │
└──────────────┘  └──────────────┘  └──────────────┘
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   SEMANTIC   │  │    VAULT     │  │   CACHE /    │
│    CACHE     │  │  (Provider   │  │  RATE LIMIT  │
│ (Vector DB)  │  │    Keys)     │  │   (Redis)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Technology Stack

| Layer | Technology | Version Target | Rationale |
|-------|------------|----------------|-----------|
| Gateway | Go | 1.22+ | Sub-150ms P95; excellent concurrency; horizontal scale |
| Performance Modules | Rust | 1.75+ | Optional; tokenizer, similarity engine |
| Internal Comms | gRPC + Protobuf | Latest stable | Low-latency service-to-service |
| Orchestration | Go | 1.22+ | Policy evaluation speed |
| Analytics | ClickHouse | 24.x | High-throughput append-only; columnar query |
| Wallets & Config | PostgreSQL | 16+ | ACID-compliant financial transactions |
| Cache & Rate Limiting | Redis | 7.x | Sub-ms reads; Lua scripting for atomic ops |
| Semantic Cache | Pinecone or Redis Vector | Latest | Similarity-based deduplication |
| Secret Management | HashiCorp Vault | 1.15+ | Provider key rotation + BYOK |
| Policy Engine | OPA (Open Policy Agent) | 0.60+ | Rego policy language; hot reload |
| Container Orchestration | Kubernetes | 1.28+ | Auto-scaling; rolling deploys |
| Service Mesh | Istio or Linkerd | Latest stable | mTLS between services; traffic management |
| Frontend | Next.js + TypeScript | 14+ | Dashboard + admin UI |
| API Layer | REST + GraphQL | — | REST for gateway; GraphQL for analytics queries |
| Message Queue | NATS or Kafka | Latest | Async event processing; audit log fanout |
| CDN / Edge | Cloudflare Workers | — | Optional: edge rate limiting; global distribution |

### Multi-Tenancy Model

```
Organization (top-level tenant)
  ├── Isolated namespace in Kubernetes
  ├── Dedicated Postgres schema or database
  ├── Scoped Redis keyspace
  ├── Separate Vault path for secrets
  └── Scoped ClickHouse partition
```

**Isolation guarantees:**
- No cross-tenant data access at the application or database layer
- Tenant-specific encryption keys (BYOK supported)
- Audit logs are tenant-scoped and immutable
- Rate limits enforced per tenant namespace

---

## 8. Core Product Capabilities

### 8.1 Unified AI Gateway

A single OpenAI-compatible endpoint for all enterprise AI traffic — requiring **zero code changes** from application teams beyond swapping the base URL.

```
Before: https://api.openai.com/v1
After:  https://gateway.yourcompany.ai/v1
```

| Capability | Detail | Status |
|------------|--------|--------|
| OpenAI API Compatibility | 100% schema parity: chat, completions, embeddings, images, audio, fine-tuning endpoints | MVP |
| Streaming (SSE) | Server-sent events pass-through with token counting mid-stream | MVP |
| Function Calling | Full tool use and function calling support across providers | MVP |
| Embeddings | Multi-provider embedding normalization | MVP |
| JSON Mode | Enforced structured output across providers that support it | Phase 2 |
| Vision / Multimodal | Image inputs for GPT-4V, Claude 3, Gemini Pro Vision | Phase 2 |
| Audio | Whisper-compatible transcription endpoint | Phase 3 |
| Multi-Provider Abstraction | Normalize request/response schema across 10+ providers | MVP |
| Authentication | API key + JWT; OAuth 2.0 for enterprise SSO flows | MVP |
| Performance | <150ms P95 overhead; 10K+ req/min; horizontal K8s scaling | MVP |

### 8.2 Intelligent Orchestration Engine

> **Platform Differentiator:** The orchestration engine makes AI traffic decisions that reduce cost, improve resilience, and optimize quality — automatically, without developer intervention.

#### Smart Routing Rules (Priority Order)
1. **Compliance routing** — data residency and model allowlist rules (highest priority)
2. **Security routing** — PII-flagged requests routed to approved models only
3. **Budget routing** — reroute to cheaper model when wallet threshold reached
4. **Intent routing** — classify task type, select optimal model for that category
5. **Cost arbitrage** — select cheapest provider meeting SLA at current market prices
6. **Load balancing** — distribute across providers to avoid rate limits
7. **Failover routing** — reroute on 429/500/timeout detection

#### Routing Rule Schema
```yaml
routing_rule:
  name: "premium-model-gating"
  priority: 10
  conditions:
    - model_requested: ["gpt-4o", "claude-opus"]
    - team_id: not_in ["engineering-leads", "legal"]
  action:
    type: reroute
    target_model: "gpt-4o-mini"
    notify: true
    reason: "Premium model access restricted to approved teams"
```

#### Routing Experiment Engine
- A/B split traffic between models (e.g., 80% GPT-4o / 20% Claude Sonnet)
- Measure: cost per request, latency P50/P95/P99, error rate, quality score (if eval attached)
- Auto-switch: promote winner when statistical significance threshold reached
- Integration: LaunchDarkly, Unleash, internal feature flag systems

#### AI Traffic Replay & Simulation
- Record last N requests (configurable: 1K–1M) per traffic segment
- Simulate: what would cost/latency/quality have been with a different model?
- Output: detailed diff report before any model switch is applied
- Use case: safe evaluation before enabling a new provider or model version

#### Cross-Model Cost Arbitrage Engine
- Ingest real-time pricing feeds from all connected providers
- Calculate cost-per-1K-tokens for input and output per model per region
- Reroute when savings exceed configured threshold (default: 10%)
- Respect SLA constraints — never reroute to a model below quality floor

### 8.3 Semantic Caching

| Attribute | Detail |
|-----------|--------|
| Mechanism | Embed incoming prompt → vector similarity search against cache → return if above threshold |
| Similarity Threshold | Configurable per team: 0.85 (aggressive) to 0.99 (conservative) |
| TTL Policies | Per model / per team / per request category; max TTL configurable |
| Cache Segmentation | Hard tenant isolation — no cross-organization cache sharing |
| Cache Invalidation | Manual flush, TTL expiry, semantic drift detection |
| Confidence Scoring | Return cache hit confidence score in response headers |
| Expected Impact | 30–50% cost reduction for repetitive workloads; <50ms on cache hit |
| Storage Backend | Pinecone (managed) or Redis Vector (self-hosted) |
| Poison Prevention | Confidence threshold + response validation before serving cached result |

### 8.4 Token Economy & Wallet System

AI consumption becomes a managed financial resource — governed with the rigor of cloud FinOps.

#### Wallet Hierarchy
```
Organization Wallet  (org-level monthly budget)
  ├── Department Wallet  (e.g., Engineering, Legal, Sales)
  │     ├── Team Wallet  (e.g., Platform Team, Growth Team)
  │     │     └── User Wallet  (per developer / service account)
  │     └── Service Account Wallet  (per application / agent)
  └── Reserve Wallet  (emergency overflow budget)
```

#### Wallet Behaviors

| Behavior | Hard Limit | Soft Limit |
|----------|-----------|------------|
| At 80% budget | — | Alert via Slack/email/webhook |
| At 95% budget | — | Escalation alert to manager + FinOps |
| At 100% budget | Block all requests; return 402 | Allow with overdraft (if configured) |
| Overdraft | Not available | Configurable: allow up to N% over limit |
| Mid-stream depletion | Complete current streaming response; block next | Alert + complete |

#### Advanced Financial Intelligence
- **Predictive Forecasting:** Linear regression on rolling 7/14/30-day spend → "You will exceed budget in N days at current rate"
- **Anomaly Detection:** Z-score spike detection on hourly token consumption; alert on >2σ deviation
- **Circuit Breaker:** Auto-suspend a user/team/service after N requests/minute threshold breached
- **Chargeback Export:** CSV/JSON export with cost center tagging for ERP/finance ingestion
- **Budget Transfers:** Request → Approval (manager or FinOps) → Transfer workflow with audit log
- **Cost Forecasting Dashboard:** 30/60/90-day spend projection by team, model, and feature
- **AI Credit Marketplace (Future):** Departments can list and purchase unused monthly credits

### 8.5 Security & Governance Layer

#### Firewall Middleware Pipeline

```
Incoming Request
  → Auth Validation
  → Rate Limit Check
  → Wallet Balance Check
  → PII Scan (regex + ML)
  → Secret Detection (entropy analysis + pattern matching)
  → Prompt Risk Scoring
  → OPA Policy Evaluation
  → [ALLOW / BLOCK / REDACT / QUARANTINE]
  → Route to Provider
```

#### Detection Capabilities

| Detection Type | Method | Action Options | Latency Budget |
|----------------|--------|----------------|----------------|
| PII (names, SSN, DOB) | Regex + NER model | Block / Redact / Alert / Quarantine | <5ms |
| Credit card numbers | Luhn algorithm + regex | Block / Redact | <1ms |
| Email addresses | Regex | Redact (configurable) | <1ms |
| API keys / secrets | Entropy + pattern matching | Block + Alert security channel | <2ms |
| IP addresses | Regex | Redact (configurable) | <1ms |
| Medical information (PHI) | HIPAA-scoped NER | Block / Redact | <5ms |
| Financial data | Domain-specific patterns | Block / Redact | <2ms |
| Custom regex policies | User-defined patterns | Any configured action | <1ms/rule |
| Prompt injection attacks | Injection pattern library | Block + Alert | <3ms |
| Jailbreak attempts | Risk scoring model | Block / Quarantine | <10ms |
| Prompt risk score | Composite scoring (0–100) | Threshold-configurable action | <10ms |

#### AI Policy Engine (OPA)

Policy-as-code with hot reload. Policies stored as Rego files in version control.

**Built-in policy templates:**
```rego
# Example: Restrict premium models by time of day
deny[reason] {
    input.model == "gpt-4o"
    time.clock(time.now_ns())[0] >= 18  # After 6PM UTC
    not team_allowed_premium[input.team_id]
    reason := "Premium model access restricted outside business hours"
}

# Example: Block oversized requests
deny[reason] {
    input.estimated_tokens > 20000
    reason := sprintf("Request exceeds token limit (%d > 20000)", [input.estimated_tokens])
}

# Example: Data classification routing
route[target] {
    input.metadata.data_classification == "CONFIDENTIAL"
    target := "self-hosted-llama"
}
```

#### Compliance Controls
- Geo-restricted routing: route based on request origin IP or data classification tag
- Model allowlists: per compliance tier (e.g., HIPAA-tier can only use approved models)
- Immutable audit logs: append-only with cryptographic hash chain for tamper detection
- Data retention policies: configurable per tenant (30/90/365 days; right-to-erasure supported)
- Tenant isolation: enforced at network, storage, and application layers

### 8.6 Observability & ROI Intelligence

#### Operational Metrics (Real-Time)

| Metric | Granularity | Storage | Retention |
|--------|-------------|---------|-----------|
| Requests per second | Per second | Redis TSDB | 7 days |
| Token consumption | Per request | ClickHouse | 365 days |
| Cost per request | Per request | ClickHouse | 365 days |
| Latency (P50/P95/P99) | Per provider per model | ClickHouse | 90 days |
| Error rate (4xx/5xx) | Per minute | ClickHouse | 90 days |
| Cache hit rate | Per hour | ClickHouse | 90 days |
| Wallet balance | Real-time | PostgreSQL | Perpetual |
| Budget burn rate | Per hour | ClickHouse | 365 days |
| Failover events | Per event | ClickHouse | 365 days |

#### Business Intelligence Metrics

| Metric | Description | Use Case |
|--------|-------------|----------|
| Cost per feature | AI spend attributed to product features via request metadata | Product pricing decisions |
| Token efficiency score | Useful output tokens / total tokens billed | Prompt optimization guidance |
| Model efficiency index | Quality score / cost ratio per model | Model selection decisions |
| Budget predictability index | Variance between forecast and actual spend | CFO reporting |
| AI ROI score | Revenue or productivity output / AI spend | Executive reporting |
| Team efficiency ranking | Cost efficiency score per team with leaderboard | Behavioral nudge |
| Cache ROI | $ saved from cache hits / cost of cache infrastructure | Cache configuration decisions |

#### AI Usage Classification
Automatically classify every request into a category for per-category cost analytics:

```
Request Categories:
├── Code Generation (completions, debugging, review)
├── Summarization (documents, emails, meetings)
├── Legal Reasoning (contract review, compliance checks)
├── Customer Support (chatbot, ticket deflection)
├── Content Creation (copy, marketing, documentation)
├── Data Extraction (parsing, classification, tagging)
├── Reasoning (analysis, planning, research)
├── Embeddings (search, similarity, clustering)
└── Other / Unclassified
```

#### Observability Integrations
- **Prometheus:** `/metrics` endpoint exposing all gateway and wallet metrics
- **Grafana:** Pre-built dashboard templates for import
- **Datadog:** Native integration via DogStatsD + APM tracing
- **New Relic:** Custom instrumentation via New Relic One
- **OpenTelemetry:** Full OTel tracing across gateway, orchestration, and wallet services
- **Jaeger / Zipkin:** Distributed tracing for request lifecycle debugging
- **PagerDuty:** Alert routing for SLA breach and anomaly events
- **OpsGenie:** Alternative alert routing
- **Splunk:** Log forwarding via HEC (HTTP Event Collector)
- **Elastic / ELK:** Log streaming via Logstash or Beats

#### Continuous Optimization Engine
- Auto-downgrade: detect when cheaper model maintains quality → automatically route there
- Prompt compression: suggest shorter prompt variants that achieve same output quality
- Token waste detection: identify patterns of unused context or redundant system prompts
- Model recommendation engine: weekly report — "Switch team X from GPT-4 to Sonnet, save $3,200/month"

### 8.7 Developer Experience

#### IDE Extensions

**VS Code Extension:**
- Real-time token counter and estimated cost in status bar
- Session cost gauge with configurable alert threshold
- Model selector dropdown with cost-per-request preview for each option
- Per-file or per-repo token budget configuration
- Dev vs. Prod mode toggle (Dev: use cheaper model + relaxed limits)
- Quick actions: "Optimize this prompt", "Estimate cost before sending"
- One-click wallet top-up request workflow

**JetBrains Plugin (IntelliJ, PyCharm, GoLand, WebStorm):**
- Feature parity with VS Code extension
- Integration with JetBrains AI Assistant for side-by-side cost comparison

**GitHub Copilot Proxy Mode:**
- Route GitHub Copilot through AI Orchestrator gateway for cost tracking and governance
- Requires enterprise Copilot plan

#### CLI Tool
```bash
# Install
npm install -g @ai-orchestrator/cli

# Authenticate
ao auth login --org acme-corp

# Check your wallet balance
ao wallet balance

# Test a request and see cost preview
ao test --model gpt-4o --prompt "Summarize this document" --dry-run

# View team spend
ao spend --team platform --period 30d

# View routing rules
ao routes list

# Apply a policy
ao policy apply ./policies/restrict-premium.rego
```

#### SDK Support
- **Python SDK:** `pip install ai-orchestrator` — drop-in replacement for `openai` package
- **Node.js SDK:** `npm install @ai-orchestrator/sdk` — wraps OpenAI JS SDK
- **Go SDK:** `go get github.com/ai-orchestrator/go-sdk`
- **Java SDK:** Maven + Gradle support for enterprise Java shops
- **REST:** Any language via standard HTTP + OpenAI-compatible JSON schema

#### Slack / Microsoft Teams App
- `/ai-budget` — check your team's current wallet balance and burn rate
- `/ai-request [amount]` — request budget increase (triggers approval workflow)
- `/ai-top-users` — see which team members are consuming most tokens this month
- `/ai-forecast` — show predicted end-of-month spend at current rate
- Budget alert messages with one-click "Approve Overdraft" or "Block Now" actions
- Daily 9AM digest: yesterday's spend, today's forecast, any anomalies
- Weekly efficiency report: your team's AI Efficiency Score vs. company average

### 8.8 Prompt Versioning & Registry

"Git for prompts" — versioned, auditable, performance-tracked prompt management.

#### Core Features
- **Prompt Store:** Central repository of all prompts used across applications
- **Version History:** Full diff between prompt versions with metadata (author, date, reason)
- **Rollback:** One-click revert to any previous prompt version
- **Approval Workflow:** PR-style review for changes to production prompts
- **A/B Testing:** Route % of traffic to new prompt version vs. baseline
- **Performance Metrics:** Per-prompt cost, latency, output quality score, token efficiency
- **Prompt Compression:** Automated suggestions to reduce token count while preserving intent
- **Variable Injection:** Template system for dynamic prompt construction with typed variables
- **Import/Export:** Bring existing prompts from LangChain hub, Humanloop, etc.

#### Prompt Metadata Schema
```json
{
  "prompt_id": "cust-support-classifier-v3",
  "version": 3,
  "description": "Classifies customer support tickets into categories",
  "author": "jane.doe@acme.com",
  "created_at": "2026-02-01T10:00:00Z",
  "tags": ["support", "classification", "production"],
  "target_model": "gpt-4o-mini",
  "avg_input_tokens": 850,
  "avg_output_tokens": 120,
  "avg_cost_per_call": 0.00048,
  "quality_score": 0.91,
  "status": "production",
  "review_required": true,
  "template": "You are a support ticket classifier...",
  "variables": ["ticket_text", "customer_tier"]
}
```

### 8.9 Enterprise Integrations

See [Section 13 — Integration Catalog](#13-integration-catalog) for full details.

**Summary categories:**
- Identity & SSO (Okta, Entra ID, Google Workspace)
- FinOps & Finance (Snowflake, SAP, Oracle, NetSuite, Workday)
- Observability (Datadog, Grafana, New Relic, Splunk)
- Ticketing & Workflow (Jira, ServiceNow, Linear)
- Communication (Slack, Microsoft Teams, Google Chat)
- CI/CD (GitHub Actions, GitLab CI, Jenkins, CircleCI)
- Experimentation (LaunchDarkly, Unleash, Statsig)
- LLM Providers (10+ providers)
- Self-Hosted Models (Ollama, vLLM, TGI, LocalAI)
- Evaluation (Weights & Biases, Braintrust, Scale AI)

---

## 9. User Stories & Acceptance Criteria

### Epic 1: Gateway Integration

**US-001: Zero-code integration**
> As a backend engineer, I want to route all AI traffic through the gateway by changing only the base URL, so that I don't need to refactor any existing application code.

**Acceptance Criteria:**
- [ ] Changing `baseURL` from `https://api.openai.com/v1` to `https://gateway.ai-orchestrator.io/v1` is the only required code change
- [ ] All OpenAI SDK methods work without modification
- [ ] Streaming responses function identically (SSE format preserved)
- [ ] Response payloads are byte-for-byte identical to direct provider responses (except added headers)
- [ ] Integration test suite passes against existing application test suite
- [ ] Latency overhead does not exceed 150ms at P95

---

**US-002: Multi-provider transparent routing**
> As a platform engineer, I want requests to be automatically routed to the best available provider, so that I don't have to manage failover logic in my application code.

**Acceptance Criteria:**
- [ ] When primary provider returns 429, request is transparently retried on secondary provider within 500ms
- [ ] When primary provider returns 500 3 times in 60 seconds, it is marked degraded and traffic shifts automatically
- [ ] Application receives a valid response — no error propagated to caller during transparent failover
- [ ] Failover event is logged and visible in dashboard within 30 seconds
- [ ] Degraded provider status is visible in admin dashboard
- [ ] Provider recovers and traffic rebalances automatically when health check passes

---

### Epic 2: Wallet & Budget Control

**US-003: Hard wallet limit enforcement**
> As a FinOps lead, I want to set a hard monthly budget per team, so that AI spend cannot exceed the approved amount without my explicit approval.

**Acceptance Criteria:**
- [ ] Admin can set hard limit (in USD) per team via dashboard or API
- [ ] When team wallet reaches 100% of limit, all subsequent requests return HTTP 402 with message: `{"error": "wallet_exhausted", "team": "...", "limit": ..., "spent": ...}`
- [ ] Requests in flight at time of limit breach complete normally (no mid-stream termination)
- [ ] Alert sent to team admin and FinOps lead when wallet reaches 80%, 90%, 95%, 100%
- [ ] Limit reset occurs on configured renewal date (default: 1st of month at 00:00 UTC)
- [ ] Hard limit cannot be exceeded even with concurrent requests (atomic balance check)

---

**US-004: Budget transfer workflow**
> As a team lead, I want to request a budget increase from my manager, so that my team can continue working when we've consumed our monthly allocation.

**Acceptance Criteria:**
- [ ] Team member can submit transfer request via Slack `/ai-request [amount] [reason]` or dashboard
- [ ] Request creates a notification for the configured approver (manager or FinOps)
- [ ] Approver can approve or reject from Slack, email link, or dashboard
- [ ] On approval, wallet balance updates atomically within 5 seconds
- [ ] On rejection, requestor receives notification with optional reason
- [ ] All transfer requests, approvals, and rejections are recorded in immutable audit log
- [ ] Transfer request expires after 48 hours if not actioned

---

**US-005: Mid-month spend forecast**
> As a CFO, I want to see a projected end-of-month AI spend for each department, so that I can identify overspend risk before it happens.

**Acceptance Criteria:**
- [ ] Dashboard displays 30-day spend forecast per department, team, and organization
- [ ] Forecast uses linear regression on last 14 days of actuals (configurable window)
- [ ] Forecast confidence interval (±%) displayed alongside projection
- [ ] "Predicted to exceed budget" warning shown when projection > 95% of limit
- [ ] Forecast refreshes every 4 hours
- [ ] Forecast data exportable as CSV with timestamps
- [ ] Historical forecast accuracy tracked and displayed (MAPE metric)

---

### Epic 3: Security & Compliance

**US-006: PII detection and redaction**
> As a security lead, I want all prompts containing PII to be automatically redacted before reaching the LLM provider, so that sensitive data never leaves our governance perimeter.

**Acceptance Criteria:**
- [ ] System detects: full names, email addresses, phone numbers, SSNs, DOBs, credit card numbers, medical record numbers, IP addresses
- [ ] Detected PII is replaced with placeholder tokens (e.g., `[PERSON_1]`, `[EMAIL_1]`) before forwarding to provider
- [ ] Detection completes within 10ms for requests ≤4K tokens
- [ ] False positive rate ≤ 2% on benchmark test dataset
- [ ] False negative rate ≤ 0.5% on benchmark test dataset
- [ ] Redaction events logged with: timestamp, team, request_id, entity_types_detected (no actual PII stored)
- [ ] Security channel alert sent when PII detected (configurable: always, or on-threshold)
- [ ] Admin can configure redaction vs. block behavior per entity type

---

**US-007: Immutable audit log**
> As a compliance officer, I want a complete, tamper-proof log of all AI requests, so that I can respond to regulatory audits and legal discovery requests.

**Acceptance Criteria:**
- [ ] Every request logged with: timestamp, user_id, team_id, model, provider, token_count_in, token_count_out, cost, latency, policy_actions_taken, request_hash
- [ ] Prompt content and response content stored only if `store_prompts: true` configured (opt-in)
- [ ] Audit log is append-only — no update or delete operations permitted at API layer
- [ ] Each log entry includes SHA-256 hash of previous entry (cryptographic chain)
- [ ] Log export available: CSV, JSON, Parquet; filterable by date, team, user, model
- [ ] Log accessible via API for SIEM integration
- [ ] Retention period configurable (default: 365 days); GDPR right-to-erasure supported for prompt content only (metadata retained)

---

### Epic 4: Developer Experience

**US-008: Real-time cost visibility in IDE**
> As a developer, I want to see the estimated cost of my AI request before I send it, so that I can make informed decisions about which model to use.

**Acceptance Criteria:**
- [ ] VS Code extension displays estimated cost in status bar as developer types prompt
- [ ] Cost estimate updates within 500ms of typing pause
- [ ] Estimate shows: model name, estimated input tokens, estimated cost in USD
- [ ] One-click option to switch to cheaper model with cost comparison shown
- [ ] Session total cost displayed and updates in real time as requests complete
- [ ] Alert shown when session cost exceeds configurable threshold (default: $5)
- [ ] Extension works offline (uses cached token pricing, updates when online)

---

### Epic 5: Observability & ROI

**US-009: Feature-level cost attribution**
> As a product manager, I want to see the AI cost attributed to each product feature, so that I can include AI infrastructure cost in my feature pricing and ROI calculations.

**Acceptance Criteria:**
- [ ] Application can tag requests with `metadata.feature_id` and `metadata.product_line`
- [ ] Dashboard shows cost breakdown by `feature_id` over any date range
- [ ] Cost per feature exportable as CSV for finance reporting
- [ ] API endpoint available for programmatic cost retrieval: `GET /v1/analytics/cost?group_by=feature_id&from=...&to=...`
- [ ] Feature cost displayed alongside usage count and average cost per call
- [ ] Alert configurable: "Notify when feature X cost exceeds $Y/day"

---

## 10. API Contract

### Authentication

```
Authorization: Bearer {api_key}
X-Organization-ID: {org_id}
X-Team-ID: {team_id}          # Optional: override team for cost attribution
X-Feature-ID: {feature_id}    # Optional: feature-level cost attribution
X-Request-Priority: {normal|high|low}  # Optional: affects routing priority
```

### Gateway Endpoints

#### POST /v1/chat/completions
OpenAI-compatible chat completion. Accepts all OpenAI parameters plus:

```http
POST /v1/chat/completions
Authorization: Bearer sk-...
Content-Type: application/json

{
  "model": "gpt-4o",                     // Or any supported model alias
  "messages": [...],
  "stream": true,
  "temperature": 0.7,
  "max_tokens": 2000,
  // AI Orchestrator extensions (all optional):
  "x_orchestrator": {
    "routing_strategy": "cost_optimized", // cost_optimized | quality_optimized | latency_optimized | explicit
    "fallback_models": ["gpt-4o-mini", "claude-haiku"],
    "cache_enabled": true,
    "cache_ttl_seconds": 3600,
    "feature_id": "email-summarizer",
    "budget_group": "product-team",
    "dry_run": false                      // If true, estimate cost without executing
  }
}
```

**Response (non-streaming):**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1709000000,
  "model": "gpt-4o-mini",              // Actual model used (may differ from requested)
  "choices": [...],
  "usage": {
    "prompt_tokens": 450,
    "completion_tokens": 280,
    "total_tokens": 730
  },
  "x_orchestrator": {
    "request_id": "req_xyz789",
    "provider_used": "openai",
    "model_requested": "gpt-4o",
    "model_used": "gpt-4o-mini",       // If routing changed model
    "routing_reason": "cost_threshold_reached",
    "cost_usd": 0.000438,
    "cache_hit": false,
    "cache_similarity": null,
    "latency_ms": 842,
    "wallet_balance_after_usd": 3241.22,
    "policy_actions": []
  }
}
```

#### GET /v1/wallet/balance
```http
GET /v1/wallet/balance?team_id=platform-team
Authorization: Bearer sk-...

Response:
{
  "organization": {
    "limit_usd": 50000,
    "spent_usd": 31420.50,
    "remaining_usd": 18579.50,
    "utilization_pct": 62.8,
    "reset_date": "2026-03-01T00:00:00Z",
    "forecast_eom_usd": 47800.00,
    "forecast_breach_date": null
  },
  "team": {
    "team_id": "platform-team",
    "limit_usd": 8000,
    "spent_usd": 5420.10,
    "remaining_usd": 2579.90,
    "utilization_pct": 67.8,
    "forecast_eom_usd": 8100.00,
    "forecast_breach_date": "2026-02-26T14:00:00Z"
  }
}
```

#### GET /v1/analytics/cost
```http
GET /v1/analytics/cost?group_by=team_id&from=2026-02-01&to=2026-02-18&granularity=day
Authorization: Bearer sk-...

Response:
{
  "period": { "from": "2026-02-01", "to": "2026-02-18" },
  "total_cost_usd": 28450.22,
  "total_tokens": 48200000,
  "breakdown": [
    {
      "team_id": "platform-team",
      "cost_usd": 12200.10,
      "tokens": 20100000,
      "requests": 84200,
      "avg_cost_per_request": 0.000145,
      "cache_savings_usd": 2400.00,
      "daily": [...]
    }
  ]
}
```

#### POST /v1/routes
```http
POST /v1/routes
Authorization: Bearer sk-...

{
  "name": "gpt4-to-mini-after-threshold",
  "priority": 20,
  "conditions": {
    "model_requested": ["gpt-4o"],
    "team_wallet_utilization_gte": 80
  },
  "action": {
    "type": "reroute",
    "target_model": "gpt-4o-mini",
    "notify_user": true
  },
  "active": true
}
```

#### POST /v1/policies
```http
POST /v1/policies
Authorization: Bearer sk-...

{
  "name": "block-pii-in-legal-team",
  "engine": "opa",
  "rego": "package orchestrator\ndeny[reason] { ... }",
  "active": true,
  "dry_run_mode": false
}
```

### Error Response Schema

```json
{
  "error": {
    "code": "wallet_exhausted",
    "message": "Team 'platform-team' has exhausted its monthly budget of $8,000.00",
    "type": "budget_error",
    "request_id": "req_xyz789",
    "details": {
      "team_id": "platform-team",
      "limit_usd": 8000.00,
      "spent_usd": 8000.00,
      "reset_date": "2026-03-01T00:00:00Z",
      "request_transfer_url": "https://dashboard.ai-orchestrator.io/wallet/request?team=platform-team"
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | Success | Request completed normally |
| 202 | Accepted | Async operation queued |
| 400 | Bad Request | Malformed request schema |
| 401 | Unauthorized | Invalid or missing API key |
| 402 | Payment Required | Wallet exhausted |
| 403 | Forbidden | Policy blocked the request |
| 422 | Unprocessable Entity | Request blocked by security middleware |
| 429 | Too Many Requests | Rate limit hit at gateway level |
| 500 | Internal Server Error | Gateway internal error |
| 502 | Bad Gateway | All providers unavailable |
| 503 | Service Unavailable | Gateway maintenance or overload |
| 504 | Gateway Timeout | Provider timeout after all retries |

### Rate Limiting Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1709000060
X-RateLimit-Policy: per-team-per-minute
Retry-After: 14          # Only present on 429
```

---

## 11. Data Models & Schemas

### Organization
```typescript
interface Organization {
  id: string;                          // UUID
  name: string;
  slug: string;                        // URL-safe identifier
  created_at: Date;
  plan: 'starter' | 'growth' | 'enterprise';
  settings: {
    default_model: string;
    store_prompts: boolean;            // Default: false
    audit_log_retention_days: number; // Default: 365
    pii_detection_enabled: boolean;
    data_residency_region: string;    // 'us' | 'eu' | 'apac' | 'any'
  };
  billing: {
    monthly_limit_usd: number;
    current_spend_usd: number;
    billing_email: string;
    chargeback_export_format: 'csv' | 'json';
  };
}
```

### Wallet
```typescript
interface Wallet {
  id: string;
  organization_id: string;
  parent_wallet_id: string | null;     // null for org-level wallet
  type: 'organization' | 'department' | 'team' | 'user' | 'service_account';
  entity_id: string;                   // department_id, team_id, user_id, etc.
  name: string;
  limit_usd: number;
  spent_usd: number;                   // Updated atomically via DB transaction
  reserved_usd: number;                // In-flight requests
  overdraft_limit_usd: number;         // 0 = no overdraft
  soft_limit_thresholds: number[];     // e.g., [0.8, 0.9, 0.95] → alert at these % of limit
  reset_period: 'monthly' | 'weekly' | 'custom';
  reset_day: number;                   // Day of month (1–28)
  created_at: Date;
  updated_at: Date;
}
```

### Request Log
```typescript
interface RequestLog {
  id: string;                          // UUID, also used as trace ID
  organization_id: string;
  team_id: string;
  user_id: string | null;
  service_account_id: string | null;
  feature_id: string | null;
  timestamp: Date;
  model_requested: string;
  model_used: string;                  // May differ due to routing
  provider_used: string;
  routing_reason: string | null;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number;
  cache_hit: boolean;
  cache_similarity_score: number | null;
  request_hash: string;                // SHA-256 of prompt for dedup
  policy_actions: PolicyAction[];
  pii_detected: boolean;
  pii_entity_types: string[];          // e.g., ['EMAIL', 'PHONE'] — no actual PII stored
  error_code: string | null;
  provider_request_id: string;
  prev_log_hash: string;               // For audit chain integrity
}
```

### Routing Rule
```typescript
interface RoutingRule {
  id: string;
  organization_id: string;
  name: string;
  priority: number;                    // Lower number = higher priority
  conditions: {
    model_requested?: string[];
    team_id?: string[];
    user_id?: string[];
    feature_id?: string[];
    estimated_tokens_gte?: number;
    team_wallet_utilization_gte?: number;  // 0–100
    time_of_day_utc?: { from: string; to: string };  // HH:MM format
    data_classification?: string[];
  };
  action: {
    type: 'reroute' | 'block' | 'allow' | 'require_approval' | 'add_metadata';
    target_model?: string;
    target_provider?: string;
    notify_user?: boolean;
    reason?: string;
  };
  active: boolean;
  created_by: string;
  created_at: Date;
}
```

### Policy
```typescript
interface Policy {
  id: string;
  organization_id: string;
  name: string;
  description: string;
  engine: 'opa' | 'regex' | 'builtin';
  rego?: string;                       // OPA Rego policy text
  regex_patterns?: string[];
  builtin_policy?: string;             // e.g., 'pii_detection', 'secret_scanning'
  action: 'block' | 'redact' | 'alert' | 'quarantine' | 'log_only';
  dry_run_mode: boolean;               // Log violations but don't enforce
  active: boolean;
  applies_to: {
    teams?: string[];
    models?: string[];
    features?: string[];
  };
  created_at: Date;
  updated_at: Date;
}
```

### Provider Configuration
```typescript
interface Provider {
  id: string;
  organization_id: string;
  name: string;
  type: 'openai' | 'anthropic' | 'gemini' | 'cohere' | 'mistral' | 'together' |
        'groq' | 'perplexity' | 'ollama' | 'vllm' | 'azure_openai' | 'bedrock' | 'custom';
  base_url: string;
  api_key_vault_path: string;          // Path in Vault, not the key itself
  models: ProviderModel[];
  health_status: 'healthy' | 'degraded' | 'down';
  last_health_check: Date;
  priority: number;                    // Routing preference (lower = preferred)
  enabled: boolean;
  rate_limits: {
    requests_per_minute: number;
    tokens_per_minute: number;
    tokens_per_day: number;
  };
  region_restrictions: string[];       // ISO regions where this provider may be used
}

interface ProviderModel {
  model_id: string;                    // Provider-specific ID e.g. 'gpt-4o-2024-11-20'
  alias: string;                       // Normalized alias e.g. 'gpt-4o'
  input_cost_per_1k_tokens: number;    // USD
  output_cost_per_1k_tokens: number;   // USD
  context_window: number;              // Max tokens
  capabilities: string[];              // ['chat', 'embeddings', 'vision', 'function_calling']
  quality_score: number | null;        // 0–100 from benchmarking
  avg_latency_ms: number | null;
}
```

### Audit Log Entry
```typescript
interface AuditLogEntry {
  id: string;
  sequence: number;                    // Monotonically increasing
  organization_id: string;
  timestamp: Date;
  actor_type: 'user' | 'service_account' | 'system' | 'admin';
  actor_id: string;
  action: string;                      // e.g., 'wallet.limit.updated', 'policy.created', 'request.blocked'
  resource_type: string;
  resource_id: string;
  before_state: Record<string, unknown> | null;
  after_state: Record<string, unknown> | null;
  ip_address: string;
  user_agent: string;
  entry_hash: string;                  // SHA-256 of this entry's content
  prev_entry_hash: string;             // For chain integrity verification
}
```

---

## 12. Error Handling & Edge Cases

### Gateway Layer Edge Cases

| Scenario | Detection | Behavior | User Impact |
|----------|-----------|----------|-------------|
| Provider returns 429 | HTTP status | Retry on next configured provider with exponential backoff | Transparent; <500ms delay |
| Provider returns 500 | HTTP status | Retry 3x with 100ms backoff, then failover | Transparent if failover available |
| All providers down | Health check failure | Return 502 with list of affected providers | Explicit error; alert sent |
| Provider timeout (>30s) | TCP timeout | Failover and log | Transparent |
| Partial stream disconnect (client drops) | SSE write failure | Log partial tokens; bill for tokens sent; do not retry | Partial response; tokens billed |
| Mid-stream wallet depletion | Real-time balance check | Complete current stream; block next request | Stream completes; 402 on next |
| Provider changes response schema | Schema validation | Log mismatch; attempt normalization; fallback to raw pass-through | Degraded but functional |
| Concurrent requests exhaust wallet | Atomic reservation | Use optimistic locking; over-reservation by <0.1% | Slight budget overage acceptable |
| Cache DB unavailable | Health check | Bypass cache; route directly to provider | Higher cost; no user impact |
| Vector DB latency spike | Timeout (configurable, default 50ms) | Skip cache; route directly | Higher cost; no user impact |

### Wallet & Metering Edge Cases

| Scenario | Behavior |
|----------|----------|
| Token count discrepancy vs. provider billing | Log diff; alert if >0.5% variance; reconciliation report weekly |
| Wallet reset race condition (e.g., midnight requests) | DB-level transaction lock; reset then allow |
| Negative wallet balance (concurrent requests) | Allow up to -0.1% overage; block further requests; alert |
| Provider billing in different granularity | Normalize to per-token; handle minimum billing increments |
| Streaming response token estimation (pre-response) | Estimate based on max_tokens parameter; settle against actual on completion |
| Request fails before any tokens consumed | Zero charge; no wallet deduction |
| Request fails mid-completion | Bill tokens consumed up to failure point |
| Free-tier model usage (some providers offer free tiers) | Track separately; do not deduct from wallet; log for audit |

### Security Middleware Edge Cases

| Scenario | Behavior |
|----------|----------|
| PII detection false positive blocks legitimate request | User sees 422 with appeal link; admin can whitelist pattern |
| PII in system prompt (usually safe) | Configurable: treat system prompt differently from user message |
| Encrypted content in prompt | Cannot detect PII in encrypted content; log warning |
| Very large prompt (>32K tokens) | Scan first and last 4K tokens; log that middle content was not scanned |
| Prompt injection in tool output | Scan tool results returned to model as well as initial prompt |
| Policy evaluation timeout (OPA) | Fail-open (configurable) or fail-closed; log timeout |
| Vault unavailable (cannot retrieve provider key) | Return 503; do not bypass vault; alert ops |

### Failover Scenarios

```
Failover Decision Tree:
Provider returns error
  ├── 429 (rate limit)
  │     └── Try next provider in priority order
  │           └── If none available → queue request (if queuing enabled) or return 429
  ├── 500 (server error)
  │     └── Retry same provider 3x (100ms, 200ms, 400ms backoff)
  │           └── On 3rd failure → try next provider
  │                 └── If none available → return 502
  ├── 503 (service unavailable)
  │     └── Skip to next provider immediately
  ├── Timeout (>30s)
  │     └── Cancel request; try next provider
  └── Network error (DNS, TCP)
        └── Try next provider immediately
```

---

## 13. Integration Catalog

### LLM Providers

| Provider | Models Supported | Integration Type | Auth |
|----------|-----------------|------------------|------|
| OpenAI | GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo, o1, o3, Embeddings, Whisper, DALL-E | Native REST + SSE | API Key |
| Anthropic | Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus | Native REST + SSE | API Key + Beta headers |
| Google (Gemini) | Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash, Embeddings | REST via Vertex AI or AI Studio | OAuth2 / API Key |
| Microsoft Azure OpenAI | All OpenAI models via Azure | OpenAI-compatible REST | API Key + Endpoint |
| AWS Bedrock | Claude (Anthropic), Titan, Llama, Mistral, Cohere via Bedrock | AWS SDK + REST | IAM Role / Access Key |
| Cohere | Command R+, Command R, Embed v3, Rerank | Native REST | API Key |
| Mistral AI | Mistral Large, Small, Codestral, Embeddings | Native REST | API Key |
| Together AI | 50+ open models (Llama, Mixtral, Qwen, etc.) | OpenAI-compatible REST | API Key |
| Groq | Llama 3, Mixtral, Gemma (ultra-fast inference) | OpenAI-compatible REST | API Key |
| Perplexity | Sonar, Sonar Pro (with web search) | OpenAI-compatible REST | API Key |
| Fireworks AI | Open models + fine-tuned models | OpenAI-compatible REST | API Key |
| Replicate | Any Replicate-hosted model | REST | API Key |
| Hugging Face Inference | Hosted open models | REST | API Key |
| NovitaAI | Open models | OpenAI-compatible REST | API Key |

### Self-Hosted / On-Premise Models

| Platform | Integration | Capabilities Tracked |
|----------|-------------|----------------------|
| Ollama | OpenAI-compatible local endpoint | Token count, latency, GPU utilization (via Prometheus) |
| vLLM | OpenAI-compatible server | Token/s throughput, GPU memory, queue depth |
| Text Generation Inference (TGI) | REST | Throughput, latency, batch size |
| LocalAI | OpenAI-compatible | Token count, latency |
| LM Studio | Local REST server | Token count, latency |
| NVIDIA NIM | REST + Triton | GPU utilization, inference latency |
| Triton Inference Server | REST + gRPC | Throughput, queue depth, GPU metrics |

### Identity & SSO

| Provider | Protocol | Features |
|----------|----------|----------|
| Okta | SAML 2.0, OIDC | SSO, SCIM provisioning, MFA enforcement |
| Microsoft Entra ID (Azure AD) | SAML 2.0, OIDC | SSO, SCIM, conditional access integration |
| Google Workspace | OIDC | SSO, Google group sync |
| Auth0 | OIDC | SSO, custom rules |
| OneLogin | SAML 2.0 | SSO, SCIM |
| Ping Identity | SAML 2.0, OIDC | Enterprise SSO |
| JumpCloud | SAML 2.0 | SSO, directory sync |
| LDAP / Active Directory | LDAP | Directory sync for on-premise enterprise |
| GitHub OAuth | OAuth 2.0 | Developer-friendly SSO for tech teams |
| GitLab OAuth | OAuth 2.0 | Alternative for GitLab-first organizations |

### FinOps & Finance

| System | Integration Type | Data Exchanged |
|--------|-----------------|----------------|
| Snowflake | Data export (Kafka → Snowflake Connector or direct) | All request logs, cost data, wallet activity |
| Databricks | Delta Live Tables connector | Streaming cost data for custom analytics |
| SAP S/4HANA | REST API + cost center tags | Chargeback export, budget sync |
| Oracle ERP Cloud | REST API | Cost center chargeback, budget alerts |
| NetSuite | REST API | Cost allocation, chargeback |
| Workday Financial | REST API | Cost center mapping, budget sync |
| QuickBooks (SMB) | CSV export + API | Monthly spend export |
| Xero (SMB) | CSV export | Monthly spend export |
| Stripe | Webhook | For AI-Orchestrator SaaS billing (our own billing) |
| AWS Cost Explorer | Tag-based cost allocation | AI infra cost consolidation |
| Azure Cost Management | Tag-based | Same |
| GCP Billing | BigQuery export | Same |
| CloudHealth / Apptio | API | Multi-cloud FinOps consolidation |
| Cloudability | API | FinOps platform integration |

### Observability & Monitoring

| Tool | Integration | Metrics/Data Sent |
|------|-------------|-------------------|
| Datadog | DogStatsD + APM + Log Forwarding | All gateway metrics, traces, wallet events |
| Grafana + Prometheus | Prometheus scrape endpoint `/metrics` | All metrics in Prometheus format |
| New Relic | New Relic One SDK + Log API | Metrics, traces, custom events |
| Splunk | HEC (HTTP Event Collector) | Structured logs, audit events |
| Elastic / ELK | Logstash Beats or direct ES API | Full log stream |
| Dynatrace | OneAgent or REST API | Metrics, distributed traces |
| AppDynamics | REST API | Application performance metrics |
| Jaeger | OTel exporter | Distributed traces |
| Zipkin | OTel exporter | Distributed traces |
| Honeycomb | OTel exporter | Wide events for debugging |
| Lightstep / ServiceNow | OTel exporter | Distributed traces |
| PagerDuty | Events API v2 | SLA breach alerts, anomaly alerts |
| OpsGenie | REST API | Alert routing |
| VictorOps / Splunk On-Call | REST API | Incident management |
| Statuspage.io | API | Customer-facing status updates |

### Alerting & Communication

| Tool | Integration | Use Cases |
|------|-------------|-----------|
| Slack | Slack App (Bolt framework) | Budget alerts, approval workflows, spend digests, leaderboard |
| Microsoft Teams | Teams App (Bot Framework) | Same as Slack |
| Google Chat | Webhook + Chat API | Budget alerts, digests |
| Email (SMTP) | Nodemailer / SES / SendGrid | Budget alerts, weekly reports, billing notifications |
| AWS SES | Direct | Transactional email at scale |
| SendGrid | API | Email delivery |
| Twilio SMS | REST API | Critical budget breach alerts via SMS |
| PagerDuty | Events API | On-call escalation for SLA breach |
| Webhooks (generic) | Configurable POST | Any custom system integration |

### Ticketing & Workflow

| Tool | Integration | Use Cases |
|------|-------------|-----------|
| Jira | REST API | Auto-create tickets for anomalies, policy violations |
| ServiceNow | REST API | ITSM workflow for budget requests, security incidents |
| Linear | REST API | Engineering-focused issue creation |
| GitHub Issues | REST API | Developer-facing issue tracking |
| Zendesk | REST API | Customer support ticket integration |
| Freshdesk | REST API | Alternative support platform |
| Asana | REST API | Task creation for budget review actions |
| Monday.com | REST API | Workflow automation for budget approvals |

### CI/CD & Developer Tooling

| Tool | Integration | Use Cases |
|------|-------------|-----------|
| GitHub Actions | Action Marketplace + REST API | Cost gate in CI: fail pipeline if estimated cost exceeds threshold |
| GitLab CI/CD | REST API | Same as GitHub Actions |
| Jenkins | Plugin + REST API | Cost gate, policy validation in pipeline |
| CircleCI | Orb + REST API | Cost gate |
| ArgoCD | Webhook | Deployment event tracking for cost attribution |
| Terraform | Provider (custom) | Provision wallets, routing rules as code |
| Pulumi | SDK | Same as Terraform |
| Helm | Chart | Deploy AI Orchestrator to Kubernetes |
| Docker Hub | Public images | Container images for self-hosted deployment |

### Experimentation & Feature Flags

| Tool | Integration | Use Cases |
|------|-------------|-----------|
| LaunchDarkly | SDK | Control routing experiments like feature rollouts |
| Unleash | REST API | Open-source feature flag alternative |
| Statsig | REST API | Experiment assignment + routing decisions |
| Split.io | REST API | A/B test model routing |
| Optimizely | REST API | Experiment framework for model selection |
| Internal flags | Webhook/API | Custom feature flag system integration |

### AI Evaluation & Quality

| Tool | Integration | Use Cases |
|------|-------------|-----------|
| Weights & Biases (W&B) | REST API | Log model comparison runs, quality metrics |
| Braintrust | REST API | LLM evaluation and prompt testing |
| Scale AI / Spellbook | REST API | Human evaluation of model outputs |
| Arize AI | REST API | Model monitoring and drift detection |
| WhyLabs | REST API | Data quality monitoring for LLM inputs |
| Promptfoo | CLI + REST | Automated prompt testing and regression |
| Ragas | Python library | RAG pipeline evaluation metrics |
| LMSYS / FastChat | — | Open benchmark datasets for quality scoring |
| HellaSwag, MMLU, etc. | Custom benchmark runner | Provider quality benchmarking |

### Data & Storage

| Service | Integration | Use Cases |
|---------|-------------|-----------|
| AWS S3 | SDK | Audit log archival, export storage, prompt snapshots |
| Google Cloud Storage | SDK | Same |
| Azure Blob Storage | SDK | Same |
| AWS RDS (PostgreSQL) | JDBC/PG driver | Managed PostgreSQL for wallets |
| AWS ElastiCache | Redis protocol | Managed Redis for caching |
| Pinecone | REST API | Managed vector DB for semantic cache |
| Weaviate | REST + GraphQL | Alternative vector DB |
| Qdrant | REST | Alternative vector DB (self-hostable) |
| Chroma | REST | Alternative vector DB (lightweight) |

### Agent Frameworks & LLM Tooling

| Framework | Integration | Notes |
|-----------|-------------|-------|
| LangChain | Drop-in via `openai_api_base` config | Full compatibility; all LangChain chains supported |
| LangGraph | Same as LangChain | Agent graph support |
| LlamaIndex | `openai_api_base` override | RAG pipelines fully supported |
| AutoGen (Microsoft) | `base_url` config | Multi-agent framework |
| CrewAI | `base_url` config | Agent orchestration |
| Semantic Kernel | `endpoint` config | Microsoft agent framework |
| Haystack | `api_base` config | Document QA pipelines |
| Instructor | Wraps OpenAI SDK | Structured output library |
| Guidance | `llm` config | Constrained generation |
| DSPy | `lm` config | Declarative LM programming |
| Vercel AI SDK | `baseURL` config | Next.js AI application framework |
| Magentic | `@prompt` decorator config | Pythonic LLM integration |

---

## 14. Security & Compliance Posture

### Security Architecture

| Control | Implementation | Status |
|---------|---------------|--------|
| Encryption at rest | AES-256 for all stored data | MVP |
| Encryption in transit | TLS 1.3 enforced; TLS 1.2 minimum | MVP |
| Secret management | HashiCorp Vault; API keys never stored in application config | MVP |
| BYOK | Bring Your Own Key for enterprise tenants | Phase 3 |
| mTLS between services | Istio service mesh for inter-service communication | Phase 2 |
| Zero prompt storage | Default off; opt-in with explicit configuration | MVP |
| Key rotation | Automated 90-day rotation for Vault-managed keys | Phase 2 |
| Secrets scanning | Detect API keys/tokens in prompts; block before forwarding | MVP |
| Tenant isolation | Kubernetes namespaces + Postgres schemas + Redis keyspace | MVP |
| Admin 2FA | TOTP required for all admin accounts | MVP |
| Audit log integrity | Cryptographic hash chain on all audit log entries | MVP |
| Penetration testing | Annual third-party pentest; quarterly automated scans | Phase 2 |
| SAST/DAST | Integrated in CI/CD pipeline | Phase 2 |
| SOC 2 readiness | Control framework implementation | Phase 3 |

### Compliance Roadmap

| Certification | Target Timeline | Business Unlock |
|---------------|----------------|-----------------|
| SOC 2 Type I | Month 6–9 | SMB and mid-market enterprise deals |
| GDPR Compliance | Month 9–12 | EU customers; data processing agreements |
| SOC 2 Type II | Month 12–18 | Large enterprise and regulated industry deals |
| ISO 27001 | Month 18–24 | European enterprise; government accounts |
| HIPAA-ready configurations | Month 18+ | Healthcare vertical |
| FedRAMP (future) | Year 3+ | US federal government |
| EU AI Act compliance documentation | Month 12 | EU enterprise; regulatory reporting |
| NIST AI RMF alignment | Month 12 | US enterprise governance requirements |

### Data Residency Options

| Region | Data Stays In | Compliant For |
|--------|---------------|---------------|
| US (default) | AWS us-east-1 / us-west-2 | US enterprise |
| EU | AWS eu-central-1 (Frankfurt) | GDPR, EU enterprise |
| APAC | AWS ap-southeast-1 (Singapore) | APAC enterprise |
| Custom | Customer-specified region | Government, regulated industries |

### Vendor Security Requirements

All LLM providers must satisfy:
- Data Processing Agreement (DPA) available
- SOC 2 Type II certified or equivalent
- GDPR-compliant data handling
- No training on customer data (enterprise tier)
- Dedicated tenancy available for sensitive workloads

---

## 15. Infrastructure & Deployment

### Deployment Models

| Model | Description | Target Customer |
|-------|-------------|-----------------|
| SaaS (Cloud-hosted) | Fully managed by AI Orchestrator; multi-tenant | Startups, mid-market |
| Single-tenant SaaS | Dedicated infrastructure per customer in our cloud | Enterprise with data sensitivity |
| Self-hosted (Kubernetes) | Customer deploys in their own Kubernetes cluster | Air-gapped, regulated industries |
| Hybrid | Gateway in customer VPC; analytics and dashboard SaaS | Financial services, healthcare |
| On-premise | Full deployment in customer datacenter | Government, defense |

### Kubernetes Architecture

```yaml
# Namespace per tenant (SaaS) or global namespace (self-hosted)
Deployments:
  - ai-gateway          (3–10 replicas, HPA enabled)
  - orchestration-engine (2–5 replicas)
  - metering-engine     (2–5 replicas)
  - security-middleware  (3–10 replicas, co-located with gateway)
  - wallet-service      (2–3 replicas, active-passive for safety)
  - analytics-ingester  (2–5 replicas)
  - dashboard-api       (2–3 replicas)
  - dashboard-frontend  (2–3 replicas)

StatefulSets:
  - postgresql          (primary + 2 replicas; managed preferred)
  - redis               (cluster mode; 3 primary + 3 replica)
  - clickhouse          (2-shard, 2-replica)

Services:
  - gateway-svc         (LoadBalancer or Ingress; external)
  - internal-svc-*      (ClusterIP; internal only)

Ingress:
  - NGINX or Traefik
  - TLS termination at ingress

Autoscaling:
  - HPA on gateway: CPU >70% → scale up; target 50 RPS/pod
  - KEDA on metering: scale based on queue depth
```

### Infrastructure as Code

- **Terraform modules:** VPC, EKS/GKE/AKS, RDS, ElastiCache, S3, Vault
- **Helm charts:** All Kubernetes workloads; versioned in GitHub
- **Pulumi alternative:** For TypeScript-first teams
- **GitOps:** ArgoCD for continuous deployment from Git

### High Availability Requirements

| Component | HA Strategy | RTO | RPO |
|-----------|-------------|-----|-----|
| Gateway | Multiple replicas + load balancer | <30s | 0 |
| Database (PostgreSQL) | Primary + standby with auto-failover | <60s | <1min |
| Cache (Redis) | Cluster mode with replica | <30s | ~0 |
| Analytics (ClickHouse) | 2-replica shard | <5min | <1min |
| Vault | HA mode with Raft consensus | <60s | 0 |
| Full region failure | Cross-region DNS failover (Route 53) | <5min | <5min |

### Disaster Recovery

| Scenario | Response | Recovery Steps |
|----------|----------|----------------|
| Database corruption | Point-in-time restore from snapshot | Restore from latest snapshot (<1h data loss); verify integrity; promote |
| Full datacenter failure | Cross-region failover | DNS TTL 60s; promote standby; redirect traffic |
| Data breach | Immediate: rotate all provider keys; revoke sessions; audit; notify | Forensic analysis; notify affected customers; regulatory disclosure |
| DDoS attack | Cloudflare WAF + rate limiting | Automatic mitigation; manual traffic shaping if needed |
| Ransomware (self-hosted) | Isolated backups; immutable S3 snapshots | Restore from clean backup; rebuild from IaC |

### Capacity Planning

| Traffic Level | Gateway Replicas | DB Size | Redis Memory | ClickHouse Storage |
|--------------|-----------------|---------|--------------|-------------------|
| 1K req/min | 2 | db.t4g.medium | cache.t4g.small | 500GB |
| 10K req/min | 5 | db.r6g.large | cache.r6g.large | 2TB |
| 100K req/min | 20 | db.r6g.4xlarge (+ replicas) | cache.r6g.4xlarge cluster | 10TB |
| 1M req/min | 80+ | Sharded PostgreSQL | Redis cluster (10+ nodes) | 50TB+ |

---

## 16. Technical Module Breakdown

| Module | Core Responsibilities | Key Milestone | Edge Cases |
|--------|----------------------|---------------|------------|
| Module 1: Gateway Layer | OpenAI-compatible API, auth, streaming pass-through, rate limiting, request tracing, connection pooling | 100% schema compatibility; <150ms P95 | Partial stream disconnect; schema drift; connection exhaustion |
| Module 2: Metering Engine | Token calculation (tiktoken), cost computation, streaming post-processing, async DB writes, real-time wallet deduction | ±0.1% billing accuracy vs. provider | Mid-stream wallet depletion; streaming estimate vs. actual reconciliation |
| Module 3: Wallet Service | Real-time balance checks, atomic deduction via DB transactions, budget policies, transfer workflows, chargeback export | Concurrent requests at scale without race conditions | Negative balance edge case; wallet reset race condition; transfer approval expiry |
| Module 4: Orchestration Engine | Policy evaluation, intent classification, model selection, failover detection, load balancing, experiment routing | <10ms routing decision latency | All providers down; policy conflict resolution; experiment statistical significance |
| Module 5: Security Middleware | Regex + NER PII scanning, entropy-based secret detection, OPA policy enforcement, prompt risk scoring | <10ms for requests ≤4K tokens | Large prompt partial scanning; encrypted content; prompt injection in tool results |
| Module 6: Semantic Cache | Embedding generation, vector similarity search, cache write/invalidation, TTL management | 30%+ cache hit rate on repetitive workloads | Cache poisoning; similarity threshold tuning; cache cold start |
| Module 7: Analytics Pipeline | ClickHouse ingestion (Kafka consumer), aggregation jobs, cost attribution, anomaly detection, forecast computation | Query latency <2s for 90-day range | Late-arriving events; backfill; partition management |
| Module 8: Prompt Registry | Version storage, diff computation, approval workflow, A/B routing integration, performance tracking | Prompt version history with rollback | Concurrent edits; approval workflow timeout; circular dependencies |
| Module 9: Dashboard & API | Next.js frontend, REST API, GraphQL analytics, WebSocket for real-time updates, admin controls | Real-time budget gauge; <2s page load | WebSocket reconnection; large dataset pagination; concurrent admin operations |
| Module 10: Notification Engine | Slack/Teams/email/webhook fanout, alert deduplication, escalation ladder, digest aggregation | Alert delivered within 30s of trigger | Notification loop prevention; rate limiting notifications; channel unavailability |

---

## 17. Customer Journey & Onboarding

### First-Run Experience (Day 0)

```
Step 1: Sign Up (5 minutes)
  → Email/SSO registration
  → Organization name + team size
  → Estimated monthly AI spend (for plan recommendation)
  → Select cloud region (data residency)

Step 2: Integration (30 minutes)
  → Generate API key
  → Copy one-liner: export OPENAI_BASE_URL="https://gateway.ai-orchestrator.io/v1"
  → Verify connection: test request via dashboard "Ping Test"
  → (Optional) SDK installation guide for Python/Node/Go

Step 3: First Insight (24 hours)
  → Dashboard auto-populates with real traffic data
  → Email: "Your first 24 hours — here's what we found"
  → Show: total spend, top models used, top teams/users
  → Highlight: potential savings from caching or cheaper model alternatives

Step 4: First Control (Day 2–5)
  → Guided setup: "Set your first team wallet limit"
  → Configure Slack alerts
  → Enable PII detection (one toggle)

Step 5: First Optimization (Week 2)
  → System surfaces: "Enable smart routing — save estimated $X/month"
  → Enable semantic cache for top-traffic endpoints
  → First routing experiment wizard

Step 6: Enterprise Expansion (Month 2–3)
  → SSO configuration wizard
  → FinOps export setup (Snowflake / CSV)
  → IDE extension rollout guide for dev team
  → Compliance review meeting with customer security team
```

### Onboarding Checklist (Tracked in Dashboard)
- [ ] First API call through gateway
- [ ] Wallet limit configured for at least one team
- [ ] Slack integration connected
- [ ] PII detection enabled
- [ ] First budget alert triggered and acknowledged
- [ ] Smart routing enabled
- [ ] Semantic cache enabled
- [ ] SSO configured (enterprise)
- [ ] Second team or department onboarded
- [ ] First chargeback export generated

### Time to Value Targets

| Milestone | Target Time |
|-----------|-------------|
| First request through gateway | <1 hour post-signup |
| Cost visibility dashboard live | <24 hours |
| First budget alert sent | <1 week |
| First cost savings realized | <2 weeks |
| Full team onboarded | <1 month |
| Finance team using chargeback report | <6 weeks |

---

## 18. Go-To-Market Strategy

### GTM Philosophy: Wedge Adoption

> **Primary Hook:** "Reduce your AI spend 30% in 7 days — without changing a single line of code." Lead with cost reduction. Governance and economy follow once the platform is integrated.

### Phase 1 — Developer-Led Adoption (Month 1–6)

- **Offer:** Free tier (up to $10K/month managed spend; 100K requests/month)
- **Value:** Immediate cost tracking, unified endpoint, zero vendor lock-in
- **Goal:** Get integrated before budget conversations — become default infrastructure
- **Channels:** Hacker News, dev Twitter/X, subreddits (r/LocalLLaMA, r/MachineLearning), Product Hunt

### Phase 2 — Platform Team Expansion (Month 4–12)

- **Upsell:** Wallet controls, Slack alerts, routing engine, semantic caching
- **Target:** Head of Platform, FinOps lead, VP Engineering
- **Trigger:** First end-of-month invoice review, or first unexpected spend spike
- **Motion:** Bottom-up — developer champion escalates to platform/FinOps

### Phase 3 — Enterprise Expansion (Month 9–24)

- **Sell to:** CTO, CFO, CISO, Head of Compliance
- **Motion:** Top-down procurement + bottom-up champion
- **Requirements:** SOC 2 Type II, enterprise MSA, SSO, data processing agreement
- **Deal size:** $50K–$500K ARR

### Channel Strategy

| Channel | Tactics | Target |
|---------|---------|--------|
| DevRel Content | "How we reduced AI spend by 40%" technical blog posts; YouTube tutorials | Developers |
| Open Source | Release gateway layer as OSS; sell wallet + dashboard + enterprise features | Developer trust + pipeline |
| Partnerships | AI-native SaaS (Notion AI, Intercom, HubSpot AI feature teams) | Mid-market referrals |
| Conferences | AI Infra Summit, KubeCon, re:Invent, Money20/20 (FinOps angle) | Enterprise buyers |
| Product Hunt | Launch the open-source gateway; drive developer signups | Early adopters |
| LinkedIn | FinOps and AI governance content for CFO/CTO audience | Enterprise buyers |
| Analyst Relations | Brief Gartner, Forrester, IDC on new category | Enterprise validation |
| System Integrators | Partner with Accenture, Deloitte, Cognizant for enterprise deployments | Large enterprise |

### Messaging by Persona

| Persona | Headline | Core Message |
|---------|----------|--------------|
| Developer | "One line of code to control your AI costs" | Zero friction integration; immediate visibility |
| Platform Lead | "Finally, AI FinOps that actually works" | Wallet controls; multi-team governance |
| CFO | "AI spend you can predict and justify" | Budget enforcement; chargeback; ROI measurement |
| CISO | "Governance for every AI request, automatically" | PII protection; audit logs; policy enforcement |
| CTO | "Stop vendor lock-in. Route intelligently." | Multi-provider; resilience; cost optimization |

---

## 19. Pricing & Business Model

### Tier Structure

| Tier | Monthly Price | Managed Spend | Requests | Features |
|------|--------------|---------------|----------|----------|
| Free | $0 | Up to $10K | 100K/month | Gateway, basic dashboard, 1 team wallet |
| Starter | $499/month | Up to $50K | 1M/month | + Smart routing, Slack alerts, 5 team wallets |
| Growth | $1,999/month | Up to $200K | 10M/month | + Semantic caching, IDE extension, SSO, 20 wallets |
| Enterprise | Custom | Unlimited | Unlimited | + Full policy engine, FinOps integrations, SOC 2, SLA, dedicated CSM |

### Monetization Options

| Model | Structure | Pros | Cons |
|-------|-----------|------|------|
| A: % of Managed Spend | 3–7% of AI spend routed through platform | Aligns incentives; scales with customer growth | Perceived as a "tax"; churn when spend drops |
| B: Platform Fee + Usage Tier | Base license + per-request volume pricing | Predictable for customer and us | Harder to land at zero |
| **C: Hybrid (Recommended)** | Minimum platform fee + % of managed spend above tier | Protects floor; scales with growth; ROI self-evident | Complexity in contracts |
| D: Cost Savings Share | % of verified cost savings delivered | Fully aligned incentives | Hard to measure; payment delay |

### Unit Economics

| Metric | Target |
|--------|--------|
| Average contract value (ACV) | $24K (Growth) → $150K (Enterprise) |
| Gross margin | >80% at scale |
| Infrastructure cost per request | <$0.0001 |
| LTV/CAC ratio | >5x |
| Net Revenue Retention (NRR) | >120% (expansion via managed spend growth) |
| Time to payback | <12 months |

> **ROI Framing for Customers:** Customer spending $100K/month on AI, saving 40% ($40K/month), paying $5K/month → 8x ROI. First question in any deal: "How much are you spending on AI today?"

### Pricing Psychology

- Free tier removes all friction for developer adoption
- Starter tier priced below "rounding error" for a company running $50K/month in AI
- Growth tier justified by first month of semantic caching savings alone
- Enterprise: price based on value delivered, not cost to serve

---

## 20. Competitive Differentiation

| Dimension | Traditional AI Setup | AI Orchestrator |
|-----------|---------------------|-----------------|
| Integration | Hard-coded SDKs; re-engineer to switch providers | Unified API; swap base URL; zero code change |
| Billing | End-of-month invoice shock | Real-time wallet enforcement; predictive forecasting |
| Model Selection | Manual; based on familiarity | Intelligent routing with cost arbitrage |
| Governance | None | AI firewall middleware with OPA policy-as-code |
| ROI | No tracking | Feature-level cost attribution + ROI scoring engine |
| Resilience | Single-provider dependency; manual failover | Automatic multi-provider failover in <500ms |
| Observability | Provider dashboards only | Embedded in Datadog/Grafana; 30+ metrics |
| Security | API key in `.env`; no PII scanning | Vault-managed keys; PII detection; audit chain |
| Developer Experience | No cost feedback during development | Real-time cost in IDE; model cost comparison |
| Finance Integration | Manual export + spreadsheets | Snowflake/SAP/Oracle direct integration |
| Compliance | No audit trail | Immutable audit log with cryptographic chain |
| Prompts | Hardcoded in application | Versioned prompt registry with rollback |

---

## 21. Success Metrics & KPIs

### North Star Metric
> **Total AI Spend Managed Through Platform ($ MRR equivalent)**
>
> Measures: adoption depth, customer trust, platform centrality, revenue generation.

### Secondary Metrics

**Product Health:**
- Weekly Active Organizations (WAO)
- Requests per day (gateway throughput)
- Cache hit rate (%)
- Mean routing decision latency (ms)
- Policy enforcement events per day

**Customer Value:**
- Average cost savings per customer (% and $)
- Time to first cost savings event
- Wallet adoption rate (% of organizations with wallet limits set)
- Alert-to-action conversion rate (% of budget alerts that result in action)

**Business:**
- Monthly Recurring Revenue (MRR)
- Net Revenue Retention (NRR) — target >120%
- Customer Acquisition Cost (CAC)
- LTV/CAC ratio — target >5x
- Churn rate — target <5% annually

### Technical KPIs

| KPI | Target | Measurement Method |
|-----|--------|-------------------|
| Proxy latency overhead P50 | <50ms | Real-time histogram |
| Proxy latency overhead P95 | <150ms | Real-time histogram |
| Proxy latency overhead P99 | <500ms | Real-time histogram |
| Platform availability | 99.9% (43.8 min/month downtime) | Uptime monitoring |
| Cache hit rate | >30% at steady state | ClickHouse daily aggregate |
| Failover recovery time | <5 seconds | Automated failover test |
| Metering accuracy | ±0.1% vs. provider billing | Monthly reconciliation |
| Policy evaluation latency | <10ms P99 | Per-request timing |
| PII detection false negative rate | <0.5% | Monthly benchmark test |
| Audit log chain integrity | 100% | Daily verification job |

### Business KPIs

| KPI | Target | Timeline |
|-----|--------|----------|
| AI spend reduction for customers | 25–60% vs. unmanaged | Within 30 days of optimization features |
| AI traffic centralized per org | 100% of LLM traffic | Within 60 days of onboarding |
| Budget overrun variance | <2% vs. configured limits | At all times |
| Time to first value | <24 hours post-integration | Onboarding |
| NPS score | >50 | Quarterly |

---

## 22. Roadmap

### 90-Day Build Plan (Investor-Ready MVP)

> The goal is a functional, deployable product that demonstrates the wedge value.

| Month | Deliverables | Success Criteria |
|-------|-------------|-----------------|
| Month 1 | OpenAI-compatible proxy; token counting (tiktoken); cost calculation; provider abstraction (OpenAI + Anthropic); basic request logging; API key auth | First external customer routing 100% of AI traffic through gateway |
| Month 2 | Hard wallet limits; real-time deduction; admin dashboard (cost per user/team); basic Slack budget alerts; PostgreSQL wallet schema; 2-provider failover | Customer reports zero bill surprises; first budget alert fired |
| Month 3 | Cost-based routing; failover automation; basic semantic caching; budget threshold alerts; CSV chargeback export; basic PII detection | First customer reports 20%+ cost reduction; finance team uses chargeback export |

### Full Product Roadmap

| Phase | Timeline | Focus | Key Deliverables |
|-------|----------|-------|-----------------|
| Phase 1 — MVP | Month 1–4 | Gateway + Metering + Wallet | OpenAI-compatible gateway, token metering, hard wallet limits, 2-provider support, basic dashboard |
| Phase 2 — Control | Month 4–6 | Communication + Governance | Slack/Teams app, budget transfers, multi-level wallet hierarchy, soft limits, PII detection, basic OPA policies |
| Phase 3 — Optimize | Month 6–9 | Orchestration + Caching | Smart routing, semantic caching, failover automation, routing experiments, cost arbitrage, 5+ providers |
| Phase 4 — Intelligence | Month 9–12 | Analytics + Enterprise | AI ROI engine, usage classification, IDE extension, advanced analytics, SSO/SCIM, SOC 2 Type I |
| Phase 5 — Moat | Month 12–18 | Defensibility Features | Prompt registry, full policy engine, FinOps integrations (Snowflake/SAP), multi-region residency, predictive forecasting |
| Phase 6 — Platform | Month 18–24 | Ecosystem + Scale | AI credit marketplace, partner API, open-source community gateway, benchmarking platform, AI compliance standard |

### Feature Flags for Safe Rollout

All new features roll out via internal feature flags:
1. **Internal dogfooding** (AI Orchestrator team) — 1 week
2. **Beta customers** (10 design partners) — 2 weeks
3. **General availability** — gradual % rollout with automated rollback triggers

---

## 23. Pilot & Beta Program

### Design Partner Requirements

Target: 5–10 design partners before general availability.

**Ideal design partner profile:**
- Spending $20K–$200K/month on AI APIs
- Engineering or platform team of 5+ people
- Willing to provide weekly feedback calls
- Willing to be a reference customer (logo + case study)
- Represents diverse verticals: SaaS, fintech, healthcare, e-commerce

### Design Partner Offer

| What They Get | What We Get |
|--------------|-------------|
| 6 months free on Growth plan ($12K value) | Weekly feedback sessions (1 hour/week) |
| Dedicated Slack channel with founding team | Permission to use logo and anonymized metrics |
| Direct influence on roadmap | Reference call participation (1/quarter) |
| Priority support (4-hour SLA) | Case study participation after 3 months |
| Early access to all new features | Introduction to 2 potential customers |

### Beta Success Criteria

Before general launch, each design partner must confirm:
- [ ] Gateway is routing >80% of their AI traffic
- [ ] At least one wallet limit configured and enforced
- [ ] At least one budget alert fired and actioned
- [ ] NPS score ≥7/10 from at least one stakeholder
- [ ] No critical data or security incidents during beta

### Beta Metrics Tracked

- Integration completion rate (target: 100% in week 1)
- Daily active usage (target: every weekday)
- Features adopted by week 4 (target: gateway + wallet + alerts)
- Issues reported per customer (target: <3 critical; <10 total)
- Churn/dropout from beta (target: <20%)

---

## 24. Risks & Mitigation

| Risk | Probability | Severity | Mitigation | Owner |
|------|-------------|----------|------------|-------|
| Added request latency exceeds 150ms P95 | Medium | High | Async architecture; co-locate middleware; Go routines; benchmark every PR | Engineering |
| Model pricing volatility | High | Medium | Dynamic pricing config with real-time feeds; cost arbitrage auto-adjusts | Product |
| Provider outage (extended) | Low | High | Multi-provider failover; <5s recovery; circuit breaker; manual override UI | Engineering |
| Developer bypasses gateway | Medium | Medium | IDE integration makes gateway easiest path; API key policy enforcement; shadow AI detection | Product |
| Semantic cache poisoning | Low | High | Similarity threshold + content validation + confidence scoring; easy invalidation | Engineering |
| AI misuse spike | Low | Medium | Circuit breaker; anomaly detection; manual suspension capability | Security |
| Enterprise security approval delay | High | High | Invest in SOC 2 early; security documentation package; DPA templates ready | GTM |
| Token metering inaccuracy vs. provider | Medium | Medium | Monthly reconciliation; <0.1% tolerance; automated drift detection | Engineering |
| Key competitor enters with VC backing | Medium | High | Speed to market; open-source moat; design partner lock-in; SOC 2 differentiation | Strategy |
| Regulatory change (EU AI Act enforcement) | Low | Medium | Monitor regulatory developments; build compliance features ahead of mandates | Legal |
| Founding team execution risk | Medium | High | Clear ownership; weekly OKR reviews; early key hires; advisor network | CEO |
| Data breach | Low | Critical | Penetration testing; zero-prompt-storage default; Vault; incident response plan | Security |
| Provider changes OpenAI API schema | Medium | High | Schema versioning; compatibility test suite; abstract provider connectors | Engineering |

---

## 25. Moat Strategy & Defensibility

### Moat Layers (Compound Over Time)

| Layer | Type | Time to Build | Switching Cost |
|-------|------|---------------|----------------|
| Traffic Centralization | Control moat | Immediate | High — removing requires redirecting all AI traffic |
| Historical Dataset | Data moat | 3–6 months | Very high — unique cost + quality + routing data |
| Policy Engine Lock-In | Workflow moat | 1–3 months | High — custom Rego policies embedded in operations |
| Wallet Dependency | Financial moat | 2–4 months | High — integrated into finance team chargeback processes |
| Predictive Intelligence | Data network effect | 6–12 months | Very high — accuracy improves with customer-specific history |
| Integration Depth | Ecosystem moat | 3–12 months | Very high — SSO + FinOps + Observability creates multi-stakeholder stickiness |
| Open-Source Community | Community moat | 12–24 months | Reputational — hardest to replicate |
| Prompt Registry | Workflow moat | 1–2 months | High — versioned prompts embedded in development workflow |

### Moat Acceleration Strategies
- Publish benchmark data: "AI Orchestrator routes 10B+ tokens/month — here's what we've learned"
- Build provider partnerships: preferred routing rates for volume commitments
- Standard-setting: contribute to emerging AI governance standards (NIST AI RMF)
- Community: open-source the gateway; sell the intelligence on top

---

## 26. SLA Definitions & Breach Remediation

### Service Level Agreements

| Metric | Commitment | Measurement Window | Exclusions |
|--------|-----------|-------------------|------------|
| Platform availability | 99.9% | Monthly | Scheduled maintenance (communicated 48h in advance); provider-caused outages |
| Gateway latency P95 | <150ms overhead | Monthly | Requests >100K tokens; streaming requests |
| Failover time | <5 seconds | Per event | If all providers simultaneously down |
| Alert delivery | <30 seconds | Per event | Slack/email infrastructure failures |
| Support response (Enterprise) | <4 hours (P1), <8 hours (P2) | Business hours + on-call | — |
| Audit log availability | 99.99% | Monthly | — |
| Metering accuracy | ±0.1% vs. provider billing | Monthly | Provider billing errors |

### Downtime Definition
- **Downtime:** >1% of requests returning 5xx errors for >2 consecutive minutes
- **Degraded:** P95 latency >500ms for >5 consecutive minutes
- **Partial outage:** Any feature unavailable for >5 minutes

### Breach Remediation

| Availability Achieved | Credit |
|-----------------------|--------|
| 99.0% – 99.9% | 10% of monthly fee |
| 95.0% – 99.0% | 25% of monthly fee |
| <95.0% | 50% of monthly fee |

**Credits are:**
- Applied to next month's invoice (not cash refund)
- Subject to customer reporting within 30 days
- Capped at 50% of monthly fee in any calendar month
- Not applicable during beta period

### Scheduled Maintenance
- Communicated ≥48 hours in advance via status page, email, and Slack
- Target maintenance window: Sundays 02:00–04:00 UTC
- Maximum planned downtime: 4 hours/month (not counted against SLA)

---

## 27. Billing Reconciliation & Metering Accuracy

### How Metering Works

```
1. REQUEST ARRIVES
   ↓
2. TOKEN PRE-ESTIMATION
   → Use tiktoken (OpenAI) or provider-specific tokenizer
   → Estimate input tokens from prompt
   → Reserve estimated output cost from wallet (based on max_tokens)
   ↓
3. PROVIDER RESPONSE RECEIVED
   → Count actual output tokens from response
   ↓
4. SETTLE BILLING
   → Actual input tokens (from response metadata if available, else re-count)
   → Actual output tokens
   → Calculate final cost: (input × input_rate) + (output × output_rate)
   → Adjust wallet: release reservation, deduct actual cost
   ↓
5. LOG TO CLICKHOUSE (async, <500ms)
```

### Reconciliation Process

**Daily:**
- Sum our metered costs per provider
- Compare to provider usage API (if available: OpenAI, Anthropic have usage endpoints)
- Flag any day where variance >0.5%

**Monthly:**
- Download provider invoices on 1st of month
- Run reconciliation report: our total vs. provider invoice per line item
- Investigate and explain all variances >0.1%
- Publish reconciliation report to enterprise customers on request

### Known Variance Sources

| Source | Expected Variance | Mitigation |
|--------|------------------|------------|
| Tokenizer version mismatch | ±0.1–0.5% | Pin tiktoken version; update on provider notice |
| Provider minimum billing increments | ±0.01% | Model per-provider billing granularity |
| Streaming partial responses (client disconnect) | ±0.1% | Count tokens emitted before disconnect |
| Image / audio tokens (multimodal) | ±1% | Use provider-specific counting rules |
| Function call overhead tokens | ±0.5% | Include tool definition tokens in count |

### Customer Billing Guarantees
- If our metering overcharges a customer vs. actual provider usage: credit 100% of overcharge
- If our metering undercharges: absorb the difference (do not back-bill)
- Monthly reconciliation report available to enterprise customers on request

---

## 28. Support Tiers & Customer Success

### Support Tiers

| Tier | Plan | Channels | Response Time | Coverage |
|------|------|----------|---------------|----------|
| Community | Free | GitHub Issues, Discord | Best effort | — |
| Standard | Starter | Email + Docs | <24 hours P1, <48 hours P2 | Business hours |
| Priority | Growth | Email + Slack Connect | <8 hours P1, <24 hours P2 | Business hours |
| Enterprise | Enterprise | Email + Slack + Phone | <4 hours P1, <8 hours P2 | 24/7 for P1 |
| Dedicated | Enterprise+ | Named CSM + Slack + Phone | <1 hour P1 | 24/7 |

### Priority Levels

| Priority | Definition | Examples |
|----------|-----------|---------|
| P1 — Critical | Platform down; data breach suspected; wallet enforcement not working | Gateway returning 5xx for all requests; billing dramatically wrong |
| P2 — High | Feature broken; significant performance degradation | Routing not working; Slack alerts not firing |
| P3 — Medium | Feature behaving unexpectedly; non-critical bug | Dashboard showing incorrect data; slow query |
| P4 — Low | Question; feature request; documentation | How do I configure X? Can you add feature Y? |

### Customer Success Playbook

**Onboarding (Month 0–1):**
- Welcome call within 24 hours of sign-up (Growth+)
- Integration review call at day 7
- First value confirmation at day 14
- 30-day check-in: confirm savings realized; expand wallet setup

**Expansion (Month 2–6):**
- Monthly business review (Enterprise)
- Quarterly executive business review (Enterprise+)
- Proactive: "Your team X is not using smart routing — enable to save ~$Y/month"
- Proactive: "You have 3 teams not yet onboarded — here's the invite flow"

**Retention (Ongoing):**
- Quarterly NPS survey
- Annual contract renewal 90 days before expiry
- Escalation path: CSM → VP Customer Success → CRO

### Documentation Requirements

| Doc Type | Audience | Format |
|----------|----------|--------|
| Quick Start Guide | Developers | Docs site + in-product |
| API Reference | Developers | OpenAPI / Swagger |
| SDK References | Developers | Per-language docs site |
| Architecture Guide | Platform Engineers | Docs site |
| Security Whitepaper | Security / Compliance | PDF download |
| Deployment Guide (Self-hosted) | DevOps | Docs site + GitHub |
| Admin Guide | Platform Leads | Docs site |
| FinOps Integration Guide | FinOps Teams | Docs site |
| Compliance Package | Compliance Officers | PDF (SOC 2 report, DPA, etc.) |

---

## 29. Partner & Reseller Ecosystem

### Partnership Tiers

| Tier | Type | Revenue Share | Requirements |
|------|------|--------------|--------------|
| Technology Partner | Integration / Ecosystem | None (mutual value) | Published integration; co-marketing |
| Referral Partner | Lead generation | 15% of first-year ARR | Signed referral agreement |
| Reseller | Full resale | 25–35% margin | Training + certification |
| Strategic Partner | OEM / White-label | Custom | Deep technical + go-to-market alignment |
| System Integrator | Implementation | 20% of ARR influenced | Certified implementation team |

### Priority Technology Partners

| Category | Priority Partners | Integration Type |
|----------|-----------------|-----------------|
| LLM Providers | Anthropic, Cohere, Mistral | Co-marketing; preferred routing |
| Cloud Platforms | AWS, Azure, GCP | Marketplace listings |
| Observability | Datadog, Grafana Labs | Native integration + joint marketing |
| Identity | Okta | SSO integration + partner portal |
| FinOps | Apptio, Cloudability | Joint solution brief |
| Consulting | Accenture, Deloitte | Reseller + implementation |

### Marketplace Listings
- AWS Marketplace — SaaS listing + CloudFormation quick-start
- Azure Marketplace — SaaS listing
- GCP Marketplace — SaaS listing
- Okta Integration Network (OIN) — SSO integration catalog
- Slack App Directory — Slack app listing
- Datadog Marketplace — Integration listing

---

## 30. Open Source Strategy

### What to Open Source

| Component | License | Rationale |
|-----------|---------|-----------|
| Gateway layer (core proxy) | Apache 2.0 | Drive adoption; become industry standard; community contributions |
| OpenAI provider connector | Apache 2.0 | Lowest barrier to entry; showcase quality |
| CLI tool | MIT | Developer experience; community growth |
| Helm charts | Apache 2.0 | Self-hosted deployment; enterprise trust |
| Terraform modules | Apache 2.0 | IaC community; enterprise evaluation |
| Benchmark suite | Apache 2.0 | Establish credibility; community validation |

### What to Keep Closed (Enterprise Moat)

- Wallet & economy engine
- Intelligent orchestration engine (routing logic)
- Semantic caching service
- AI policy engine integration
- Analytics and BI layer
- Dashboard and admin UI
- Notification engine
- Prompt registry

### Open Source Community Strategy
- GitHub organization: `ai-orchestrator`
- Weekly release cadence for OSS components
- Public roadmap on GitHub Projects
- Discord community server
- Monthly community calls
- Contributor recognition program
- "Powered by AI Orchestrator" badge for community projects
- Annual AI infrastructure open source conference (Year 2+)

---

## 31. Team, Hiring & Execution Risk

### Founding Team Gaps to Fill (Priority Order)

| Role | Priority | When to Hire | Why Critical |
|------|----------|-------------|--------------|
| Staff Go Engineer (Gateway) | Immediate | Month 1 | Core gateway performance is the product |
| Product Designer | Month 1–2 | Month 2 | Dashboard UX is adoption driver |
| Security Engineer | Month 2–3 | Month 3 | Enterprise sales gate; SOC 2 requirement |
| DevRel Engineer | Month 3–4 | Month 4 | Open source + community = distribution |
| Enterprise AE (Account Executive) | Month 4–6 | Month 6 | Revenue; takes 3–6 months to ramp |
| Customer Success Manager | Month 6 | Month 6 | Retention and expansion |
| Staff ML Engineer | Month 6–9 | Month 9 | Routing intelligence; classification; forecasting |
| VP Engineering | Month 9–12 | Month 12 | Scale engineering org |

### Execution Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Founder dependency (bus factor) | Document all critical systems; cross-train; advisory board |
| Slow enterprise sales cycle | Developer self-serve + free tier creates pipeline without sales |
| Feature scope creep | Strict quarterly OKRs; "out of scope" section enforced |
| Technical debt accumulation | Dedicated 20% sprint capacity for refactoring after MVP |
| Hiring delays | Pre-build recruiter relationships; compensation benchmarking |

### Advisors Needed
- CTO or VP Eng from enterprise SaaS (procurement knowledge)
- FinOps expert (Apptio / Cloudability alumni)
- Enterprise security architect (SOC 2 + CISO relationships)
- LLM provider insider (pricing dynamics, partnership access)
- Enterprise GTM expert (Datadog / Snowflake alumni preferred)

---

## 32. Long-Term Vision

### Platform Evolution (3-Year Arc)

```
Year 1: AI Cost Control & Gateway
  → Centralize traffic; enforce budgets; deliver 30%+ savings
  → Category creation: "AI FinOps"

Year 2: AI Intelligence Layer
  → Optimize quality + cost simultaneously
  → Predictive spend management
  → Policy governance at enterprise scale
  → Category expansion: "AI Control Plane"

Year 3: Enterprise AI Operating System
  → Become standard infrastructure for enterprise AI
  → Credit marketplace; cross-org benchmarking
  → Regulatory compliance standard
  → Category leadership: "Enterprise AI OS"
```

### Platform Vision (5-Year)
- **AI ROI Intelligence Engine** — every dollar of AI spend linked to revenue or productivity outcomes
- **Cross-Provider Performance Benchmark** — industry-standard quality and cost comparison; published quarterly
- **Enterprise AI Compliance Standard** — become the reference architecture for regulated AI usage
- **Internal AI Credit Marketplace** — departments trade, transfer, and bid for AI resources in real-time
- **Predictive AI Spend Simulator** — model cost impact of architectural decisions before committing
- **AI Governance Certificate** — certify organizations as "AI Orchestrator Governed" (like SOC 2 for AI)

### Category Evolution

```
LLM Gateway (proxy)
  → AI Control Plane (govern + optimize)
    → Enterprise AI Financial OS (predict + measure + trade)
      → AI Governance Standard (certify + benchmark)
```

**Controlling today:** Cost + Routing + Security
**Must also control:** Quality + Policy + Prediction + Financial Behavior

### Strategic Exit Scenarios

| Acquirer Type | Examples | Strategic Rationale | Likely Timeline |
|---------------|----------|--------------------|-----------------|
| Cloud Hyperscaler | AWS, Azure, GCP | Add governance + FinOps to cloud AI services | Year 3–5 |
| DevOps / Observability Platform | Datadog, Dynatrace, New Relic | Expand into AI infrastructure control | Year 2–4 |
| LLM Provider | Anthropic, Cohere, Mistral | Acquire customer relationships + multi-provider intelligence | Year 3–5 |
| FinOps Platform | Apptio, Cloudability | Add AI spend to cloud cost management suite | Year 2–4 |
| Enterprise Software | ServiceNow, Salesforce | AI governance as enterprise platform feature | Year 4–6 |
| IPO | — | If category leadership achieved | Year 5–7 |

---

## 33. Assumptions Log

All assumptions underpinning this PRD. Must be validated with data before Series A.

| # | Assumption | Risk if Wrong | Validation Method | Status |
|---|------------|--------------|-------------------|--------|
| A1 | Enterprises will route 100% of AI traffic through a third-party proxy | If <50% adoption, revenue and moat both fail | Design partner interviews; integration completion rate | Unvalidated |
| A2 | 30–50% cost reduction is achievable via routing + caching for most workloads | Core value prop fails | Beta program with 5 design partners; A/B test | Unvalidated |
| A3 | Enterprises will pay 3–5% of managed AI spend for governance | If price sensitivity is higher, unit economics break | Pricing experiment during beta | Unvalidated |
| A4 | <150ms latency overhead is acceptable to enterprise customers | If latency sensitivity higher, adoption blocked | Latency benchmark in beta; customer interviews | Unvalidated |
| A5 | Finance teams will use chargeback exports (vs. building their own) | FinOps stickiness lower than projected | Design partner FinOps interviews | Unvalidated |
| A6 | Developer adoption leads to platform team purchase | If grassroots → top-down motion doesn't work, CAC rises | Track conversion from free → paid in beta | Unvalidated |
| A7 | LLM provider pricing will remain volatile enough to make arbitrage valuable | If providers lock in pricing, arbitrage moat weakens | Monitor pricing changes quarterly | Ongoing |
| A8 | Semantic caching achieves 30%+ hit rate for enterprise workloads | If workloads too varied, cache ROI insufficient | Beta cache hit rate measurement | Unvalidated |
| A9 | SOC 2 Type II is the primary enterprise security gate (vs. GDPR, ISO 27001) | May need multiple certs faster than planned | Customer discovery with 20 enterprise security leads | Unvalidated |
| A10 | Go/Rust architecture achieves <150ms P95 | If performance insufficient, architecture rethink required | Load test at 10K req/min in staging | Unvalidated |

---

## 34. Out of Scope (This Phase)

Stay firmly in the **"AI traffic control + financial governance"** lane. The following are intentionally deferred to avoid scope creep and maintain focus:

| Out of Scope | Why Deferred | When to Revisit |
|-------------|--------------|-----------------|
| Custom model training infrastructure | Different buyer, different market | Year 3+ |
| Fine-tuning hosting | Competed by together.ai, Replicate | Year 3+ |
| Vector database as a product | Competed by Pinecone, Weaviate | Never (use as integration) |
| Full MLOps platform | Competed by Weights & Biases, MLflow | Never |
| Consumer-facing AI products | Different distribution, margin structure | Never |
| General API gateway features | No LLM-specific differentiation | Never |
| Model training compute | Infrastructure company; different economics | Never |
| Proprietary LLM development | Compete with providers = destroy partnerships | Never |

---

## 35. Glossary

| Term | Definition |
|------|------------|
| **AI Control Plane** | The centralized infrastructure layer that governs all AI traffic, costs, and policies across an organization |
| **Budget Breach** | When actual spending reaches or exceeds the configured wallet limit |
| **Cache Hit** | A response served from semantic cache rather than calling an LLM provider |
| **Chargeback** | Allocating AI costs to specific business units or cost centers for internal billing |
| **Circuit Breaker** | Automatic suspension of AI access when usage exceeds a configured spike threshold |
| **Cost Arbitrage** | Automatically routing to the cheapest provider offering equivalent quality and SLA |
| **Cost Center** | An organizational unit (team, department) to which AI costs are attributed |
| **Data Residency** | Ensuring that data (prompts, responses, logs) is stored and processed within a specific geographic region |
| **Design Partner** | An early customer who provides feedback and helps shape the product in exchange for early access |
| **Failover** | Automatically rerouting traffic from a degraded or unavailable provider to an available one |
| **FinOps** | Cloud Financial Operations — applying financial accountability to cloud infrastructure spend; applied here to AI spend |
| **Hard Limit** | A wallet limit that blocks all requests once reached; no spending beyond the limit |
| **ICP** | Ideal Customer Profile — the characteristics of the customer most likely to buy and retain |
| **Immutable Audit Log** | A log that cannot be modified or deleted, secured with a cryptographic hash chain |
| **Intent Routing** | Classifying the purpose of an AI request (e.g., code generation, summarization) and routing to the model best suited for that category |
| **LLM** | Large Language Model — AI models that generate text (GPT-4o, Claude, Gemini, etc.) |
| **Metering** | Counting tokens consumed by each request for billing and cost attribution |
| **Model Efficiency Index** | A composite score of output quality divided by cost for a given model and task type |
| **Multi-tenancy** | Architecture where multiple organizations share the same infrastructure with complete data isolation |
| **OPA** | Open Policy Agent — a general-purpose policy engine using the Rego policy language |
| **Orchestration Engine** | The component that decides how to route each AI request based on cost, quality, compliance, and availability rules |
| **Overdraft** | Allowing spending beyond the hard wallet limit by a configured amount; requires explicit opt-in |
| **P95 Latency** | The latency at the 95th percentile — 95% of requests complete faster than this value |
| **PII** | Personally Identifiable Information — data that can identify an individual (name, email, SSN, etc.) |
| **Policy-as-Code** | Governance rules expressed as code (Rego/OPA) that can be version-controlled and automatically enforced |
| **Prompt Registry** | A versioned store of prompts used across applications, with history, rollback, and approval workflows |
| **Provider** | An LLM API provider: OpenAI, Anthropic, Gemini, Cohere, Mistral, etc. |
| **Rego** | The policy language used by OPA for writing governance rules |
| **Routing Rule** | A configured rule that determines how AI traffic is directed based on conditions (model, team, cost, time, etc.) |
| **Semantic Cache** | A cache that returns stored responses for requests with similar meaning, not just identical text |
| **Semantic Similarity** | A measure (0–1) of how similar two pieces of text are in meaning, computed via vector embeddings |
| **Soft Limit** | A wallet threshold that triggers alerts but allows spending to continue (unlike a hard limit) |
| **SSO** | Single Sign-On — authentication via an identity provider (Okta, Entra ID, etc.) |
| **SCIM** | System for Cross-domain Identity Management — protocol for automated user provisioning |
| **TAM / SAM / SOM** | Total Addressable Market / Serviceable Addressable Market / Serviceable Obtainable Market |
| **Tiktoken** | OpenAI's tokenizer library used to count tokens before sending to the API |
| **Token** | The basic unit of text processed by LLMs; approximately 0.75 words on average |
| **Token Economy** | The managed system of token budgets, allocations, and transfers within an organization |
| **Vault** | HashiCorp Vault — a secrets management system used to store API keys securely |
| **Vector Embedding** | A numerical representation of text in high-dimensional space, used for semantic similarity computation |
| **Wallet** | A budget allocation at any organizational level (user, team, department, org) with configurable limits |
| **BYOK** | Bring Your Own Key — enterprise customers provide their own encryption keys for data at rest |
| **OTel** | OpenTelemetry — open-source observability framework for distributed tracing, metrics, and logs |
| **NRR** | Net Revenue Retention — measures revenue growth from existing customers including expansion and churn |
| **gRPC** | Google Remote Procedure Call — high-performance, open-source RPC framework using Protocol Buffers |
| **SSE** | Server-Sent Events — protocol for streaming responses from server to client (used for LLM streaming) |

---

*AI Orchestrator — Confidential. For Investor, Executive & Engineering Review.*
*Version 3.0 — Last updated February 2026*
*This is a living document — updated each sprint. All sections marked [Unvalidated] must be confirmed with customer data before being treated as ground truth.*