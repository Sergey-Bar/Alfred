# DevOps README

This file documents deploy, secrets handling, and basic checks for the Alfred project.

Secrets
- Do NOT commit secrets to the repository.
- Use your cloud provider's secret manager or HashiCorp Vault for production secrets.
- For local development, use a `.env` file added to `.gitignore` or Docker Compose environment variables.

Recommended secret names:
- `DATABASE_URL` - Postgres connection string
- `REDIS_URL` - Redis connection string
- `GHCR_PAT` - GitHub Container Registry Personal Access Token (for CI push)

Local development
- Start dependencies (Postgres, Redis) using Docker Compose for local testing:

```powershell
# from repo root
cd dev/devops/docker
docker compose up -d
```

- Run backend tests locally:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements/requirements-dev.txt
pytest -q
```

Helm and Kubernetes
- To validate the Helm chart templates locally:

```powershell
helm template alfred dev/devops/charts/alfred -f dev/devops/charts/alfred/values.yaml
```

CI
- The `ci.yml` workflow runs lint, backend tests, frontend tests/build, and a Helm template check on PRs.
- Image security scanning is performed by `security-scan.yml` (Trivy).

Deploy checklist (staging)
1. Ensure all PR checks pass (CI + security scans).
2. Run `helm template` and review rendering.
3. Deploy to staging using your helm values (ensure `redis.enabled=true` if worker is required).
4. Run smoke tests (`.github/workflows/e2e-smoke.yml` can be used in CI).

If you need Vault or cloud provider specific instructions, add them to this README under the relevant section.
