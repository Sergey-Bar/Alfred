P1 — Backend: N+1 queries and query performance

Findings:
- Several dashboard and leaderboard endpoints do per-record lookups causing N+1 queries (expensive at scale).
- Identified spots:
  - `backend/app/main.py`: `get_leaderboard`, `get_transfer_history` originally fetched users per-entry.
  - `backend/app/dashboard.py`: `get_user_usage_stats`, `get_team_pool_stats` counted related rows inside loop.

Changes made / recommended:
- Bulk-fetch related users and counts, and use group-by aggregation to avoid per-item selects. (I updated some of these endpoints to batch fetch.)

Remaining suggestions:
1. Review all endpoints that iterate over model lists and call `session.get(...)` inside the loop; replace with single bulk query and mapping.
2. Add query-level benchmarks in CI to detect regressions (simple timing around endpoints with synthetic data).
3. Consider adding database indices for high-cardinality filter columns (`RequestLog.created_at`, `RequestLog.user_id`, `TokenTransfer.sender_id`/`recipient_id`).

Priority: High for dashboard endpoints (can degrade with more users).