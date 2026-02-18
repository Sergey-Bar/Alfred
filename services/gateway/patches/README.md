Draft fixes for `services/gateway` failing tests

This folder contains a short plan and recommended code changes to try when gateway unit tests fail in CI.

High-level hypotheses (common causes):

- Tests rely on listening ports or fixed ports; use ephemeral ports (`:0`) or `httptest.NewServer` so parallel runs don't conflict.
- Timing/flaky tests use `time.Sleep` — replace with deterministic synchronization (channels, contexts, or `retry` with backoff and timeouts).
- Tests depend on global state initialized at import time — refactor to inject dependencies (e.g., `createRouter(cfg)` or `NewApp(db)` factory) so tests control lifecycle.
- Redis/Postgres connectivity in tests times out — mock external services where possible or use testcontainers/docker-compose in integration tests.

Candidate quick changes to try (apply locally on a branch):

1. Convert server tests to `httptest.NewServer` and avoid fixed ports.

2. Replace sleeps with `require.Eventually()` (testify) or custom wait-for condition.

3. Ensure `config_test.go` uses the package-external pattern (package `config_test`) and imports `services/gateway/config` to avoid import cycles.

4. Add `t.Parallel()` only where safe; if tests share global state, remove `t.Parallel()`.

Commands to create a local branch and apply fixes (run locally):

```powershell
cd services/gateway
git checkout -b gateway/test-fixes-draft
# edit files as suggested in this README
go test ./... -v
git add -A
git commit -m "test(gateway): draft fixes for flaky tests"
git push --set-upstream origin gateway/test-fixes-draft
```

When pushed, CI will run and the diagnostics workflow will upload `gateway-tests.log`; share that artifact for triage.

If you want, I can prepare a series of concrete code edits in this branch — say `yes` and I'll make an initial attempt at deterministic fixes (but I will need `gateway-tests.log` to iterate precisely).
