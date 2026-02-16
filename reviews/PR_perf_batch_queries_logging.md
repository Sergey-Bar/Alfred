Perf: Batch DB queries & structured logging

Summary

- Batched several hot-path queries to eliminate N+1 patterns (teams, leaderboard, approvals, transfers).
- Added timing logs using the central structured logger for analytics on endpoint latency.
- Added single-column indexes on `team_member_links.team_id` and `team_member_links.user_id`.

Testing

- Ran full test suite locally: `pytest -q` — all tests passed (75 passed, 2 skipped).

Next actions / recommendations

- Run `EXPLAIN` on production-like DB (Postgres) for updated queries; consider additional indexes based on query plans.
- Add DB migration to create indexes for production (if using Postgres) and verify `down_revision` in Alembic.
- Run CI/E2E and monitor new structured logs in staging to ensure no noise from extra info fields.

Files changed (high level)

- `src/backend/app/routers/teams.py` — batched member counts, added timing log.
- `src/backend/app/routers/governance.py` — defensive guards, batched identity fetches, timing logs.
- `src/backend/app/dashboard.py` — replaced per-user loops with grouped aggregates and timing logs.
- `src/backend/app/models.py` — added indexes to `TeamMemberLink`.

How to reproduce benchmarks

1. Push branch and open PR on GitHub (branch: `perf/batch-queries-logging`).
2. Run `python dev/tools/explain_queries.py` locally with `DATABASE_URL` pointed at a copy of production DB.

If you want, I can add an automated CI job that runs the `explain_queries` script against a test DB snapshot and uploads the results as an artifact — want me to add that to the PR?
