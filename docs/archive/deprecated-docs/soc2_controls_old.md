# SOC 2 Type II Controls — Alfred Platform

> **Classification:** Internal — Compliance Engineering  
> **Owner:** Sergey Bar  
> **Review Cycle:** Quarterly  
> **Last Updated:** 2026-02-18

---

## 1. Overview

This document maps Alfred's technical and organizational controls to the **SOC 2 Trust Service Criteria (TSC)** — Security, Availability, Processing Integrity, Confidentiality, and Privacy. Each control includes:

- Criteria reference (CC/A/PI/C/P)
- Control description
- Implementation status
- Evidence artifacts

---

## 2. Security (Common Criteria — CC)

### CC1 — Control Environment

| Control ID | Description                                                 | Status         | Evidence                                            |
| ---------- | ----------------------------------------------------------- | -------------- | --------------------------------------------------- |
| CC1.1      | CISO/Security Lead designated as information security owner | ✅ Implemented | `CODEOWNERS`, org chart                             |
| CC1.2      | Security policies documented and reviewed annually          | ✅ Implemented | `devops/compliance/`, `docs/RESPONSIBLE_AI_RISK.md` |
| CC1.3      | Mandatory security training for engineering team            | ⏳ In Progress | Training plan in `qa/TRAINING_ENABLEMENT_PLAN.md`   |

### CC2 — Communication & Information

| Control ID | Description                                     | Status         | Evidence                                                |
| ---------- | ----------------------------------------------- | -------------- | ------------------------------------------------------- |
| CC2.1      | Incident runbook available to on-call engineers | ✅ Implemented | `docs/operations/PLAYBOOK.md`                           |
| CC2.2      | Change management process documented            | ✅ Implemented | `.github/copilot-instructions.md` (Governance Protocol) |
| CC2.3      | System architecture documentation maintained    | ✅ Implemented | `README.md`, `docs/api_documentation.md`                |

### CC3 — Risk Assessment

| Control ID | Description                       | Status         | Evidence                                     |
| ---------- | --------------------------------- | -------------- | -------------------------------------------- |
| CC3.1      | Threat modeling for proxy gateway | ✅ Implemented | `devops/scripts/penetration_testing_plan.md` |
| CC3.2      | Responsible AI risk assessment    | ✅ Implemented | `docs/RESPONSIBLE_AI_RISK.md`                |
| CC3.3      | Dependency vulnerability scanning | ✅ Implemented | `tools/ci/`, GitHub Dependabot               |

### CC4 — Monitoring Activities

| Control ID | Description                                                 | Status         | Evidence                                                           |
| ---------- | ----------------------------------------------------------- | -------------- | ------------------------------------------------------------------ |
| CC4.1      | Immutable audit log for all credential and quota operations | ✅ Implemented | `src/backend/app/logic.py` — audit_log table (write-only)          |
| CC4.2      | Real-time alerting on anomalous spend patterns              | ✅ Implemented | Circuit breaker in `services/gateway/security/security.go`         |
| CC4.3      | Dashboard monitoring for system health                      | ✅ Implemented | `src/frontend/src/pages/DashboardNew.jsx`, `tools/check_health.py` |
| CC4.4      | Request-level logging with PII redaction                    | ✅ Implemented | `src/backend/app/safety/` PII detection middleware                 |

### CC5 — Control Activities

| Control ID | Description                                            | Status         | Evidence                                                    |
| ---------- | ------------------------------------------------------ | -------------- | ----------------------------------------------------------- |
| CC5.1      | API key authentication on all endpoints                | ✅ Implemented | `src/backend/app/routers/users.py` — key validation         |
| CC5.2      | Role-based access control (RBAC)                       | ✅ Implemented | `src/frontend/src/pages/RBACAdmin.jsx`, backend role checks |
| CC5.3      | Pre-request credit deduction (not post-request)        | ✅ Implemented | `src/backend/app/logic.py` — debit-before-forward pattern   |
| CC5.4      | Hard/Soft limit enforcement before provider forwarding | ✅ Implemented | Wallet limit logic in `logic.py`, `WalletManagement.jsx`    |

