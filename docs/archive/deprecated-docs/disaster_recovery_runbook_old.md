# Disaster Recovery Runbook — Alfred Platform

> **Classification:** Internal — Operations Critical  
> **Owner:** Sergey Bar + SRE On-call  
> **Review Cycle:** Semi-annual drill required  
> **Last Updated:** 2026-02-18

---

## 1. Overview

This runbook covers disaster recovery (DR) procedures for the Alfred AI Control & Economy Platform. It addresses:

- Complete service outage recovery
- Database restoration
- Provider failover escalation
- Data corruption remediation
- Credential compromise response

**Recovery Objectives:**

| Metric                             | Target     | Maximum Tolerance |
| ---------------------------------- | ---------- | ----------------- |
| **RTO** (Recovery Time Objective)  | 30 minutes | 2 hours           |
| **RPO** (Recovery Point Objective) | 5 minutes  | 15 minutes        |
| **MTTR** (Mean Time to Repair)     | 15 minutes | 60 minutes        |

---

## 2. Emergency Contacts

| Role                   | Name       | Contact        | Escalation Order     |
| ---------------------- | ---------- | -------------- | -------------------- |
| Platform Owner         | Sergey Bar | [internal]     | 1st                  |
| SRE On-Call            | Rotation   | PagerDuty      | 1st (auto)           |
| Database Admin         | [TBD]      | [internal]     | 2nd                  |
| Security Lead          | [TBD]      | [internal]     | If security incident |
| Cloud Provider Support | AWS/GCP    | Support portal | 3rd                  |

---

## 3. Severity Classification

| Severity  | Description              | Response Time       | Examples                                          |
| --------- | ------------------------ | ------------------- | ------------------------------------------------- |
| **SEV-1** | Complete platform outage | Immediate (< 5 min) | DB unreachable, gateway down, auth system failure |
| **SEV-2** | Partial degradation      | < 15 min            | Single provider down, cache failure, high latency |
| **SEV-3** | Non-critical issue       | < 1 hour            | Dashboard errors, export failures, stale metrics  |
| **SEV-4** | Cosmetic/minor           | Next business day   | UI glitches, non-critical log errors              |

---

## 4. Procedure: Complete Service Outage (SEV-1)

### 4.1. Initial Assessment (0-5 minutes)

```bash
# 1. Check service health endpoints
curl -s https://alfred.internal/health | jq .
curl -s https://alfred.internal/v1/health | jq .

# 2. Check container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
# Or in Kubernetes:
kubectl get pods -n alfred -o wide

# 3. Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# 4. Check Redis connectivity
redis-cli -u $REDIS_URL ping

# 5. Review recent deployments
git log --oneline -5 origin/main
```

### 4.2. Service Recovery (5-15 minutes)

```bash
# Option A: Rolling restart (minimal downtime)
kubectl rollout restart deployment/alfred-gateway -n alfred
kubectl rollout restart deployment/alfred-backend -n alfred
kubectl rollout restart deployment/alfred-frontend -n alfred

# Option B: Rollback to last known good version
kubectl rollout undo deployment/alfred-gateway -n alfred
kubectl rollout undo deployment/alfred-backend -n alfred

# Option C: Docker Compose recovery
docker compose down
docker compose up -d
docker compose logs -f --tail=100

# Verify recovery
kubectl rollout status deployment/alfred-gateway -n alfred --timeout=120s
```

### 4.3. Post-Recovery Validation

```bash
# Run smoke tests
pytest qa/Backend/ -k "smoke" -v --timeout=30
npm run test:e2e -- --grep "smoke"

# Verify critical paths
python tools/check_health.py --full
```

---

## 5. Procedure: Database Recovery (SEV-1)

### 5.1. Connection Pool Exhaustion

```bash
# Check active connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
psql $DATABASE_URL -c "SELECT state, count(*) FROM pg_stat_activity GROUP BY state;"

# Kill idle connections (if pool exhausted)
psql $DATABASE_URL -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'idle'
    AND query_start < now() - interval '10 minutes'
    AND pid != pg_backend_pid();
"

# Restart backend to reset pool
# NOTE: Backend uses SQLAlchemy pool with pool_pre_ping=True (BUG-001 fix)
kubectl rollout restart deployment/alfred-backend -n alfred
```

