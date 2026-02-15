# Support Playbook

Purpose

- Triage common issues reported by users and provide steps to reproduce, gather diagnostics, and escalate.

Common Issues

- Authentication/API key failures
  - Check request logs for hashed API key usage and match timestamps.
  - Ask user for request ID and timestamp; correlate with logs.

- Transfers/Approvals not applied
  - Verify database `token_transfers` and `approval_requests` tables for records.
  - Check background worker logs for notification delivery failures and RQ queue state.

Gathering diagnostics

- Ask user for: user email, approximate timestamp, request ID (if present), and a screenshot of the error.
- Commands for on-call to run (run from repo root):

```powershell
# NOTE: use the repo compose file path when running locally
# List recent token transfers
docker compose -f devops/merged/docker/docker-compose.yml exec db psql -U alfred -d alfred -c "select id, sender_id, recipient_id, amount, status, created_at from token_transfers order by created_at desc limit 20;"

# Tail API logs
docker compose -f devops/merged/docker/docker-compose.yml logs -f api

# Tail worker logs (if using compose worker service)
docker compose -f devops/merged/docker/docker-compose.yml logs -f worker

# Check RQ queue length via redis-cli (if available)
docker compose -f devops/merged/docker/docker-compose.yml exec redis redis-cli LLEN rq:queue:default

# Query recent audit logs (requires DB access)
docker compose -f devops/merged/docker/docker-compose.yml exec db psql -U alfred -d alfred -c "select id, actor_user_id, action, target_type, target_id, created_at from audit_logs order by created_at desc limit 20;"
```

Escalation

- If logs show 5xx errors or repeated failures, escalate to SRE and include: request IDs, user info, affected endpoints, and recent deploys.
