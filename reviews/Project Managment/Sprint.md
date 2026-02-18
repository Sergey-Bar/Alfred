# AI Orchestrator — Development Task Board

**Project:** AI Orchestrator — Enterprise AI Control & Economy Platform
**Last Updated:** February 2026
**Total Tasks:** 111
**Reference:** AI_Orchestrator_PRD_MASTER.md

---

## Model Selection Guide

### Your Available Models by Tier

| Tier          | Cost         | Models                                                            | Best For                                                         |
| ------------- | ------------ | ----------------------------------------------------------------- | ---------------------------------------------------------------- |
| **FREE**      | 0X tokens    | GPT 4.1 Free, GPT 4o Free, GPT 5 Mini Free                        | Boilerplate, config, scaffolding, simple CRUD, docs              |
| **FAST**      | 0.25X tokens | Grok Code Fast 1                                                  | Autocomplete, quick edits, repetitive patterns, file generation  |
| **EFFICIENT** | 0.33X tokens | Gemini 3 Flash, Claude Haiku 4.5, GPT 5.1 Codex Mini              | Standard features, REST endpoints, unit tests, data models       |
| **POWER**     | 1X tokens    | Claude Sonnet 4, Claude Sonnet 4.5, GPT 5.1 Codex, Gemini 2.5 Pro | Complex algorithms, concurrency, architecture decisions          |
| **MAX**       | 1X tokens    | Claude Opus 4.5, GPT 5.1 Codex Max, GPT 5.2                       | Security-critical code, hard bugs, system design, novel problems |

### Model Recommendation Logic

```
Task Complexity 1 — Easy (boilerplate, config, CRUD)
  → GPT 4o Free or GPT 5 Mini Free
  → Save tokens, these models handle it perfectly

Task Complexity 2 — Medium (standard features, APIs, tests)
  → GPT 5.1 Codex Mini (0.33X) or Claude Haiku 4.5 (0.33X)
  → Great output-to-cost ratio

Task Complexity 3 — Hard (algorithms, concurrency, architecture)
  → Claude Sonnet 4.5 (1X) or GPT 5.1 Codex (1X)
  → Need deep reasoning + code quality

Task Complexity 4 — Very Hard (security, distributed systems, novel design)
  → Claude Opus 4.5 (1X) or GPT 5.1 Codex Max (1X)
  → Don't cut corners here — bugs are expensive
```

### Specific Model Strengths

| Model                  | Strength                                  | Use It When                                        |
| ---------------------- | ----------------------------------------- | -------------------------------------------------- |
| **GPT 4o Free**        | Solid general coding, fast                | Scaffolding, config, boilerplate                   |
| **GPT 5 Mini Free**    | Lightweight, fast                         | Simple functions, type definitions, comments       |
| **Grok Code Fast 1**   | Fastest autocomplete                      | Repetitive code, filling in patterns               |
| **Claude Haiku 4.5**   | Efficient, follows instructions precisely | REST endpoints, data models, unit tests            |
| **GPT 5.1 Codex Mini** | Good code generation, cheap               | Standard features, middleware                      |
| **Gemini 3 Flash**     | Fast, large context                       | Refactoring across multiple files                  |
| **Claude Sonnet 4.5**  | Best reasoning + code                     | Complex algorithms, system design, debugging       |
| **GPT 5.1 Codex**      | Best pure code generation                 | Go/Rust performance code, complex logic            |
| **GPT 5.1 Codex Max**  | Maximum code quality                      | Critical path code, security modules               |
| **Claude Opus 4.5**    | Deepest reasoning                         | Architecture decisions, security review, hard bugs |
| **Gemini 2.5 Pro**     | Massive context window                    | Large refactors, cross-file analysis, legacy code  |
| **GPT 5.2**            | Latest general intelligence               | Novel problems, unclear requirements               |

---

## Priority + Complexity Legend

```
PRIORITY:
  🔴 P0 — MVP Critical (build this first, product doesn't exist without it)
  🟠 P1 — High (delivers core value, needed within 90 days)
  🟡 P2 — Medium (important for enterprise sales, Phase 2-3)
  🟢 P3 — Nice to Have (moat features, Phase 4-5)

COMPLEXITY:
  ⭐ 1 — Easy     (hours, well-defined, clear implementation)
  ⭐⭐ 2 — Medium  (days, standard engineering, some decisions)
  ⭐⭐⭐ 3 — Hard    (1-2 weeks, complex logic, architecture matters)
  ⭐⭐⭐⭐ 4 — Very Hard (2-4 weeks, distributed systems, security-critical)

STATUS:
  [ ] Not started
  [~] In progress
  [x] Done
  [!] Blocked
```

---

## Phase 1 — MVP: Gateway + Metering + Wallet

### Target: Month 1–4 | Goal: First external customer routing live

---

### 🏗️ Epic 1: Project Foundation

