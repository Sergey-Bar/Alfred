# Repository Structure

This document describes the repository layout, conventions and where to find things.

Top-level layout

- `.github/` - GitHub workflows, issue/PR templates, CODEOWNERS
- `backend/app/` - Backend FastAPI application code (Python)
- `backend/alembic/` - Database migration scripts
- `backend/config/` - Environment templates and runtime config
- `devops/docker/` - Dockerfile and compose files
- `docs/` - User and developer documentation
- `frontend/` - React + Vite admin dashboard
- `devops/k8s/` - Kubernetes manifests (staging/production)
- `devops/scripts/` - Helper scripts (deploy, backup, restore)
- `frontend/static/` - Built frontend assets (copied during build)
 - `dist/` - Optional minimal deployable bundle produced by `scripts/build_minimal.sh`
- `backend/tests/` - Pytest test suites
- `backend/requirements/requirements.txt` / `backend/requirements/requirements-dev.txt` - Python deps
- `pyproject.toml` - project metadata and tooling config

Conventions

- Formatting: `black`, `isort`, `ruff` (configured in `pyproject.toml`).
- Type checking: `mypy` for backend. Keep `disallow_untyped_defs` where possible.
- Tests: backend uses `pytest` with in-memory SQLite for unit tests. Frontend uses `vitest` for unit tests.
- Branching: use feature branches (`feature/`), PRs must pass CI and code review.
- Commits: follow Conventional Commits (pre-commit configured to help).
- Secrets: never store API keys in the repo. Use environment variables and secrets managers.

Adding new components

-- Backend: add code under `backend/app/`, include tests in `backend/tests/`, add migrations to `backend/alembic/versions/`.
- Frontend: add pages/components under `frontend/src/`, add unit tests under `frontend/src/__tests__/`.
-- Deployments: place k8s manifests under `devops/k8s/<env>/` and update `devops/scripts/deploy_k8s.sh`.

CI and Releases

- CI workflows live in `.github/workflows/` and run linting, tests, and builds.
- Releases are created via tags (`vX.Y.Z`) and the `deploy.yml` workflow.

Where to look first

- `README.md` - project overview and quick start
- `docs/` - deeper guides (Install, API, Architecture)
-- `backend/app/main.py` - FastAPI application entrypoint
- `frontend/` - admin dashboard source

If something is unclear, update this doc or open an issue with the `docs` label.

