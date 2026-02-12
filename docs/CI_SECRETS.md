# CI / Deployment Secrets

This document lists GitHub secrets and environment variables required for CI/CD and deployments.

## GitHub Secrets (recommended)
- `GITHUB_TOKEN` (provided automatically) - Used by actions to access the repo.
- `GHCR_PAT` - Personal access token with `write:packages` for pushing images to GitHub Container Registry.
- `DOCKER_USERNAME` / `DOCKER_PASSWORD` - If using Docker Hub.
- `CODECOV_TOKEN` - Upload coverage reports to Codecov.
- `KUBE_CONFIG_DATA` - Base64-encoded kubeconfig for `kubectl` deployments (optional for automation).
- `KUBE_CONFIG_DATA` - Base64-encoded kubeconfig for `kubectl` deployments (optional for automation). Example value is `$(cat ~/.kube/config | base64 -w0)` on Linux/macOS.
- `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` - Container registry credentials (if private registry).
- `SLACK_WEBHOOK_URL` - For notifications in CI (optional).

## Environment Variables used by workflows
- `DATABASE_URL` - Database connection string for integration tests (CI only)
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` - LLM provider keys (do NOT store production keys in CI)

## How to add secrets
1. Go to repository Settings -> Secrets -> Actions
2. Click "New repository secret"
3. Add the secret name and value

## Using secrets in workflows
Use secrets in workflows as `${{ secrets.NAME }}`. Example:

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  GHCR_PAT: ${{ secrets.GHCR_PAT }}
``` 

To decode `KUBE_CONFIG_DATA` in a workflow and write to kubeconfig:

```yaml
- name: Configure kubeconfig
  run: echo "$KUBE_CONFIG_DATA" | base64 --decode > $HOME/.kube/config
  env:
    KUBE_CONFIG_DATA: ${{ secrets.KUBE_CONFIG_DATA }}
```

## Security notes
- Do not commit secrets to the repository.
- Use scoped service accounts for deployments.
- Rotate registry tokens periodically.