| ID   | Task                                                                                  | Priority | Complexity | Recommended Model      | Notes                                                |
| ---- | ------------------------------------------------------------------------------------- | -------- | ---------- | ---------------------- | ---------------------------------------------------- |
| T001 | [ ] Go monorepo project structure (gateway, metering, wallet, orchestration services) | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Standard Go project layout — free model handles this |
| T002 | [ ] Dockerfile + docker-compose for local dev                                         | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Boilerplate, straightforward                         |
| T003 | [ ] GitHub Actions CI pipeline (lint, test, build)                                    | 🔴 P0    | ⭐ 1       | **GPT 5 Mini Free**    | Standard YAML — free model                           |
| T004 | [ ] Kubernetes manifests (Deployment, Service, Ingress, HPA)                          | 🔴 P0    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Standard K8s config but needs tuning                 |
| T005 | [ ] Environment configuration management (Viper/envconfig)                            | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Config boilerplate                                   |
| T006 | [ ] Structured logging setup (zerolog or zap)                                         | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Standard setup                                       |
| T007 | [ ] PostgreSQL schema migrations (golang-migrate)                                     | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Write SQL migration files                            |
| T008 | [ ] Redis connection + health check                                                   | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Standard Redis client setup                          |
| T009 | [ ] Makefile with dev commands (run, test, build, migrate)                            | 🔴 P0    | ⭐ 1       | **GPT 5 Mini Free**    | Simple scripting                                     |
| T010 | [ ] Pre-commit hooks (golangci-lint, gofmt, go vet)                                   | 🟠 P1    | ⭐ 1       | **GPT 5 Mini Free**    | Config files                                         |

---

### 🌐 Epic 2: AI Gateway Core

