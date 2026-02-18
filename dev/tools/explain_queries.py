"""
Lightweight EXPLAIN benchmark for representative queries.
Run locally with: `python dev/tools/explain_queries.py` (ensure `DATABASE_URL` env var points to your DB).
"""

import os

from sqlalchemy import text
from sqlmodel import create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")
engine = create_engine(DATABASE_URL, echo=False)

QUERIES = {
    "teams_batch_count": "SELECT team_member_links.team_id, COUNT(team_member_links.user_id) AS cnt FROM team_member_links WHERE team_member_links.team_id IN (SELECT id FROM teams LIMIT 10) GROUP BY team_member_links.team_id;",
    "leaderboard_aggregate": "SELECT CAST(request_logs.user_id AS TEXT) as uid, SUM(request_logs.prompt_tokens) as sum_prompt, SUM(request_logs.completion_tokens) as sum_completion, COUNT(request_logs.id) as cnt FROM request_logs WHERE request_logs.created_at >= DATE('now', '-30 days') GROUP BY CAST(request_logs.user_id AS TEXT) LIMIT 50;",
    "pending_approvals_for_team_admin": "SELECT approval_request.* FROM approval_request WHERE approval_request.status = 'pending' AND approval_request.user_id IN (SELECT user_id FROM team_member_links WHERE team_id IN (SELECT team_id FROM team_member_links WHERE user_id = ?));",
}


def run_explain(sql: str, params=None):
    with engine.connect() as conn:
        try:
            if engine.url.drivername.startswith("sqlite"):
                # SQLite uses EXPLAIN QUERY PLAN
                plan = conn.execute(text("EXPLAIN QUERY PLAN " + sql), params or {}).fetchall()
            else:
                plan = conn.execute(text("EXPLAIN " + sql), params or {}).fetchall()
            return plan
        except Exception as e:
            return f"EXPLAIN failed: {e}"


if __name__ == "__main__":
    print(f"Running EXPLAIN against: {DATABASE_URL}\n")
    for name, q in QUERIES.items():
        print(f"--- {name} ---")
        plan = run_explain(q, params=None)
        print(plan)
        print()

    print("Done.")