### 5.2. Full Database Restore

```bash
# 1. Identify latest backup
aws s3 ls s3://alfred-backups/db/ --recursive | sort | tail -5

# 2. Download backup
aws s3 cp s3://alfred-backups/db/latest/alfred_dump.sql.gz ./restore/

# 3. Create restore database
createdb alfred_restore

# 4. Restore from backup
gunzip -c restore/alfred_dump.sql.gz | psql alfred_restore

# 5. Validate record counts
psql alfred_restore -c "
  SELECT 'users' as t, count(*) FROM users
  UNION SELECT 'transactions', count(*) FROM transactions
  UNION SELECT 'audit_log', count(*) FROM audit_log
  UNION SELECT 'api_keys', count(*) FROM api_keys;
"

# 6. Swap databases (maintenance window required)
# CRITICAL: Notify all stakeholders before proceeding
psql -c "ALTER DATABASE alfred RENAME TO alfred_broken;"
psql -c "ALTER DATABASE alfred_restore RENAME TO alfred;"

# 7. Run migrations to ensure schema is current
alembic -c src/backend/config/alembic.ini upgrade head

# 8. Restart all services
kubectl rollout restart deployment -n alfred
```

### 5.3. Audit Log Integrity Verification

```bash
# The audit log uses hash chains — verify integrity
python -c "
from app.logic import verify_audit_chain
result = verify_audit_chain()
print(f'Chain valid: {result.valid}')
print(f'Entries checked: {result.entries}')
if not result.valid:
    print(f'First broken link: {result.break_point}')
"
```

---

## 6. Procedure: Provider Failover Escalation (SEV-2)

### 6.1. Single Provider Down

The gateway automatically handles provider failover (< 500ms via circuit breaker). Manual intervention is needed only when:

- All providers for a region are down
- Circuit breaker is not recovering

```bash
# Check provider health status
curl -s https://alfred.internal/v1/providers/health | jq .

# Force circuit breaker reset for specific provider
curl -X POST https://alfred.internal/admin/providers/openai/circuit-breaker/reset \
  -H "Authorization: Bearer $ADMIN_KEY"

# Temporarily disable a provider
curl -X PATCH https://alfred.internal/admin/providers/openai \
  -H "Authorization: Bearer $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Check routing rules are redirecting properly
curl -s https://alfred.internal/v1/governance/routing-rules | jq '.[] | select(.enabled)'
```

### 6.2. Cache Recovery

```bash
# Check Redis/cache status
redis-cli -u $REDIS_URL INFO memory
redis-cli -u $REDIS_URL DBSIZE

# Flush semantic cache if corrupted (will temporarily reduce hit rate)
redis-cli -u $REDIS_URL KEYS "alfred:semantic:*" | head -20
redis-cli -u $REDIS_URL --scan --pattern "alfred:semantic:*" | xargs redis-cli -u $REDIS_URL DEL

# Cache will rebuild automatically — monitor hit rate
# Expected: 0% immediately, returning to 30%+ within ~2 hours under normal traffic
```

---

## 7. Procedure: Credential Compromise (SEV-1)

### 7.1. Immediate Response (0-5 minutes)

```bash
# 1. IMMEDIATELY rotate all Vault tokens
vault token revoke -self
vault login -method=approle role_id=$VAULT_ROLE_ID secret_id=$VAULT_SECRET_ID

# 2. Rotate all provider API keys
vault write alfred/rotate/openai force=true
vault write alfred/rotate/anthropic force=true
vault write alfred/rotate/google force=true

# 3. Invalidate all API key caches
curl -X POST https://alfred.internal/admin/cache/invalidate-keys \
  -H "Authorization: Bearer $EMERGENCY_KEY"

# 4. Check audit log for unauthorized access
psql $DATABASE_URL -c "
  SELECT timestamp, user_id, action, resource, ip_address
  FROM audit_log
  WHERE timestamp > now() - interval '24 hours'
    AND (action LIKE '%key%' OR action LIKE '%auth%' OR action LIKE '%admin%')
  ORDER BY timestamp DESC
  LIMIT 50;
"
```

