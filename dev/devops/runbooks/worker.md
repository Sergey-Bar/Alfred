# Worker Runbook

Purpose
- How to start and validate the RQ worker that processes notifications and background tasks.

Prerequisites
- Docker Compose with the `with-cache` profile (includes `redis` and `worker` services).
- Environment variables: `REDIS_URL` (e.g. redis://redis:6379/0), `DATABASE_URL`.

Start locally (Docker Compose)

```powershell
cd dev/devops/docker
docker compose up --build --profile with-cache -d
```

Check worker logs

```powershell
docker compose logs -f worker
```

Enqueue a test job (from API container)

```powershell
docker compose exec api bash
python -c "from app.notifications import enqueue_notification; enqueue_notification('approval_requested', {'user_id':'test','user_name':'Test','user_email':'test@example.com','requested_credits':1.0,'reason':'smoke'})"
```

Validation
- Worker logs should show `backend.app.workers.process_task` execution and any provider send attempts.
- If Redis is not reachable, the API will fall back to in-process execution (see `backend/app/notifications.py`).

Troubleshooting
- If worker exits immediately: ensure `redis` is healthy and `REDIS_URL` points to it.
- If jobs fail repeatedly, inspect provider credentials and network connectivity.
