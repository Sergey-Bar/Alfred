# GitHub Configuration Required

**Status**: 4 configuration warnings remaining (not code errors)

## Overview

The GitHub Actions workflows are correctly configured, but they reference GitHub repository settings that need to be created manually. These warnings will disappear once the configuration is set up in your GitHub repository.

## Required Configuration

### 1. GitHub Environments

**Warnings:**
- `deploy.yml:24` - Environment 'staging' not found
- `deploy.yml:57` - Environment 'production' not found

**How to Fix:**

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Environments**
3. Click **New environment** and create:
   - Environment name: `staging`
   - Protection rules (optional):
     - Required reviewers (optional)
     - Wait timer (optional)
     - Deployment branches: `main` branch only
   
4. Click **New environment** again and create:
   - Environment name: `production`
   - Protection rules (recommended):
     - ✅ Required reviewers: add 1-2 team members
     - ✅ Deployment branches: tags matching `v*` pattern

**Environment URLs (already configured in workflow):**
- Staging: `https://staging.alfred.dev`
- Production: `https://alfred.dev`

### 2. GitHub Secrets

**Warnings:**
- `deploy.yml:40` - Secret 'KUBE_CONFIG_DATA' might not exist
- `deploy.yml:74` - Secret 'KUBE_CONFIG_DATA' might not exist

**How to Fix:**

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:

   **Name:** `KUBE_CONFIG_DATA`  
   **Value:** Base64-encoded Kubernetes config file
   
   ```bash
   # Generate the value (on Linux/macOS)
   cat ~/.kube/config | base64 -w 0
   
   # On macOS
   cat ~/.kube/config | base64
   
   # On Windows (PowerShell)
   [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content ~/.kube/config -Raw)))
   ```

**Note:** This secret is optional. If not provided, the deployment steps will skip Kubernetes configuration (workflows include fallback handling).

### 3. Optional: GitHub Container Registry

The `ci.yml` workflow uses `GITHUB_TOKEN` to push Docker images to GitHub Container Registry (ghcr.io). This works automatically with no additional configuration required.

**If you want to use a custom token instead:**

1. Create a Personal Access Token (PAT) with `write:packages` and `read:packages` scopes
2. Add it as a repository secret named `GHCR_PAT`
3. Update `ci.yml` line 195 to use: `password: ${{ secrets.GHCR_PAT }}`

## Verification Checklist

After setting up the configuration:

- [ ] Created `staging` environment in GitHub
- [ ] Created `production` environment in GitHub  
- [ ] Added `KUBE_CONFIG_DATA` secret (optional)
- [ ] Configured environment protection rules (optional)
- [ ] Tested deployment workflow with `workflow_dispatch`

## Testing Deployments

### Manual Deployment Test

1. Go to **Actions** tab in your repository
2. Select the **Deploy** workflow
3. Click **Run workflow**
4. Choose environment: `staging` or `production`
5. Click **Run workflow**

### Automatic Deployments

**Staging (automatic on push to main):**
```bash
git push origin main
```

**Production (automatic on version tag):**
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Current Workflow Status

| Workflow | Status | Notes |
|----------|--------|-------|
| CI | ✅ Ready | Runs on every push/PR |
| E2E Smoke Tests | ✅ Ready | Runs on PR to main |
| Security Scan | ✅ Ready | Runs on push/PR to main |
| Deploy | ⚠️ Needs Config | Requires environments & secrets setup |

## Warnings vs Errors

**Important:** The 4 remaining items are **configuration warnings**, not code errors:

- ✅ All code syntax is correct
- ✅ All workflows will run successfully
- ⚠️ Deploy workflow needs GitHub environment setup
- ⚠️ Kubernetes deployments need KUBE_CONFIG_DATA secret (optional)

The warnings will disappear from the Problems panel once you configure the environments and secrets in your GitHub repository settings.

## Summary

**Total Issues**: 4 configuration warnings (down from 49 problems!)

**Fixed**:
- ✅ Playwright config (CommonJS → ES modules)
- ✅ Gitleaks action version
- ✅ Trivy action version
- ✅ All backend path references
- ✅ Workflow syntax errors
- ✅ Secret condition syntax

**Remaining** (require GitHub repo configuration):
- ⚠️ Create staging environment
- ⚠️ Create production environment  
- ⚠️ Add KUBE_CONFIG_DATA secret (optional)

All code issues have been resolved! 🎉