### 7.2. User API Key Revocation

```bash
# If user API keys are compromised, revoke all and force regeneration
psql $DATABASE_URL -c "
  UPDATE api_keys SET revoked = true, revoked_at = now(), revoked_reason = 'security_incident'
  WHERE revoked = false;
"

# Notify all users via configured channels (Slack, email)
python -c "
from app.integrations import notify_all_users
notify_all_users(
    subject='[URGENT] API Key Rotation Required',
    message='All API keys have been revoked due to a security incident. Please generate a new key.'
)
"
```

---

## 8. Procedure: Data Corruption (SEV-1)

### 8.1. Ledger Transaction Corruption

```bash
# CRITICAL: This touches the ledger — requires Sergey Bar approval
# ROLLBACK: Restore from DB backup (Section 5.2)

# 1. Identify corrupted transactions
psql $DATABASE_URL -c "
  SELECT id, user_id, amount, type, created_at
  FROM transactions
  WHERE amount < 0 AND type = 'debit'
    AND created_at > now() - interval '1 hour'
  ORDER BY created_at DESC;
"

# 2. Halt all request processing
kubectl scale deployment/alfred-gateway --replicas=0 -n alfred

# 3. Apply corrective entries (NEVER delete — write compensating transactions)
# Each correction must reference the original transaction_id for idempotency
psql $DATABASE_URL -c "
  INSERT INTO transactions (user_id, amount, type, reference_id, note, created_at)
  SELECT user_id, ABS(amount), 'refund', id, 'Corrective entry - data corruption recovery', now()
  FROM transactions
  WHERE id IN ('txn-xxx', 'txn-yyy');  -- Replace with actual IDs
"

# 4. Resume processing
kubectl scale deployment/alfred-gateway --replicas=3 -n alfred
```

---

## 9. Communication Templates

### SEV-1 Initial Notification

```
INCIDENT: Alfred Platform - [Service/Component] Outage
SEVERITY: SEV-1
TIME: [UTC timestamp]
IMPACT: [Description of user/business impact]
STATUS: Investigating
NEXT UPDATE: [ETA, typically 15 min]
ON-CALL: [Name]
```

### SEV-1 Resolution

```
RESOLVED: Alfred Platform - [Service/Component] Outage
DURATION: [X minutes]
ROOT CAUSE: [Brief description]
REMEDIATION: [Actions taken]
FOLLOW-UP: Post-mortem scheduled for [date]
```

---

## 10. DR Drill Checklist

Perform semi-annually in staging environment:

- [ ] Simulate complete service outage → recover within RTO (30 min)
- [ ] Restore database from backup → verify RPO (5 min data loss)
- [ ] Provider failover test → verify < 500ms switchover
- [ ] Cache flush → verify rebuild and hit rate recovery
- [ ] API key rotation → verify zero-downtime rotation
- [ ] Audit log integrity check → verify hash chain
- [ ] Communication flow test → verify PagerDuty → Slack → Email chain
- [ ] Document any gaps found → create tickets

**Last Drill Date:** **\_\_\_\_**  
**Next Drill Date:** **\_\_\_\_**  
**Drill Lead:** **\_\_\_\_**

---

## 11. Post-Incident Process

1. **Stabilize** — Ensure all services are healthy and monitored
2. **Communicate** — Send resolution notice to stakeholders
3. **Post-mortem** — Schedule within 48 hours; use blameless format
4. **Remediate** — Create action items with owners and deadlines
5. **Update Runbook** — Incorporate lessons learned into this document
6. **Verify** — Run full test suite to confirm system integrity:
   ```bash
   pytest qa/Backend/ -v
   npm run test:unit
   npm run test:e2e
   ```

---

_Alfred — Disaster Recovery Runbook v1.0_  
_Confidential — Operations Critical_  
_Maintained by: Sergey Bar + SRE Team_
