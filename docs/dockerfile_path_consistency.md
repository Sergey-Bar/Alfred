# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Documents the unified Dockerfile path strategy and migration plan for Alfred.
# Why: Roadmap item 19 calls for resolving inconsistent Dockerfile paths to reduce confusion and build errors.
# Root Cause: Multiple Dockerfiles exist in different locations (dev/devops/docker/ and docker-tools/), referenced inconsistently in Compose files and CI.
# Context: This doc explains the unification approach, recommended path, and migration steps. Future: automate validation, add CI checks, and document multi-stage builds for advanced use cases.

---

# Dockerfile Path Consistency Guide

## Problem
Multiple Dockerfiles exist:
- dev/devops/docker/Dockerfile (referenced in dev/devops/docker/docker-compose.yml)
- docker-tools/Dockerfile (referenced in devops/merged/docker/docker-compose.yml)

This causes confusion, build drift, and inconsistent local/dev/prod images.

## Solution
- **Primary Dockerfile:** Use `docker-tools/Dockerfile` as the canonical build file for all environments.
- **Migration:**
  1. Update all Compose files and CI scripts to reference the unified Dockerfile path.
  2. Remove or deprecate the duplicate in `dev/devops/docker/` after validation.
  3. Align build args, base images, and dependencies as needed.
- **Versioning:**
  - Standardize on a single Dockerfile for all environments.
  - Use multi-stage builds for advanced scenarios (future).

## Usage
```sh
# Build the image
cd docker-tools
 docker build -t alfred-api .
```

## Best Practices
- Use `.dockerignore` to optimize builds
- Validate with `docker build --no-cache .`
- Document all changes in the changelog

## Next Steps
- Remove deprecated files after migration window
- Add CI check for drift/duplication
- Document multi-stage build patterns (future)

---

For questions, contact the DevOps team or see the #devops channel in Slack.
