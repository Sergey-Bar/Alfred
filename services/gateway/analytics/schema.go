/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       ClickHouse schema definitions for analytics pipeline.
             Defines request_log, cost_events, wallet_events
             tables with proper partitioning, indices, and
             materialized views for common aggregations.
Root Cause:  Sprint tasks T116 — ClickHouse schema design.
Context:     Analytics is the backbone of FinOps visibility.
             Schema design affects all downstream queries.
Suitability: L3 — schema design requires careful data modeling.
──────────────────────────────────────────────────────────────
*/

package analytics

// ─── ClickHouse Schema SQL ──────────────────────────────────

// RequestLogSchema is the DDL for the main request log table.
// Captures every LLM request processed by the gateway.
const RequestLogSchema = `
CREATE TABLE IF NOT EXISTS request_log (
    -- identity
    request_id      String,
    trace_id        String,
    org_id          String,
    team_id         String,
    user_id         String,
    api_key_hash    String,

    -- request metadata
    model           String,
    provider        String,
    endpoint        String,          -- /v1/chat/completions, /v1/embeddings
    method          String,          -- POST, GET

    -- tokens
    prompt_tokens   UInt32,
    completion_tokens UInt32,
    total_tokens    UInt32,

    -- cost (in microdollars: $0.01 = 10000)
    cost_microdollars Int64,
    currency        String DEFAULT 'USD',

    -- performance
    latency_ms      UInt32,
    ttfb_ms         UInt32,          -- time to first byte (streaming)
    provider_latency_ms UInt32,      -- upstream provider latency

    -- status
    status_code     UInt16,
    error_type      String,
    is_cached       UInt8,           -- 1 = cache hit, 0 = miss
    cache_similarity Float32,

    -- routing
    routing_rule_id String,
    was_failover    UInt8,

    -- safety
    safety_blocked  UInt8,
    safety_violations UInt16,

    -- timestamps
    created_at      DateTime64(3) DEFAULT now64(3),
    event_date      Date DEFAULT toDate(created_at)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (org_id, team_id, created_at, request_id)
TTL event_date + INTERVAL 365 DAY
SETTINGS index_granularity = 8192;
`

// CostEventSchema tracks credit/cost events for FinOps reporting.
const CostEventSchema = `
CREATE TABLE IF NOT EXISTS cost_events (
    event_id        String,
    org_id          String,
    team_id         String,
    user_id         String,
    wallet_id       String,

    -- cost breakdown
    model           String,
    provider        String,
    prompt_tokens   UInt32,
    completion_tokens UInt32,
    cost_microdollars Int64,

    -- wallet impact
    balance_before  Int64,
    balance_after   Int64,
    wallet_type     String,          -- user, team, org

    -- metadata
    request_id      String,
    event_type      String,          -- deduction, refund, topup, transfer
    description     String,

    created_at      DateTime64(3) DEFAULT now64(3),
    event_date      Date DEFAULT toDate(created_at)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (org_id, team_id, wallet_id, created_at)
TTL event_date + INTERVAL 730 DAY
SETTINGS index_granularity = 8192;
`

// WalletEventSchema tracks wallet lifecycle events.
const WalletEventSchema = `
CREATE TABLE IF NOT EXISTS wallet_events (
    event_id        String,
    wallet_id       String,
    org_id          String,
    team_id         String,
    user_id         String,

    event_type      String,          -- created, limit_changed, reset, suspended, activated
    old_value       String,
    new_value       String,

    actor_id        String,          -- who made the change
    actor_type      String,          -- admin, system, cron

    created_at      DateTime64(3) DEFAULT now64(3),
    event_date      Date DEFAULT toDate(created_at)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (org_id, wallet_id, created_at)
TTL event_date + INTERVAL 730 DAY
SETTINGS index_granularity = 8192;
`

// ─── Materialized Views (T121) ──────────────────────────────

// DailyCostMV aggregates cost by org/team/model per day.
const DailyCostMV = `
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_cost_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (org_id, team_id, model, event_date)
AS SELECT
    org_id,
    team_id,
    model,
    provider,
    toDate(created_at) AS event_date,
    count()            AS request_count,
    sum(prompt_tokens)      AS total_prompt_tokens,
    sum(completion_tokens)  AS total_completion_tokens,
    sum(total_tokens)       AS total_tokens,
    sum(cost_microdollars)  AS total_cost_microdollars,
    sum(latency_ms)         AS sum_latency_ms,
    sum(is_cached)          AS cache_hits
FROM request_log
GROUP BY org_id, team_id, model, provider, event_date;
`

// HourlyCostMV provides finer-grained cost visibility.
const HourlyCostMV = `
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_cost_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (org_id, team_id, event_hour)
AS SELECT
    org_id,
    team_id,
    toStartOfHour(created_at) AS event_hour,
    toDate(created_at)        AS event_date,
    count()                   AS request_count,
    sum(total_tokens)         AS total_tokens,
    sum(cost_microdollars)    AS total_cost_microdollars,
    sum(is_cached)            AS cache_hits
FROM request_log
GROUP BY org_id, team_id, event_hour, event_date;
`

// AllSchemas returns all DDL statements in creation order.
func AllSchemas() []string {
	return []string{
		RequestLogSchema,
		CostEventSchema,
		WalletEventSchema,
		DailyCostMV,
		HourlyCostMV,
	}
}
