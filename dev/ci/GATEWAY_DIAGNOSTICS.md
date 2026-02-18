Gateway diagnostics - how to run tests and fetch logs

This file explains how to reproduce gateway tests locally and how to fetch the `gateway-tests.log` artifact produced by the diagnostics workflow in GitHub Actions.

Run tests locally

```bash
cd services/gateway
# ensure you have Go 1.20+ installed
go mod tidy
# run tests and save output to a file
go test ./... -v 2>&1 | tee gateway-tests.log
```

If you want to push the log into the repo for sharing (temporary):

```bash
mkdir -p dev/ci/logs
cp gateway-tests.log dev/ci/logs/gateway-tests-$(date +%Y%m%d-%H%M%S).log
# optionally commit (prefer not to commit logs to long-lived branches)
```

Fetch artifact from GitHub Actions (recommended)

- Using `gh` (GitHub CLI):

```bash
# list workflow runs for gateway-diagnostics
gh run list --workflow gateway-diagnostics.yml --limit 20
# view runs and pick the run-id, then download artifacts
gh run download <run-id> --name gateway-test-logs --dir dev/ci/artifacts
```

- Via web UI: open the workflow run, expand 'Artifacts', and download `gateway-test-logs`.

Next steps for the agent

- Provide the `gateway-tests.log` file here or upload it to `dev/ci/artifacts/` and tell me where it is; I'll triage failures and propose fixes.
