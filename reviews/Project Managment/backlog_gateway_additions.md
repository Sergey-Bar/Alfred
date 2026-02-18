# Gateway: Additional Backlog Items (automated scan)

**Date:** 2026-02-18

This file contains a focused list of actionable items discovered while scanning `services/gateway`.

Actionable items

- Run `go mod tidy` inside `services/gateway` and commit the generated `go.sum` so CI can run `go test` reliably.
- Run `go test ./... -v` locally and fix any failing tests.
- The agent environment lacks the `go` tool; tests could not be executed here — run the commands locally (below).
- Update `services/gateway/go.mod` to a canonical module path for reproducible external builds (example: `github.com/<org>/ai-orchestrator/services/gateway`).
- Add `golangci-lint` and a lint step to `.github/workflows/ci.yml` to catch style/possible bugs early.
- Add an integration test that runs via `docker compose` (Postgres + Redis) to validate migrations and Redis connectivity.

Local verification commands

```bash
cd services/gateway
# tidy dependencies and generate go.sum
go mod tidy
# run unit tests
go test ./... -v
# commit the lockfile
git add go.sum
git commit -m "chore(gateway): add go.sum"
git push
```

Options I can take next (pick one):

- Prepare a PR that updates the `go.mod` module path (you provide the canonical path).
- Add a CI job for `golangci-lint` and a linting step in `.github/workflows/ci.yml`.
- Create an integration test scaffold that runs against `docker compose`.

If you want me to proceed with any of the options above, tell me which one and I'll implement it.

Findings from quick code scan

- `redisclient.New` ignores the error returned by `redis.ParseURL(cfg.RedisURL)`; if the URL is invalid this may lead to unexpected behavior. Suggest changing `New` to return `(*Client, error)` and propagate parse/creation errors.
- `config_test.go` is declared as `package main` which is unconventional for package-level tests—consider changing to `package config` or `package config_test` for clearer isolation and to avoid accidental dependency on `main` package symbols.
- Add a `.dockerignore` to the gateway to avoid copying local artifacts into the Docker build context (e.g., `.git`, `node_modules`, `bin/`, `.venv`).
- Consider tightening error logs on Redis ping to include the configured `REDIS_URL` (redacted) to aid diagnostics.
- The migrations file uses table name `wallets_events`; confirm this naming is intended (plural `wallets_events`) and matches any DB code that will query it.

Suggested immediate fixes (I can implement any of these):

1. Make `redisclient.New(cfg *config.Config) (*Client, error)` and handle `redis.ParseURL` error. Update `main.go` call to handle the error.
2. Add `.dockerignore` and minor Dockerfile sanity checks (install `ca-certificates` in runtime if needed for TLS).
3. Change `config_test.go` package to `config_test` and import `ai-orchestrator/gateway/config` (or `package config`), then run tests to verify.
4. Add a CI job to fail if `go.sum` is missing and an optional `golangci-lint` step.

I recorded these items in the project TODOs (IDs 21–24). Next I can open PRs for any of the above; which shall I start with? If no preference, I'll implement the `redisclient` error handling and add `.dockerignore` first.

Updates applied:

- Added `services/gateway/.golangci.yml` to enable `golangci-lint` configuration.
- Added `services/gateway/integration_test.go` as a scaffolded integration test that is skipped by default. Set `RUN_GATEWAY_INTEGRATION=1` to run locally after starting docker-compose.
- Updated CI (`.github/workflows/ci.yml`) to install and run `golangci-lint` for the gateway when `.golangci.yml` exists, and to fail early if `services/gateway/go.sum` is missing.

Next recommended actions:

- Run `go mod tidy` locally and commit `go.sum` so CI gateway tests can run.
- Run unit tests locally and fix any failures.
- Optionally enable integration tests by setting `RUN_GATEWAY_INTEGRATION=1` and starting `docker compose up`.
