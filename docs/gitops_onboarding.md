# [AI GENERATED]

# Model: GitHub Copilot (GPT-4.1)

# Logic: Scaffold GitOps onboarding documentation for moderate roadmap item.

# Why: Roadmap item 17 calls for GitOps onboarding docs to improve developer onboarding and operational consistency.

# Root Cause: No clear, unified GitOps onboarding documentation exists in the project.

# Context: This doc provides step-by-step instructions for setting up GitOps workflows (ArgoCD/Flux), repo structure, secrets, and best practices for new contributors and DevOps engineers. Future improvements: add screenshots, troubleshooting, and advanced multi-region patterns. For advanced GitOps patterns, consider using a more specialized model (Claude Opus).

---

# GitOps Onboarding Guide

## Overview

This guide provides step-by-step instructions for onboarding new contributors and DevOps engineers to Alfred's GitOps workflows. It covers repo structure, ArgoCD/Flux setup, secrets management, and best practices for production and staging environments.

## Prerequisites

- Access to Alfred's GitHub repository
- kubectl installed and configured
- Access to target Kubernetes cluster (staging/production)
- ArgoCD or Flux installed (see below)

## Repo Structure

- All deployment manifests are in `devops/merged/k8s/`
- Dockerfiles are in `devops/merged/docker/` and `docker-tools/`
- Secrets and config templates are in `devops/merged/secrets.md`
- Helm charts are in `devops/merged/charts/alfred/`

## GitOps Workflow (ArgoCD Example)

1. Fork and clone the repo
2. Make changes to manifests or Helm charts
3. Push to a feature branch and open a PR
4. CI/CD runs tests and builds images
5. On merge to main, ArgoCD auto-syncs manifests to the cluster

## Setting Up ArgoCD

1. Install ArgoCD: https://argo-cd.readthedocs.io/en/stable/getting_started/
2. Add Alfred app:
   ```bash
   argocd app create alfred \
     --repo https://github.com/your-org/alfred.git \
   --path devops/merged/k8s/production \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace alfred-prod
   ```
3. Sync and monitor deployment:
   ```bash
   argocd app sync alfred
   argocd app get alfred
   ```

## Setting Up Flux (Alternative)

1. Install Flux: https://fluxcd.io/docs/installation/
2. Bootstrap with your repo:
   ```bash
   flux bootstrap github \
     --owner=your-org \
     --repository=alfred \
   --path=devops/merged/k8s/production
   ```
3. Monitor sync status:
   ```bash
   flux get kustomizations
   ```

## Secrets Management

- Store secrets in cloud secret manager or sealed-secrets (see `devops/merged/secrets.md`)
- Never commit raw secrets to the repo

## Best Practices

- Use PRs for all changes; never push directly to main
- Keep manifests DRY with Helm/Kustomize
- Use branch protection and CI checks
- Document all changes in the changelog

## Troubleshooting

- Check ArgoCD/Flux UI for sync errors
- Validate manifests with `kubectl apply --dry-run=client`
- See `devops/merged/README.md` for advanced troubleshooting

---

For questions, contact the DevOps team or see the #devops channel in Slack.
