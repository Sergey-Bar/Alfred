# Gateway CONTRIBUTING

Quick start for local development and tests for the gateway service.

## Prerequisites

- Go 1.20+ installed and on your `PATH` (https://golang.org/dl/)
- Docker & Docker Compose (for local Postgres/Redis)

## Run locally

Install module dependencies and tidy:

```bash
cd services/gateway
go mod tidy
```

Run tests:

```bash
go test ./... -v
```

Run the service:

```bash
go run .
# or build
go build -o bin/gateway .
./bin/gateway
```

Docker compose (starts postgres + redis + gateway):

```bash
cd ../../
docker compose up --build
# then visit http://localhost:8080/healthz (or set `GATEWAY_ADDR` env var before running to change listen address)
```

## Developer checklist

- Run `go mod tidy` and commit `go.sum` when adding or updating deps.
- Add unit tests for new functionality and ensure CI passes.
- Run `golangci-lint run` (optional) before opening PRs.

- To run the gateway linter in CI we use `golangci-lint` with configuration in `.golangci.yml`.
- If you add or update linters, run `golangci-lint run` locally and fix reported issues before pushing.

## Integration tests

- Integration tests are scaffolded in `services/gateway/integration_test.go` and are skipped by default.
- To run integration tests locally start Postgres and Redis via Docker Compose and set:

```bash
export RUN_GATEWAY_INTEGRATION=1
go test -run TestIntegration -v
```

## Notes on `go.mod` and module path

- The current `go.mod` module path is a placeholder. For reproducible CI builds and publishing, replace the module path in `services/gateway/go.mod` with your canonical repository import path (for example `github.com/<org>/alfred/services/gateway`).
- After changing dependencies run:

```bash
cd services/gateway
go mod tidy
git add go.sum
git commit -m "chore(gateway): update go.sum"
```

## Notes

- The module path in `go.mod` is currently a placeholder. For publishing or multi-repo CI, replace with your canonical module path (e.g., `github.com/<org>/ai-orchestrator/services/gateway`).
