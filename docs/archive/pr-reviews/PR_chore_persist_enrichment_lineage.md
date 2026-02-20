# PR Draft: chore/persist-enrichment-lineage

Branch: `chore/persist-enrichment-lineage`

Summary:

- Convert demo in-memory stores for data enrichment and data lineage to persistent SQLModel-backed tables.
- Add Alembic migration stub and minimal `env.py` to run migrations locally.
- Apply lint/format fixes across backend and tests; ensure tests pass.

Files of interest:

- `src/backend/app/routers/data_enrichment.py`
- `src/backend/app/routers/data_lineage.py`
- `src/backend/app/models.py` (new persistent models)
- `src/backend/alembic/versions/20260216_add_enrichment_lineage.py`
- `src/backend/alembic/env.py`

Testing performed:

- `pytest` run with `PYTHONPATH='.;src/backend'` — result: 75 passed, 2 skipped.
- Lint/format: `ruff format`, `black` applied.

Action items for reviewer:

- Verify migrations & `down_revision` ordering against repo migration history.
- Confirm CI secrets and pipeline adjustments.
- Approve and merge; run migrations in staging before deploy.