### CC6 — Logical & Physical Access Controls

| Control ID | Description                                        | Status         | Evidence                                                  |
| ---------- | -------------------------------------------------- | -------------- | --------------------------------------------------------- |
| CC6.1      | Provider API keys stored in HashiCorp Vault        | ✅ Implemented | `services/gateway/security/security.go` — `VaultClient`   |
| CC6.2      | mTLS between internal services                     | ✅ Implemented | `services/gateway/security/security.go` — `MTLSConfig`    |
| CC6.3      | API key rotation with zero-downtime                | ✅ Implemented | `RotateProviderKey()` with cache invalidation             |
| CC6.4      | SSO/SAML integration for enterprise authentication | ✅ Implemented | `src/frontend/src/pages/SSOConfig.jsx`, SCIM provisioning |
| CC6.5      | Secret scanning in pre-commit hooks                | ✅ Implemented | `devops/scripts/secret_rotation_plan.md`                  |

### CC7 — System Operations

| Control ID | Description                                   | Status         | Evidence                                     |
| ---------- | --------------------------------------------- | -------------- | -------------------------------------------- |
| CC7.1      | CI/CD pipeline with lint, test, build gates   | ✅ Implemented | `.github/workflows/ci.yml`                   |
| CC7.2      | Database migrations managed via Alembic       | ✅ Implemented | `src/backend/alembic/`                       |
| CC7.3      | Container-based deployment with health checks | ✅ Implemented | `Dockerfile`, `docker-compose.yml`           |
| CC7.4      | Penetration test plan and execution schedule  | ✅ Implemented | `devops/scripts/penetration_testing_plan.md` |

### CC8 — Change Management

| Control ID | Description                                         | Status         | Evidence                                                |
| ---------- | --------------------------------------------------- | -------------- | ------------------------------------------------------- |
| CC8.1      | Sole merge authority (Sergey Bar) for main branch   | ✅ Implemented | `.github/copilot-instructions.md` — Governance Protocol |
| CC8.3      | Code review required for all L3/L4 changes          | ✅ Implemented | `reviews/` directory, PR templates                      |
| CC8.4      | Rollback procedures documented for critical changes | ✅ Implemented | Rollback comment blocks in L3/L4 code                   |

### CC9 — Risk Mitigation

| Control ID | Description                                  | Status         | Evidence                                                  |
| ---------- | -------------------------------------------- | -------------- | --------------------------------------------------------- |
| CC9.1      | Provider failover with < 500ms SLA           | ✅ Implemented | `services/gateway/routing/` — circuit breaker + failover  |
| CC9.2      | Semantic cache to reduce provider dependency | ✅ Implemented | `services/gateway/caching/` — 30%+ target hit rate        |
| CC9.3      | BYOK encryption for tenant data isolation    | ✅ Implemented | `services/gateway/security/security.go` — `BYOKEncryptor` |

---

## 3. Availability (A)

| Control ID | Description                          | Status         | Evidence                                          |
| ---------- | ------------------------------------ | -------------- | ------------------------------------------------- |
| A1.1       | P95 gateway latency < 150ms overhead | ✅ Target Set  | Performance tests in `qa/Backend/Performance/`    |
| A1.2       | Multi-region deployment support      | ✅ Implemented | `devops/scripts/setup_sharding_multi_region.sh`   |
| A1.3       | Auto-scaling configuration           | ✅ Implemented | `devops/scripts/setup_autoscaling.sh`, Helm chart |
| A1.4       | Health check endpoints               | ✅ Implemented | `tools/check_health.py`, `/health` endpoint       |
| A1.5       | Disaster Recovery runbook            | ✅ Implemented | `docs/operations/disaster_recovery_runbook.md`    |

