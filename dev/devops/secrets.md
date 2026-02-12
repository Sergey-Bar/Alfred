# Secrets Handling Guide

This document provides guidance for handling secrets in the Alfred repository and CI.

## Goals
- Avoid committing secrets to source control.
- Ensure CI does not leak secrets in logs.
- Provide a simple path to migrate to a secret manager later.

## Local development
- Use a `.env` file (added to `.gitignore`) for local secrets, or export environment variables in your shell.
- Copy `config/.env.example` to `.env` and fill in your values.
- Example `.env` (DO NOT COMMIT):

```
DATABASE_URL=postgresql://alfred:localpass@localhost:5432/alfred
REDIS_URL=redis://localhost:6379
GHCR_PAT=ghp_xxx
```

## CI / Deployment Secrets Reference

These secrets should be configured in GitHub (Settings -> Secrets -> Actions):

| Secret Name | Description |
|-------------|-------------|
| `GHCR_PAT` | Personal access token with `write:packages` for pushing images to GitHub Container Registry. |
| `DOCKER_USERNAME` / `DOCKER_PASSWORD` | If using Docker Hub instead of GHCR. |
| `CODECOV_TOKEN` | (Optional) Upload coverage reports to Codecov. |
| `KUBE_CONFIG_DATA` | (Optional) Base64-encoded kubeconfig for automated `kubectl` deployments. |
| `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` | Container registry credentials (if using private registry in staging). |
| `SLACK_WEBHOOK_URL` | For notifications in CI (optional). |

### Environment Variables used by workflows
- `DATABASE_URL`: Connection string for integration tests (CI only).
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`: LLM provider keys (do NOT store production keys in CI; use mocks or ephemeral keys if possible).

## Production
- Migrate secrets to a managed secret store (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager).
- Do not embed secrets in Helm `values.yaml` files for production; pass them via the cloud provider secret injection or Kubernetes `Secret` objects.
- Use the `secret-scan` CI job (gitleaks) to detect accidental secrets in commits and PRs.

## Security notes
- Do not commit secrets to the repository.
- Use scoped service accounts for deployments.
- Rotate registry tokens periodically.