| ID   | Task                                                        | Priority | Complexity | Recommended Model      | Notes                                         |
| ---- | ----------------------------------------------------------- | -------- | ---------- | ---------------------- | --------------------------------------------- |
| T011 | [ ] HTTP server with graceful shutdown (chi or gin router)  | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Need proper middleware chain design           |
| T012 | [ ] API key authentication middleware                       | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Auth is security-adjacent, use reliable model |
| T013 | [ ] Request correlation ID injection (trace ID per request) | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Middleware, simple                            |
| T014 | [ ] POST /v1/chat/completions — non-streaming               | 🔴 P0    | ⭐⭐⭐ 3   | **GPT 5.1 Codex**      | Core product endpoint, needs precision        |
| T015 | [ ] POST /v1/chat/completions — SSE streaming pass-through  | 🔴 P0    | ⭐⭐⭐ 3   | **GPT 5.1 Codex**      | SSE in Go is tricky; buffering, flushing      |
| T016 | [ ] POST /v1/embeddings endpoint                            | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Simpler than chat                             |
| T017 | [ ] Function calling / tool use pass-through                | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Schema normalization needed                   |
| T018 | [ ] Request/response header normalization                   | 🔴 P0    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Per-provider header handling                  |
| T019 | [ ] Rate limiting middleware (Redis token bucket)           | 🔴 P0    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Distributed rate limiting is subtle           |
| T020 | [ ] Connection pooling to upstream providers                | 🔴 P0    | ⭐⭐⭐ 3   | **GPT 5.1 Codex**      | HTTP client pool management in Go             |
| T021 | [ ] Health check endpoint GET /health + GET /ready          | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Simple                                        |
| T022 | [ ] Timeout handling (per-provider configurable)            | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Context cancellation in Go                    |
| T023 | [ ] Request body size limits + validation                   | 🟠 P1    | ⭐ 1       | **GPT 5 Mini Free**    | Middleware config                             |
| T024 | [ ] Dry-run mode (estimate cost, don't call provider)       | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Route through metering, skip provider         |

---

### 🔌 Epic 3: Provider Connectors

| ID   | Task                                                        | Priority | Complexity | Recommended Model      | Notes                                           |
| ---- | ----------------------------------------------------------- | -------- | ---------- | ---------------------- | ----------------------------------------------- |
| T025 | [ ] Provider interface / abstraction layer (Go interface)   | 🔴 P0    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Interface design affects everything downstream  |
| T026 | [ ] OpenAI provider connector                               | 🔴 P0    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Well-documented API                             |
| T027 | [ ] Anthropic provider connector (different auth + headers) | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Different schema than OpenAI                    |
| T028 | [ ] Provider config CRUD (base URL, key path, model list)   | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | DB + REST API                                   |
| T029 | [ ] Provider pricing config (input/output rate per model)   | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | Config file + seeding                           |
| T030 | [ ] Google Gemini provider connector                        | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Vertex AI or AI Studio REST                     |
| T031 | [ ] Azure OpenAI provider connector                         | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | OpenAI-compatible but different base URL + auth |
| T032 | [ ] AWS Bedrock provider connector                          | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | AWS SDK + different streaming format            |
| T033 | [ ] Cohere provider connector                               | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | —                                               |
| T034 | [ ] Mistral provider connector                              | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | OpenAI-compatible                               |
| T035 | [ ] Together AI connector                                   | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | OpenAI-compatible, easy                         |
| T036 | [ ] Groq connector                                          | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | OpenAI-compatible, easy                         |
| T037 | [ ] Ollama self-hosted connector                            | 🟢 P3    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Local endpoint, OpenAI-compatible               |
| T038 | [ ] vLLM self-hosted connector                              | 🟢 P3    | ⭐⭐ 2     | **Claude Haiku 4.5**   | OpenAI-compatible server                        |
| T039 | [ ] Provider health check poller (every 30s)                | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Background goroutine, status tracking           |
| T040 | [ ] Provider model list sync (fetch available models)       | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Cron + DB update                                |

---

### 💰 Epic 4: Token Metering Engine

| ID   | Task                                                                    | Priority | Complexity | Recommended Model      | Notes                                     |
| ---- | ----------------------------------------------------------------------- | -------- | ---------- | ---------------------- | ----------------------------------------- |
| T041 | [ ] Tiktoken integration (token counting for OpenAI models)             | 🔴 P0    | ⭐⭐ 2     | **GPT 5.1 Codex**      | CGo or WASM binding; non-trivial in Go    |
| T042 | [ ] Cost calculation engine (input × rate + output × rate)              | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Precision arithmetic (decimal, not float) |
| T043 | [ ] Token estimation pre-request (for wallet reservation)               | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Estimate from max_tokens + prompt         |
| T044 | [ ] Streaming token counter (count tokens as chunks arrive)             | 🔴 P0    | ⭐⭐⭐ 3   | **GPT 5.1 Codex**      | Stream parsing, real-time accumulation    |
| T045 | [ ] Post-stream settlement (reserve → actual, adjust wallet)            | 🔴 P0    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Race condition risk; needs careful design |
| T046 | [ ] Async request log write to DB (non-blocking)                        | 🔴 P0    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Channel + goroutine pattern               |
| T047 | [ ] Partial stream disconnect handling (bill tokens sent)               | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Detect client drop mid-stream             |
| T048 | [ ] Provider tokenizer support (Anthropic, Gemini differ from tiktoken) | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Per-provider counting rules               |
| T049 | [ ] Free tier model tracking (don't deduct for free models)             | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Flag per provider config                  |

---

### 🏦 Epic 5: Wallet Service

| ID   | Task                                                              | Priority | Complexity | Recommended Model     | Notes                                          |
| ---- | ----------------------------------------------------------------- | -------- | ---------- | --------------------- | ---------------------------------------------- |
| T050 | [ ] Wallet data model + PostgreSQL schema                         | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**  | See PRD schema; hierarchy matters              |
| T051 | [ ] Wallet CRUD REST API                                          | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Standard REST; 8 endpoints                     |
| T052 | [ ] Atomic balance deduction (SELECT FOR UPDATE or advisory lock) | 🔴 P0    | ⭐⭐⭐⭐ 4 | **Claude Opus 4.5**   | Financial correctness — don't get this wrong   |
| T053 | [ ] Hard limit enforcement — return HTTP 402 on exhaustion        | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Pre-request wallet check                       |
| T054 | [ ] Soft limit threshold detection (80%, 90%, 95%)                | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Compare spent/limit, emit events               |
| T055 | [ ] Wallet balance API GET /v1/wallet/balance                     | 🔴 P0    | ⭐ 1       | **GPT 4o Free**       | Simple query                                   |
| T056 | [ ] Monthly wallet reset cron job                                 | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Reset on configured day; handle timezone       |
| T057 | [ ] Wallet hierarchy enforcement (parent limits children)         | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5** | Recursive limit checking                       |
| T058 | [ ] Overdraft configuration (allow N% over limit)                 | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Configurable per wallet                        |
| T059 | [ ] Wallet reservation system (pre-flight hold)                   | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5** | Two-phase: reserve → settle                    |
| T060 | [ ] Concurrent request handling without race conditions           | 🟠 P1    | ⭐⭐⭐⭐ 4 | **Claude Opus 4.5**   | Load test at 1000 concurrent; verify atomicity |
| T061 | [ ] Chargeback export (CSV/JSON by team, date range)              | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**  | SQL aggregation + streaming CSV                |

---

### 📊 Epic 6: Basic Dashboard (Next.js)

| ID   | Task                                                        | Priority | Complexity | Recommended Model      | Notes                             |
| ---- | ----------------------------------------------------------- | -------- | ---------- | ---------------------- | --------------------------------- |
| T062 | [ ] Next.js 14 project setup (TypeScript, Tailwind, ESLint) | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | `create-next-app` + config        |
| T063 | [ ] Authentication (NextAuth.js with API key + email)       | 🔴 P0    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Standard NextAuth setup           |
| T064 | [ ] Organization onboarding flow (signup → first API key)   | 🔴 P0    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Multi-step form                   |
| T065 | [ ] Cost dashboard — total spend by team/model/date         | 🔴 P0    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Recharts + API fetch              |
| T066 | [ ] Wallet balance card + utilization bar                   | 🔴 P0    | ⭐ 1       | **GPT 4o Free**        | UI component                      |
| T067 | [ ] API key management (create, list, revoke)               | 🔴 P0    | ⭐⭐ 2     | **Claude Haiku 4.5**   | CRUD + show-once key display      |
| T068 | [ ] Request log table (sortable, filterable, paginated)     | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Table with server-side pagination |
| T069 | [ ] Team management (create teams, invite members)          | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | User/team CRUD                    |
| T070 | [ ] Wallet limit configuration UI                           | 🟠 P1    | ⭐ 1       | **GPT 4o Free**        | Simple form                       |
| T071 | [ ] Provider configuration UI (add/test provider)           | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Form + connection test            |
| T072 | [ ] Real-time spend ticker (WebSocket or polling)           | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Live updates on dashboard         |

---

## Phase 2 — Control: Communication + Governance

### Target: Month 4–6 | Goal: Budget alerts live; multi-team governance

---

### 🔔 Epic 7: Notification Engine

| ID   | Task                                                              | Priority | Complexity | Recommended Model     | Notes                             |
| ---- | ----------------------------------------------------------------- | -------- | ---------- | --------------------- | --------------------------------- |
| T073 | [ ] Notification service (fanout to multiple channels)            | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5** | Abstract over Slack/email/webhook |
| T074 | [ ] Alert deduplication (don't fire same alert twice in N mins)   | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Redis-backed dedup window         |
| T075 | [ ] Escalation ladder (80% → team lead, 95% → FinOps, 100% → all) | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Configurable escalation chain     |
| T076 | [ ] Email notifications (AWS SES or SendGrid)                     | 🟠 P1    | ⭐ 1       | **GPT 4o Free**       | SDK + template                    |
| T077 | [ ] Webhook notifications (configurable POST)                     | 🟠 P1    | ⭐ 1       | **GPT 4o Free**       | HTTP POST with retry              |
| T078 | [ ] Daily spend digest (scheduled cron + send)                    | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Aggregate + format + send         |

---

### 💬 Epic 8: Slack App

| ID   | Task                                                    | Priority | Complexity | Recommended Model      | Notes                                                |
| ---- | ------------------------------------------------------- | -------- | ---------- | ---------------------- | ---------------------------------------------------- |
| T079 | [ ] Slack App setup (Bolt for Go/Node)                  | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Slack Bolt boilerplate                               |
| T080 | [ ] Budget alert messages with Block Kit formatting     | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Slack Block Kit JSON — Haiku is precise with schemas |
| T081 | [ ] /ai-budget slash command (show balance)             | 🟠 P1    | ⭐ 1       | **GPT 4o Free**        | Simple command handler                               |
| T082 | [ ] /ai-request slash command (budget increase request) | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Modal + form handling                                |
| T083 | [ ] Approval workflow (Approve/Reject buttons in Slack) | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Interactive components + state management            |
| T084 | [ ] /ai-forecast slash command                          | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Call forecast API, format response                   |
| T085 | [ ] /ai-top-users slash command                         | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Query + format leaderboard                           |
| T086 | [ ] Daily 9AM digest job                                | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Cron + aggregate + Slack message                     |

---

### 💸 Epic 9: Budget Transfer Workflow

| ID   | Task                                                               | Priority | Complexity | Recommended Model    | Notes                                                    |
| ---- | ------------------------------------------------------------------ | -------- | ---------- | -------------------- | -------------------------------------------------------- |
| T087 | [ ] Transfer request data model + API                              | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5** | CRUD + state machine (pending/approved/rejected/expired) |
| T088 | [ ] Transfer approval API (POST /v1/wallet/transfers/{id}/approve) | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5** | Atomic: approve + move funds                             |
| T089 | [ ] Transfer request expiry (48h auto-expire)                      | 🟠 P1    | ⭐ 1       | **GPT 4o Free**      | Cron job                                                 |
| T090 | [ ] Transfer history UI (dashboard)                                | 🟠 P1    | ⭐ 1       | **GPT 4o Free**      | Table component                                          |

---

## Phase 3 — Optimize: Orchestration + Caching

### Target: Month 6–9 | Goal: 30%+ cost savings measurably delivered

---

### 🔀 Epic 10: Routing Engine

| ID   | Task                                                                 | Priority | Complexity | Recommended Model      | Notes                                         |
| ---- | -------------------------------------------------------------------- | -------- | ---------- | ---------------------- | --------------------------------------------- |
| T091 | [ ] Routing rule data model + CRUD API                               | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | See PRD schema                                |
| T092 | [ ] Rule evaluation engine (priority-ordered, condition matching)    | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Condition evaluation with short-circuit       |
| T093 | [ ] Cost-based routing (cheapest provider meeting SLA)               | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Real-time price comparison + routing          |
| T094 | [ ] Provider failover logic (see PRD decision tree)                  | 🟠 P1    | ⭐⭐⭐ 3   | **GPT 5.1 Codex**      | State machine: try → retry → failover → error |
| T095 | [ ] SLA-aware load balancing (round-robin + weighted)                | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Weighted routing with latency awareness       |
| T096 | [ ] Geo-based routing restrictions (request origin → allowed region) | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | IP → geo lookup → provider filter             |
| T097 | [ ] Routing rules management UI                                      | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Drag-and-drop priority ordering               |
| T098 | [ ] Routing decision logging (why was this model chosen?)            | 🟠 P1    | ⭐ 1       | **GPT 4o Free**        | Append routing_reason to request log          |

---

### 🧪 Epic 11: Routing Experiments

| ID   | Task                                                                      | Priority | Complexity | Recommended Model      | Notes                                    |
| ---- | ------------------------------------------------------------------------- | -------- | ---------- | ---------------------- | ---------------------------------------- |
| T099 | [ ] Experiment data model (name, traffic split, models, metrics)          | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | —                                        |
| T100 | [ ] A/B traffic splitting (hash-based, configurable %)                    | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Consistent hashing for stable assignment |
| T101 | [ ] Experiment metric aggregation (cost, latency, error rate per variant) | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | ClickHouse query                         |
| T102 | [ ] Statistical significance detection (simple z-test)                    | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Math library                             |
| T103 | [ ] Auto-switch on threshold (promote winner)                             | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Trigger on significance + delta          |
| T104 | [ ] Experiment UI (create, monitor, conclude)                             | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | —                                        |

---

### 🧠 Epic 12: Semantic Caching

| ID   | Task                                                           | Priority | Complexity | Recommended Model      | Notes                                      |
| ---- | -------------------------------------------------------------- | -------- | ---------- | ---------------------- | ------------------------------------------ |
| T105 | [ ] Vector DB integration (Pinecone or Redis Vector)           | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | SDK integration                            |
| T106 | [ ] Embedding generation for incoming prompts                  | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Call embedding provider; handle latency    |
| T107 | [ ] Similarity search + threshold comparison                   | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Tune threshold per team; handle edge cases |
| T108 | [ ] Cache write on first response                              | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Store embedding + response + TTL           |
| T109 | [ ] Per-team cache segmentation (namespace isolation)          | 🟠 P1    | ⭐ 1       | **GPT 4o Free**        | Key prefix strategy                        |
| T110 | [ ] TTL management (per model, per team)                       | 🟠 P1    | ⭐ 1       | **GPT 4o Free**        | Config + expiry                            |
| T111 | [ ] Cache confidence score in response headers                 | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Add X-Cache-Similarity header              |
| T112 | [ ] Cache bypass (header-triggered)                            | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | X-Cache-Bypass: true                       |
| T113 | [ ] Cache performance metrics (hit rate, savings $)            | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Counter in ClickHouse                      |
| T114 | [ ] Cache invalidation (manual flush endpoint)                 | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | DELETE endpoint + vector delete            |
| T115 | [ ] Cache poisoning prevention (response validation pre-serve) | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Validate cache hit is coherent             |

---

### 📈 Epic 13: Analytics Pipeline

| ID   | Task                                                          | Priority | Complexity | Recommended Model     | Notes                                     |
| ---- | ------------------------------------------------------------- | -------- | ---------- | --------------------- | ----------------------------------------- |
| T116 | [ ] ClickHouse schema design (requests, costs, wallet_events) | 🟠 P1    | ⭐⭐ 2     | **Claude Sonnet 4.5** | Schema design affects all queries         |
| T117 | [ ] Event ingestion pipeline (NATS/Kafka → ClickHouse)        | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5** | Reliable async pipeline with backpressure |
| T118 | [ ] Cost per model / team / feature query API                 | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**  | GET /v1/analytics/cost with group_by      |
| T119 | [ ] Latency percentile queries (P50, P95, P99 per provider)   | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**  | ClickHouse quantile functions             |
| T120 | [ ] Cache hit rate aggregation query                          | 🟡 P2    | ⭐ 1       | **GPT 4o Free**       | Simple ClickHouse count                   |
| T121 | [ ] Daily cost aggregation jobs (materialized views)          | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**  | ClickHouse materialized view              |
| T122 | [ ] Cost data CSV export endpoint                             | 🟡 P2    | ⭐ 1       | **GPT 4o Free**       | Stream CSV from query                     |

---

## Phase 4 — Intelligence: Analytics + Enterprise

### Target: Month 9–12 | Goal: Enterprise-ready; SOC 2 in progress

---

### 🔒 Epic 14: Security Middleware

| ID   | Task                                                               | Priority | Complexity | Recommended Model     | Notes                                            |
| ---- | ------------------------------------------------------------------ | -------- | ---------- | --------------------- | ------------------------------------------------ |
| T123 | [ ] PII detection middleware (regex-based: email, phone, SSN, CC)  | 🟠 P1    | ⭐⭐⭐ 3   | **GPT 5.1 Codex Max** | Low false negative requirement; use best model   |
| T124 | [ ] NER-based PII detection (name, DOB, medical)                   | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Opus 4.5**   | ML model integration; precision matters          |
| T125 | [ ] Secret/API key detection (entropy analysis + patterns)         | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Opus 4.5**   | Security-critical; must have low false negatives |
| T126 | [ ] PII redaction (replace with [PERSON_1] etc.)                   | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Regex replace with placeholder tokens            |
| T127 | [ ] Prompt risk scoring (composite 0–100 score)                    | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5** | Aggregate signals into risk score                |
| T128 | [ ] Prompt injection detection (pattern library)                   | 🟡 P2    | ⭐⭐ 2     | **Claude Sonnet 4.5** | Security research needed                         |
| T129 | [ ] Security action handlers (block / redact / alert / quarantine) | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**  | Action routing from detection result             |
| T130 | [ ] Security alert channel notification                            | 🟠 P1    | ⭐ 1       | **GPT 4o Free**       | Slack/webhook event                              |
| T131 | [ ] Middleware latency budget enforcement (<10ms P99)              | 🟠 P1    | ⭐⭐⭐ 3   | **GPT 5.1 Codex**     | Profiling + optimization                         |

---

### 📋 Epic 15: OPA Policy Engine

| ID   | Task                                                                            | Priority | Complexity | Recommended Model      | Notes                         |
| ---- | ------------------------------------------------------------------------------- | -------- | ---------- | ---------------------- | ----------------------------- |
| T132 | [ ] OPA server integration (sidecar or embedded)                                | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | OPA REST API + policy loading |
| T133 | [ ] Policy CRUD API (upload/update/delete Rego policies)                        | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Store in DB + sync to OPA     |
| T134 | [ ] Built-in policy templates (premium model gating, token limits, time-of-day) | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Write 5–10 Rego templates     |
| T135 | [ ] Policy dry-run mode (evaluate but don't enforce)                            | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Flag in policy config         |
| T136 | [ ] Policy evaluation logging (which policies fired, why)                       | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Append to request log         |
| T137 | [ ] Policy management UI (upload, test, activate)                               | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Code editor + test panel      |

---

### 🔐 Epic 16: Audit Log

| ID   | Task                                                                   | Priority | Complexity | Recommended Model      | Notes                                             |
| ---- | ---------------------------------------------------------------------- | -------- | ---------- | ---------------------- | ------------------------------------------------- |
| T138 | [ ] Audit log schema (append-only, hash chain)                         | 🟠 P1    | ⭐⭐⭐ 4   | **Claude Opus 4.5**    | Cryptographic correctness critical for compliance |
| T139 | [ ] Audit log writer (every admin action, policy event, request block) | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Instrument key events                             |
| T140 | [ ] Hash chain verification job (daily integrity check)                | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Walk chain, verify each hash                      |
| T141 | [ ] Audit log export API (CSV, JSON, Parquet; filterable)              | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Streaming export                                  |
| T142 | [ ] GDPR right-to-erasure (delete prompt content, keep metadata)       | 🟡 P2    | ⭐⭐ 2     | **Claude Sonnet 4.5**  | Precise deletion scope matters                    |
| T143 | [ ] Audit log viewer (dashboard, filterable)                           | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Table + filters                                   |

---

### 📡 Epic 17: Observability Integrations

| ID   | Task                                                               | Priority | Complexity | Recommended Model      | Notes                                   |
| ---- | ------------------------------------------------------------------ | -------- | ---------- | ---------------------- | --------------------------------------- |
| T144 | [ ] Prometheus /metrics endpoint (all gateway + wallet metrics)    | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | prometheus/client_golang                |
| T145 | [ ] OpenTelemetry tracing (trace spans for full request lifecycle) | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | OTel SDK in Go; propagate trace context |
| T146 | [ ] Grafana dashboard template (JSON export)                       | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Grafana JSON dashboard config           |
| T147 | [ ] Datadog integration (DogStatsD metrics + APM)                  | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Datadog Go SDK                          |
| T148 | [ ] PagerDuty alert integration                                    | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Events API v2 webhook                   |
| T149 | [ ] Splunk log forwarding (HEC)                                    | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | HTTP POST to HEC endpoint               |

---

### 🔑 Epic 18: SSO & Identity

| ID   | Task                                                       | Priority | Complexity | Recommended Model      | Notes                                 |
| ---- | ---------------------------------------------------------- | -------- | ---------- | ---------------------- | ------------------------------------- |
| T150 | [ ] SAML 2.0 SSO integration (Okta, Entra ID)              | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | SAML is complex; use a proven library |
| T151 | [ ] OIDC SSO integration (Google Workspace, Auth0)         | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Standard OIDC flow                    |
| T152 | [ ] SCIM provisioning (auto-create users/teams from IdP)   | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | SCIM 2.0 spec compliance              |
| T153 | [ ] RBAC (role-based access: owner, admin, member, viewer) | 🟠 P1    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Permission middleware                 |
| T154 | [ ] SSO configuration UI (dashboard)                       | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | SAML/OIDC config form                 |

---

### 🧮 Epic 19: AI Intelligence Features

| ID   | Task                                                                          | Priority | Complexity | Recommended Model      | Notes                                             |
| ---- | ----------------------------------------------------------------------------- | -------- | ---------- | ---------------------- | ------------------------------------------------- |
| T155 | [ ] AI usage classification (categorize requests: code, summary, legal, etc.) | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Few-shot classifier or fine-tuned model           |
| T156 | [ ] Budget forecasting (linear regression on 14-day rolling window)           | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | gonum/stat or simple implementation               |
| T157 | [ ] Anomaly detection (Z-score on hourly token consumption)                   | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Rolling mean + std dev                            |
| T158 | [ ] Budget forecast dashboard widget                                          | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Line chart + projected line                       |
| T159 | [ ] Cost per feature attribution (tag requests with feature_id)               | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Pass-through metadata tag                         |
| T160 | [ ] AI ROI scoring engine (spend vs. productivity metric)                     | 🟢 P3    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Complex; requires customer-provided output metric |
| T161 | [ ] Token efficiency score per team (output quality / tokens)                 | 🟢 P3    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Composite metric                                  |
| T162 | [ ] Model efficiency leaderboard (teams ranked by efficiency)                 | 🟢 P3    | ⭐ 1       | **GPT 4o Free**        | SQL rank + dashboard                              |
| T163 | [ ] Cross-model cost arbitrage engine (real-time price feeds)                 | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Price polling + routing trigger                   |
| T164 | [ ] AI Traffic Replay & Simulation                                            | 🟢 P3    | ⭐⭐⭐⭐ 4 | **Claude Opus 4.5**    | Record + replay + simulate — complex              |

---

### 🖥️ Epic 20: IDE Extension (VS Code)

| ID   | Task                                                   | Priority | Complexity | Recommended Model      | Notes                  |
| ---- | ------------------------------------------------------ | -------- | ---------- | ---------------------- | ---------------------- |
| T165 | [ ] VS Code extension project setup (TypeScript, vsce) | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Boilerplate            |
| T166 | [ ] Status bar token counter + estimated cost          | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | VS Code API            |
| T167 | [ ] Session cost gauge (runs, resets per session)      | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Local state            |
| T168 | [ ] Model selector dropdown with cost comparison       | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | QuickPick with pricing |
| T169 | [ ] Dev vs. Prod mode toggle (cheap model in dev)      | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Config toggle          |
| T170 | [ ] Budget alert popup in IDE                          | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | VS Code notification   |
| T171 | [ ] Per-repo cost tracking (.vscode/settings.json)     | 🟢 P3    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Workspace config       |

---

## Phase 5 — Moat: Defensibility Features

### Target: Month 12–18 | Goal: Hard to leave; enterprise fully locked in

---

### 📝 Epic 21: Prompt Registry

| ID   | Task                                                                    | Priority | Complexity | Recommended Model      | Notes                                           |
| ---- | ----------------------------------------------------------------------- | -------- | ---------- | ---------------------- | ----------------------------------------------- |
| T172 | [ ] Prompt registry data model (id, version, content, metadata)         | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | See PRD schema                                  |
| T173 | [ ] Prompt version history + diff API                                   | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Diff algorithm (difflib-style)                  |
| T174 | [ ] Prompt rollback endpoint                                            | 🟡 P2    | ⭐ 1       | **GPT 4o Free**        | Copy old version as new version                 |
| T175 | [ ] Prompt approval workflow (PR-style review)                          | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Status machine + reviewer assignment            |
| T176 | [ ] Prompt A/B testing (route % of traffic to new version)              | 🟢 P3    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Integrate with routing experiment engine        |
| T177 | [ ] Prompt performance metrics (cost, quality, token usage per version) | 🟢 P3    | ⭐⭐ 2     | **Claude Haiku 4.5**   | ClickHouse query grouped by prompt_id + version |
| T178 | [ ] Prompt registry UI (browser, edit, version history)                 | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Code editor (Monaco) + version list             |

---

### 🔗 Epic 22: FinOps Integrations

| ID   | Task                                                                    | Priority | Complexity | Recommended Model    | Notes                               |
| ---- | ----------------------------------------------------------------------- | -------- | ---------- | -------------------- | ----------------------------------- |
| T179 | [ ] Snowflake export (scheduled cost data push via connector)           | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5** | Snowflake Go driver                 |
| T180 | [ ] Cost center tagging system (tag any wallet with cost center ID)     | 🟡 P2    | ⭐ 1       | **GPT 4o Free**      | Add field + filter                  |
| T181 | [ ] Department chargeback automation (scheduled export per cost center) | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5** | Cron + aggregate + export           |
| T182 | [ ] SAP / Oracle ERP export (CSV format with cost center headers)       | 🟢 P3    | ⭐⭐ 2     | **Claude Haiku 4.5** | Format to ERP-compatible CSV schema |
| T183 | [ ] Scheduled export configuration UI                                   | 🟡 P2    | ⭐ 1       | **GPT 4o Free**      | Simple schedule config form         |

---

### 🛠️ Epic 23: Developer Tooling

| ID   | Task                                                               | Priority | Complexity | Recommended Model      | Notes                                          |
| ---- | ------------------------------------------------------------------ | -------- | ---------- | ---------------------- | ---------------------------------------------- |
| T184 | [ ] CLI tool (Go binary: ao auth, ao wallet, ao routes, ao policy) | 🟡 P2    | ⭐⭐⭐ 3   | **GPT 5.1 Codex**      | cobra CLI framework                            |
| T185 | [ ] Python SDK (pip install ai-orchestrator)                       | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Wrap OpenAI Python SDK                         |
| T186 | [ ] Node.js SDK (npm install @ai-orchestrator/sdk)                 | 🟡 P2    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Wrap OpenAI JS SDK                             |
| T187 | [ ] Go SDK                                                         | 🟢 P3    | ⭐⭐ 2     | **GPT 5.1 Codex**      | Native Go client                               |
| T188 | [ ] Terraform provider (wallets, routing rules as code)            | 🟢 P3    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Terraform plugin SDK                           |
| T189 | [ ] Helm chart (full K8s deployment)                               | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Helm 3 chart with values                       |
| T190 | [ ] GitHub Actions cost gate action                                | 🟢 P3    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Action that fails pipeline if cost > threshold |
| T191 | [ ] OpenAPI spec (auto-generated from gateway handlers)            | 🟠 P1    | ⭐ 1       | **GPT 4o Free**        | swaggo or oapi-codegen                         |

---

### 🏢 Epic 24: Infrastructure & Security Hardening

| ID   | Task                                                                    | Priority | Complexity | Recommended Model      | Notes                                           |
| ---- | ----------------------------------------------------------------------- | -------- | ---------- | ---------------------- | ----------------------------------------------- |
| T192 | [ ] HashiCorp Vault integration (provider key storage + rotation)       | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Vault Go SDK; dynamic secrets                   |
| T193 | [ ] mTLS between internal services (Istio or manual cert management)    | 🟡 P2    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Service mesh or cert-manager                    |
| T194 | [ ] BYOK encryption (customer-provided encryption keys)                 | 🟢 P3    | ⭐⭐⭐⭐ 4 | **Claude Opus 4.5**    | Key hierarchy; KMS integration                  |
| T195 | [ ] Data residency routing enforcement (region-lock per org)            | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Org setting → provider filter                   |
| T196 | [ ] Penetration test prep (document attack surface, fix findings)       | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Opus 4.5**    | Security review — highest stakes                |
| T197 | [ ] SOC 2 controls documentation + evidence collection                  | 🟠 P1    | ⭐⭐ 2     | **Claude Sonnet 4.5**  | Write control descriptions; collect screenshots |
| T198 | [ ] Disaster recovery runbook (DB restore, region failover)             | 🟡 P2    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Step-by-step runbook                            |
| T199 | [ ] Load testing suite (k6 or Gatling; 10K req/min target)              | 🟠 P1    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | k6 scripts                                      |
| T200 | [ ] Billing reconciliation monthly job (our count vs. provider invoice) | 🟠 P1    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Financial accuracy critical                     |

---

### 🌐 Epic 25: Microsoft Teams App

| ID   | Task                                | Priority | Complexity | Recommended Model      | Notes                           |
| ---- | ----------------------------------- | -------- | ---------- | ---------------------- | ------------------------------- |
| T201 | [ ] Teams app setup (Bot Framework) | 🟢 P3    | ⭐⭐ 2     | **GPT 5.1 Codex Mini** | Microsoft Bot Framework         |
| T202 | [ ] Budget alert adaptive cards     | 🟢 P3    | ⭐⭐ 2     | **Claude Haiku 4.5**   | Adaptive Card JSON              |
| T203 | [ ] Approval workflow in Teams      | 🟢 P3    | ⭐⭐⭐ 3   | **Claude Sonnet 4.5**  | Interactive card + approval API |

---

## Summary Views

### Tasks by Phase

| Phase                            | P0  | P1  | P2  | P3  | Total |
| -------------------------------- | --- | --- | --- | --- | ----- |
| Phase 1 — MVP (Mo 1–4)           | 42  | 12  | 4   | 0   | 58    |
| Phase 2 — Control (Mo 4–6)       | 0   | 18  | 4   | 0   | 22    |
| Phase 3 — Optimize (Mo 6–9)      | 0   | 14  | 18  | 0   | 32    |
| Phase 4 — Intelligence (Mo 9–12) | 0   | 18  | 22  | 6   | 46    |
| Phase 5 — Moat (Mo 12–18)        | 0   | 1   | 16  | 6   | 23    |

### Tasks by Model Tier

| Tier                                                      | # Tasks | % of Total |
| --------------------------------------------------------- | ------- | ---------- |
| Free (GPT 4o / GPT 5 Mini)                                | 44      | 39%        |
| 0.25X (Grok Code Fast)                                    | 0       | —          |
| 0.33X (Claude Haiku / GPT 5.1 Codex Mini / Gemini Flash)  | 58      | 52%        |
| 1X Power (Claude Sonnet / GPT 5.1 Codex / Gemini 2.5 Pro) | 17      | 15%        |
| 1X Max (Claude Opus / GPT 5.1 Codex Max)                  | 8       | 7%         |

> **Cost strategy:** ~39% of tasks can be done with free models. Save your 1X tokens for P0 concurrency, security, and architecture decisions.

### Hardest Tasks (Complexity 4 — Don't Skimp on Model)

| ID   | Task                                 | Recommended Model   | Why                                     |
| ---- | ------------------------------------ | ------------------- | --------------------------------------- |
| T052 | Atomic wallet balance deduction      | **Claude Opus 4.5** | Financial correctness; race conditions  |
| T060 | Concurrent request handling at scale | **Claude Opus 4.5** | Load-tested concurrency; hard to debug  |
| T125 | Secret/API key detection             | **Claude Opus 4.5** | Security-critical; low false negatives  |
| T138 | Immutable audit log with hash chain  | **Claude Opus 4.5** | Cryptographic correctness               |
| T164 | AI Traffic Replay & Simulation       | **Claude Opus 4.5** | Novel, complex system design            |
| T194 | BYOK encryption                      | **Claude Opus 4.5** | Key hierarchy mistakes are catastrophic |

### First 30 Days — Optimal Task Order

```
Week 1: Foundation
  T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008
  All free/fast models. Get local dev running.

Week 2: Gateway Core
  T011 → T012 → T013 → T014 → T025 → T026 → T027
  Mix of Haiku + GPT 5.1 Codex. First request through gateway.

Week 3: Metering + Wallet
  T041 → T042 → T043 → T050 → T051 → T052 → T053 → T054
  Heavy Claude Opus for T052. This is the financial engine.

Week 4: Basic Dashboard + Integration
  T062 → T063 → T064 → T065 → T066 → T067
  Free/Codex Mini for UI. Get something a customer can log into.
```

---

_Tasks file generated from AI_Orchestrator_PRD_MASTER.md v3.0_
_Update this file at the start of each sprint. Check off tasks as they ship._
_When in doubt about model choice: spend free tokens on config, save Opus for money-and-security code._
