# Alfred Disaster Recovery Runbook

[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model: Claude Opus 4.6
Tier: L2
Logic: Comprehensive disaster recovery procedures.
Root Cause: Sprint task T198 — DR runbook documentation.
Context: Enables rapid recovery from various failure scenarios.
Suitability: L2 — Standard operations documentation.
──────────────────────────────────────────────────────────────

## 1. Overview

### 1.1 Purpose

This runbook provides step-by-step procedures for recovering the Alfred platform from various disaster scenarios. It is designed to minimize downtime and data loss while ensuring service continuity.

### 1.2 Recovery Objectives

| Metric                             | Target  | Tier 1 (Critical) | Tier 2 (Standard) |
| ---------------------------------- | ------- | ----------------- | ----------------- |
| **RTO** (Recovery Time Objective)  | 4 hours | 1 hour            | 4 hours           |
| **RPO** (Recovery Point Objective) | 1 hour  | 15 minutes        | 1 hour            |
| **MTTR** (Mean Time to Recovery)   | 2 hours | 30 minutes        | 2 hours           |

### 1.3 Service Tiers

| Tier   | Services                            | Priority                  |
| ------ | ----------------------------------- | ------------------------- |
| Tier 1 | Gateway, Ledger, Authentication     | Critical — Restore First  |
| Tier 2 | Dashboard, Analytics, Notifications | Standard — Restore Second |
| Tier 3 | Reports, Non-essential APIs         | Deferrable                |

## 2. Contact List

### 2.1 Internal Contacts

| Role                | Name             | Phone           | Email            |
| ------------------- | ---------------- | --------------- | ---------------- |
| Incident Commander  | On-call rotation | PagerDuty       | oncall@alfred.ai |
| Security Lead       | Sergey Bar       | +1-xxx-xxx-xxxx | sergey@alfred.ai |
| Infrastructure Lead | TBD              | +1-xxx-xxx-xxxx | infra@alfred.ai  |
| VP Engineering      | TBD              | +1-xxx-xxx-xxxx | vpeng@alfred.ai  |

### 2.2 External Contacts

| Service     | Contact            | Phone | Account ID       |
| ----------- | ------------------ | ----- | ---------------- |
| AWS Support | Enterprise Support | -     | xxxx-xxxx-xxxx   |
| GCP Support | Premium Support    | -     | alfred-prod-xxxx |
| Cloudflare  | Status Page        | -     | alfred-xxxx      |
| PagerDuty   | -                  | -     | alfred           |

### 2.3 Escalation Path

```
Level 1: On-call Engineer (0-15 min)
    ↓
Level 2: Infrastructure Lead (15-30 min)
    ↓
Level 3: Security Lead + VP Engineering (30-60 min)
    ↓
Level 4: Executive Team (60+ min)
```

## 3. Disaster Scenarios

### 3.1 Scenario Matrix

| Scenario                   | Probability | Impact   | Recovery Time | Section |
| -------------------------- | ----------- | -------- | ------------- | ------- |
| Single zone failure        | Medium      | Low      | Auto-recovery | 4.1     |
| Region failure             | Low         | High     | 1-2 hours     | 4.2     |
| Database corruption        | Very Low    | Critical | 2-4 hours     | 4.3     |
| Ransomware/Security breach | Very Low    | Critical | 4-8 hours     | 4.4     |
| Cloud provider outage      | Very Low    | Critical | 2-4 hours     | 4.5     |
| DDoS attack                | Medium      | Medium   | 30 min        | 4.6     |
| Certificate expiry         | Low         | High     | 15 min        | 4.7     |
| Secret rotation failure    | Low         | Medium   | 30 min        | 4.8     |

## 4. Recovery Procedures

### 4.1 Single Zone Failure

**Trigger:** Health checks fail in one availability zone.

**Automatic Recovery:**

1. Load balancer removes unhealthy instances
2. Auto-scaling launches replacements in healthy zones
3. Traffic redistributes automatically

**Manual Verification:**

```bash
# Check instance health
kubectl get pods -n alfred -o wide

# Check load balancer targets
aws elbv2 describe-target-health --target-group-arn <arn>

# Verify traffic distribution
kubectl top pods -n alfred
```

**No action required unless automatic recovery fails.**

### 4.2 Region Failure

**Trigger:** Entire cloud region becomes unavailable.

**Prerequisites:**

- Multi-region deployment enabled
- DNS failover configured
- Cross-region database replication active

**Recovery Steps:**

1. **Declare Incident** (5 min)

   ```
   - Page incident commander
   - Create incident channel #incident-YYYYMMDD-region
   - Update status page: "Investigating"
   ```

2. **Activate Failover Region** (15 min)

   ```bash
   # Verify secondary region health
   kubectl --context=dr-region get pods -n alfred

   # Promote read replica to primary
   aws rds promote-read-replica --db-instance-identifier alfred-dr-replica

   # Update application configuration
   kubectl --context=dr-region set env deployment/alfred-backend \
     DATABASE_URL=$DR_DATABASE_URL
   ```

3. **Update DNS** (5 min)

   ```bash
   # Failover to DR region (Route53)
   aws route53 change-resource-record-sets \
     --hosted-zone-id <zone> \
     --change-batch file://dr-failover.json

   # Or use Cloudflare
   curl -X PATCH "https://api.cloudflare.com/client/v4/zones/<zone>/dns_records/<id>" \
     -H "Authorization: Bearer $CF_TOKEN" \
     -d '{"content": "<dr-region-ip>"}'
   ```

4. **Verify Services** (15 min)

   ```bash
   # Test authentication
   curl https://api.alfred.ai/health

   # Test critical paths
   ./scripts/smoke_test.sh --env=production
   ```

5. **Update Status Page** (2 min)
   ```
   Status: "Operating in disaster recovery mode"
   ```

### 4.3 Database Corruption

**Trigger:** Data integrity errors, application errors indicating bad data.

**Recovery Steps:**

1. **Isolate the Issue** (5 min)

   ```bash
   # Check for active writes
   psql -h $DB_HOST -c "SELECT * FROM pg_stat_activity WHERE state='active';"

   # If needed, stop application writes
   kubectl scale deployment alfred-backend --replicas=0
   ```

2. **Assess Corruption** (15 min)

   ```sql
   -- Check for corruption
   SELECT pg_stat_user_tables.relname, n_dead_tup, n_live_tup
   FROM pg_stat_user_tables;

   -- Verify audit log integrity
   SELECT id, prev_hash,
          encode(sha256(concat(prev_hash, user_id::text, action, timestamp::text)::bytea), 'hex') as calculated_hash,
          hash
   FROM audit_log
   WHERE hash != encode(sha256(concat(prev_hash, user_id::text, action, timestamp::text)::bytea), 'hex')
   LIMIT 10;
   ```

3. **Point-in-Time Recovery** (1-2 hours)

   ```bash
   # List available snapshots
   aws rds describe-db-snapshots --db-instance-identifier alfred-prod

   # Or list point-in-time recovery window
   aws rds describe-db-instances --db-instance-identifier alfred-prod \
     --query 'DBInstances[0].LatestRestorableTime'

   # Restore to new instance
   aws rds restore-db-instance-to-point-in-time \
     --source-db-instance-identifier alfred-prod \
     --target-db-instance-identifier alfred-prod-recovered \
     --restore-time 2024-01-15T14:30:00Z

   # Wait for restoration
   aws rds wait db-instance-available \
     --db-instance-identifier alfred-prod-recovered
   ```

4. **Validate Data** (30 min)

   ```bash
   # Run data validation scripts
   python tools/validate_db.py --connection=$RECOVERED_DB_URL

   # Verify wallet balances
   psql -h $RECOVERED_DB -c "SELECT SUM(balance) FROM wallets;"
   ```

5. **Cutover** (15 min)

   ```bash
   # Update application to use recovered database
   kubectl set env deployment/alfred-backend \
     DATABASE_URL=$RECOVERED_DB_URL

   # Restart application
   kubectl rollout restart deployment/alfred-backend
   ```

### 4.4 Security Breach / Ransomware

**Trigger:** Security alert, suspicious activity, ransom demand.

**CRITICAL: Do not pay ransom. Do not negotiate.**

**Recovery Steps:**

1. **Contain Immediately** (5 min)

   ```bash
   # ISOLATE: Block all external access
   kubectl apply -f k8s/emergency-network-policy.yaml

   # Revoke all API keys
   psql -c "UPDATE api_keys SET is_active = false, revoked_at = NOW();"

   # Rotate JWT secret
   kubectl create secret generic jwt-secret --from-literal=secret=$(openssl rand -hex 32) --dry-run=client -o yaml | kubectl apply -f -
   ```

2. **Preserve Evidence** (15 min)

   ```bash
   # Snapshot all volumes
   aws ec2 create-snapshots --instance-specification InstanceId=<id>,ExcludeBootVolume=false

   # Export logs
   aws logs create-export-task --log-group-name alfred-prod \
     --destination-bucket security-incident-logs \
     --from $(date -d '24 hours ago' +%s)000 --to $(date +%s)000

   # Do NOT modify running instances — forensic analysis needed
   ```

3. **Contact Security Lead** (Immediate)

   ```
   - Call Sergey Bar directly
   - Do not discuss over Slack/email (may be compromised)
   - Prepare for law enforcement involvement
   ```

4. **Clean Environment Deployment** (2-4 hours)

   ```bash
   # Deploy from verified clean infrastructure
   terraform apply -var-file=clean-deployment.tfvars

   # Restore from pre-breach backup
   # (Identify breach timestamp first via security analysis)

   # Regenerate ALL credentials
   ./scripts/rotate_all_secrets.sh
   ```

5. **Post-Incident**
   - Full security audit
   - Customer notification (if required by law)
   - Incident report and postmortem

### 4.5 Cloud Provider Outage

**Trigger:** Cloud provider status page shows outage.

**If Multi-Cloud:**

```bash
# Failover to secondary cloud
./scripts/failover_cloud_provider.sh --target=gcp
```

**If Single-Cloud:**

```
1. Monitor provider status page
2. Communicate with customers via status page
3. No action possible until provider recovers
4. Consider temporary read-only mode if partial service available
```

### 4.6 DDoS Attack

**Trigger:** Traffic spike, service degradation, Cloudflare alerts.

**Recovery Steps:**

1. **Activate DDoS Protection** (5 min)

   ```bash
   # Enable Cloudflare "Under Attack" mode
   curl -X PATCH "https://api.cloudflare.com/client/v4/zones/<zone>/settings/security_level" \
     -H "Authorization: Bearer $CF_TOKEN" \
     -d '{"value":"under_attack"}'

   # Enable rate limiting rules
   kubectl apply -f k8s/rate-limit-strict.yaml
   ```

2. **Block Attack Sources** (10 min)

   ```bash
   # Analyze traffic patterns
   kubectl logs -l app=gateway --tail=10000 | grep -E "client_ip" | sort | uniq -c | sort -rn | head -50

   # Block via WAF rules
   # Add IP ranges to Cloudflare block list
   ```

3. **Scale Capacity** (10 min)

   ```bash
   # Increase replica count
   kubectl scale deployment alfred-gateway --replicas=20

   # Scale database connections
   # Temporarily increase connection pool
   ```

4. **Restore Normal Mode** (After attack subsides)
   ```bash
   # Disable "Under Attack" mode
   curl -X PATCH "https://api.cloudflare.com/client/v4/zones/<zone>/settings/security_level" \
     -H "Authorization: Bearer $CF_TOKEN" \
     -d '{"value":"high"}'
   ```

### 4.7 Certificate Expiry

**Trigger:** SSL errors, cert-manager alerts.

**Recovery Steps:**

1. **Check Certificate Status** (2 min)

   ```bash
   # Check expiry
   echo | openssl s_client -servername api.alfred.ai -connect api.alfred.ai:443 2>/dev/null | openssl x509 -noout -dates

   # Check cert-manager
   kubectl get certificates -n alfred
   kubectl describe certificate alfred-tls -n alfred
   ```

2. **Force Renewal** (5 min)

   ```bash
   # Delete existing certificate to trigger renewal
   kubectl delete certificate alfred-tls -n alfred

   # Or manually trigger
   kubectl cert-manager renew alfred-tls -n alfred

   # Wait for issuance
   kubectl wait --for=condition=Ready certificate/alfred-tls -n alfred --timeout=300s
   ```

3. **Manual Certificate** (If automated fails)

   ```bash
   # Generate via Let's Encrypt CLI
   certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
     -d api.alfred.ai -d app.alfred.ai

   # Import to Kubernetes
   kubectl create secret tls alfred-tls \
     --cert=/etc/letsencrypt/live/api.alfred.ai/fullchain.pem \
     --key=/etc/letsencrypt/live/api.alfred.ai/privkey.pem \
     --dry-run=client -o yaml | kubectl apply -f -
   ```

### 4.8 Secret Rotation Failure

**Trigger:** Vault errors, authentication failures after rotation.

**Recovery Steps:**

1. **Identify Affected Secret** (5 min)

   ```bash
   # Check Vault status
   vault status

   # List recent secret versions
   vault kv metadata get secret/alfred/prod/database
   ```

2. **Rollback to Previous Version** (5 min)

   ```bash
   # Get previous version
   vault kv get -version=2 secret/alfred/prod/database

   # Rollback
   vault kv rollback -version=2 secret/alfred/prod/database
   ```

3. **Resync Applications** (5 min)
   ```bash
   # Restart pods to pick up new secrets
   kubectl rollout restart deployment alfred-backend
   kubectl rollout restart deployment alfred-gateway
   ```

## 5. Communication Templates

### 5.1 Internal Incident Notification

```
INCIDENT DECLARED: [Severity Level]

Time: YYYY-MM-DD HH:MM UTC
Impact: [Description]
Incident Commander: [Name]
Channel: #incident-YYYYMMDD-[name]

Current Status: Investigating
ETA for Update: [Time]
```

### 5.2 Customer Status Page Update

```
[Service Disruption] - Investigating

We are currently investigating reports of [issue description].

Impact: [Affected services]
Status: Investigating

We will provide an update within 30 minutes.
```

### 5.3 Resolution Notification

```
[Resolved] - [Issue Description]

The issue affecting [services] has been resolved.

Duration: [Start time] - [End time] (X hours Y minutes)
Root Cause: [Brief description]
Resolution: [Action taken]

We apologize for any inconvenience. A detailed postmortem will be shared within 48 hours.
```

## 6. Testing Schedule

| Test Type          | Frequency | Last Tested | Next Test  |
| ------------------ | --------- | ----------- | ---------- |
| Failover drill     | Quarterly | YYYY-MM-DD  | YYYY-MM-DD |
| Backup restoration | Monthly   | YYYY-MM-DD  | YYYY-MM-DD |
| Full DR exercise   | Annually  | YYYY-MM-DD  | YYYY-MM-DD |
| Tabletop exercise  | Quarterly | YYYY-MM-DD  | YYYY-MM-DD |

## 7. Appendix

### A. Emergency Network Policy

```yaml
# k8s/emergency-network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: emergency-lockdown
  namespace: alfred
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress: [] # Block all ingress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
```

### B. DR Failover DNS

```json
// dr-failover.json
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.alfred.ai",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "<dr-region-zone>",
          "DNSName": "<dr-region-lb>",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}
```

### C. Runbook Changelog

| Date       | Version | Author              | Changes         |
| ---------- | ------- | ------------------- | --------------- |
| 2024-01-XX | 1.0     | Infrastructure Team | Initial runbook |

---

**Classification:** Internal — Operations Team
**Review Frequency:** Quarterly
**Owner:** Infrastructure Lead