---

## 4. Processing Integrity (PI)

| Control ID | Description                                        | Status         | Evidence                                                 |
| ---------- | -------------------------------------------------- | -------------- | -------------------------------------------------------- |
| PI1.1      | Credit transactions are atomic (no partial writes) | ✅ Implemented | `logic.py` — `async with db.begin()` pattern             |
| PI1.2      | Idempotent refund processing                       | ✅ Implemented | Transaction ID deduplication in ledger                   |
| PI1.3      | Hash-chained immutable audit log                   | ✅ Implemented | `logic.py` — audit entries with cryptographic hash chain |
| PI1.4      | Input validation on all API endpoints              | ✅ Implemented | Pydantic v2 `model_config = ConfigDict(strict=True)`     |
| PI1.5      | Token counting accuracy (pre/post comparison)      | ✅ Implemented | Metering system in `services/gateway/metering/`          |

---

## 5. Confidentiality (C)

| Control ID | Description                                    | Status         | Evidence                                    |
| ---------- | ---------------------------------------------- | -------------- | ------------------------------------------- |
| C1.1       | PII detection and redaction in prompt logging  | ✅ Implemented | `src/backend/app/safety/` — NER detector    |
| C1.2       | Prompt injection detection                     | ✅ Implemented | Safety pipeline middleware                  |
| C1.3       | Secret scanning in prompts                     | ✅ Implemented | Safety pipeline — regex + entropy detection |
| C1.4       | Data residency routing enforcement             | ✅ Implemented | `ResidencyEnforcer` in security.go          |
| C1.5       | Customer data encryption at rest (AES-256-GCM) | ✅ Implemented | `BYOKEncryptor` with AES-256-GCM            |

---

## 6. Privacy (P)

| Control ID | Description                                  | Status          | Evidence                                                        |
| ---------- | -------------------------------------------- | --------------- | --------------------------------------------------------------- |
| P1.1       | GDPR-aligned data deletion capability        | ⏳ Design Phase | Backend deletion endpoint planned                               |
| P1.2       | Data processing records maintained           | ✅ Implemented  | Audit log captures all data operations                          |
| P1.3       | Consent management for prompt data retention | ⏳ Design Phase | Requires org-level settings                                     |
| P1.4       | Data export (right to portability)           | ✅ Implemented  | `src/frontend/src/pages/FinOpsExports.jsx`, Import/Export admin |

---

## 7. Evidence Collection Schedule

| Activity                | Frequency   | Owner            | Method                                     |
| ----------------------- | ----------- | ---------------- | ------------------------------------------ |
| Audit log review        | Monthly     | Security Lead    | Query `audit_log` table for anomalies      |
| Access review           | Quarterly   | Engineering Lead | Review RBAC assignments, API key inventory |
| Vulnerability scan      | Weekly      | CI/CD            | Automated via Dependabot + secret scanning |
| Penetration test        | Annual      | External Auditor | Per `penetration_testing_plan.md`          |
| Disaster recovery drill | Semi-annual | SRE              | Execute DR runbook in staging              |
| Policy review           | Annual      | Sergey Bar       | Review all docs in `devops/compliance/`    |

---

## 8. Gap Summary

| Gap                              | Priority | Remediation                                         | Target Date |
| -------------------------------- | -------- | --------------------------------------------------- | ----------- |
| GDPR deletion endpoint           | P1       | Implement `/admin/gdpr/delete` with cascading purge | Q2 2026     |
| Consent management UI            | P2       | Org-level data retention settings in Settings page  | Q2 2026     |
| Formal security training program | P2       | Complete training enablement plan execution         | Q2 2026     |
| External SOC 2 audit engagement  | P1       | Engage auditor for Type II examination period       | Q3 2026     |

---

_Alfred — SOC 2 Controls Mapping v1.0_  
_Confidential — Internal Engineering Use Only_
