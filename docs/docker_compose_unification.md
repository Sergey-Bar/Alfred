# [AI GENERATED]

# Model: GitHub Copilot (GPT-4.1)

# Logic: Documents the unified Docker Compose strategy, locations, and migration plan for Alfred.

# Why: Roadmap item 18 calls for resolving duplicate/fragmented Docker Compose files to reduce confusion and operational risk.

# Root Cause: Multiple docker-compose.yml files exist in dev/devops/docker/ and devops/merged/docker/ with minor differences (e.g., Postgres version, Dockerfile path).

# Context: This doc explains the unification approach, recommended file, and migration steps. Future: automate validation, add CI checks, and document multi-environment overrides.

---

# Docker Compose Unification Guide

## Problem

Multiple Docker Compose files exist:

- devops/merged/docker/docker-compose.yml (Postgres 16, Dockerfile path: devops/merged/docker/Dockerfile)
- devops/merged/docker/docker-compose.yml (Postgres 16, Dockerfile path: devops/docker/Dockerfile)

This causes confusion, drift, and inconsistent local/dev/prod environments.

## Solution

- **Primary Compose File:** Use `devops/merged/docker/docker-compose.yml` as the canonical source for all environments.
- **Migration:**
  1. Update all docs/scripts to reference the unified file.
  2. Remove or deprecate the duplicate in `devops/merged/docker/` after validation.
  3. Align service versions, environment variables, and Dockerfile paths as needed.
- **Versioning:**
  - Use Postgres 16+ for all environments (update if needed).
  - Standardize Dockerfile location to `devops/docker/Dockerfile`.

## Usage

```sh
cd devops/merged/docker
# Start all services
 docker compose up -d
# Stop all services
 docker compose down
```

## Best Practices

- Use `.env` for secrets and overrides
- Validate with `docker compose config`
- Document all changes in the changelog

## Next Steps

- Remove deprecated files after migration window
- Add CI check for drift/duplication
- Document multi-environment overrides (future)

---

For questions, contact the DevOps team or see the #devops channel in Slack.
