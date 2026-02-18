# Gateway (minimal scaffold)

This is a minimal Go gateway scaffold for the AI Orchestrator project.

Run locally:

```bash
cd services/gateway
go run .
```

Build Docker image:

```bash
docker build -t ai-orchestrator-gateway:local .
# run with a custom address to avoid port conflicts:
# GATEWAY_ADDR=":8081" docker run -p 8081:8081 ai-orchestrator-gateway:local
```

Health endpoints:

- `GET /healthz` — liveness
- `GET /ready` — readiness

Next steps:

- Add router (chi/gorilla), middleware, logging, config, and provider connectors.

## Environment

You can provide runtime configuration via environment variables or a `.env` file in `services/gateway`.

- `DATABASE_URL` (default: postgres://postgres:postgres@postgres:5432/ao?sslmode=disable)
- `REDIS_URL` (default: redis://redis:6379)
- `ENV` (development|production)

The scaffold uses `github.com/joho/godotenv` to load `.env` files if present.
