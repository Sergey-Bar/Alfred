## Summary

Describe the change and why it was made.

## Changes

- Persist enrichment pipelines, enrichment jobs, and lineage events (SQLModel models + Alembic migration).
- Replace in-memory demo stores with DB-backed endpoints (`data_enrichment`, `data_lineage`).
- Add Alembic `env.py` and migration stub to create tables.
- Lint & format fixes; tests pass locally (75 passed, 2 skipped).

## Migration

Run the following to apply DB migrations in your environment (set `DATABASE_URL` first):

```bash
cd src/backend
alembic -c config/alembic.ini upgrade head
```

## Testing

- Unit, integration, and backend tests run locally: `pytest` (75 passed, 2 skipped).

## Notes

- CI requires updated secrets (e.g., `CI_POSTGRES_PASSWORD`) per `.github/workflows/ci.yml`.
- Reviewer: @Sergey-Bar

## Checklist

- [ ] Migration reviewed
- [ ] QA run E2E tests in staging
- [ ] Add any follow-up tasks to the PR
