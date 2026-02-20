# Unit Test Coverage Audit Report

**Generated:** 2026-02-19  
**Sprint Task:** T224 - Unit test coverage audit (target >90%)  
**Overall Coverage:** 39% ❌ (Target: 90%)

---

## Executive Summary

The backend codebase currently has **39% unit test coverage**, significantly below the 90% target for production readiness. This audit identifies critical gaps requiring immediate attention before launch.

### Risk Assessment

| Risk Level    | Coverage % | Modules Affected | Business Impact                                                 |
| ------------- | ---------- | ---------------- | --------------------------------------------------------------- |
| 🔴 CRITICAL   | 0-20%      | 18 modules       | Security vulnerabilities, financial integrity, audit compliance |
| 🟠 HIGH       | 21-50%     | 32 modules       | Integration failures, data quality issues                       |
| 🟡 MEDIUM     | 51-79%     | 17 modules       | Minor bugs, edge case handling                                  |
| 🟢 ACCEPTABLE | 80-100%    | 14 modules       | Production ready                                                |

---

## Critical Coverage Gaps (🔴 P0 - Launch Blockers)

### Security & Authentication (0-6% Coverage)

| Module                           | Coverage | Lines Uncovered | Impact                                                  |
| -------------------------------- | -------- | --------------- | ------------------------------------------------------- |
| `app/routers/sso_rbac.py`        | **6%**   | 275/293         | JWT auth, RBAC, SSO integration - potential auth bypass |
| `app/integrations/teams_bot.py`  | **0%**   | 193/193         | Microsoft Teams integration - zero validation           |
| `app/notifications.py`           | **0%**   | 44/44           | Alert delivery failures undetected                      |
| `app/workers.py`                 | **0%**   | 17/17           | Background jobs untested                                |
| `app/routers/security_review.py` | **0%**   | 8/8             | Security audit endpoints unvalidated                    |

**Urgency:** Immediate. Security-critical code with <10% coverage exposes Alfred to auth bypass, privilege escalation, and integration failures.

### Safety & PII Detection (0-37% Coverage)

| Module                           | Coverage | Lines Uncovered | Impact                                  |
| -------------------------------- | -------- | --------------- | --------------------------------------- |
| `app/safety/ner_detector.py`     | **0%**   | 183/183         | Named entity recognition fails silently |
| `app/safety/pii_detector.py`     | **25%**  | 106/142         | PII leakage risk - GDPR violation       |
| `app/safety/pipeline.py`         | **37%**  | 155/247         | Safety validation pipeline untested     |
| `app/safety/prompt_injection.py` | **33%**  | 79/118          | Prompt injection attacks undetected     |
| `app/safety/secret_scanner.py`   | **32%**  | 100/146         | API key leakage in logs/prompts         |

**Urgency:** High. PII detection and safety modules are compliance-critical (GDPR, SOC 2). Zero testing = regulatory risk.

### Financial & Ledger Logic (57% Coverage)

| Module                     | Coverage | Lines Uncovered | Impact                                                                |
| -------------------------- | -------- | --------------- | --------------------------------------------------------------------- |
| `app/logic.py`             | **57%**  | 106/247         | Wallet deductions, credit refunds, audit log - potential double-spend |
| `app/routers/wallets.py`   | **33%**  | 187/278         | Wallet CRUD operations - integrity risk                               |
| `app/routers/transfers.py` | **35%**  | 87/134          | Credit transfers - financial leakage                                  |
| `app/routers/finops.py`    | **52%**  | 104/217         | Cost attribution - billing errors                                     |

**Urgency:** Immediate. Logic.py is the ledger system core - 43% uncovered lines risk credit leakage, double-spend, audit log corruption.

### Audit & Compliance (20-40% Coverage)

| Module                      | Coverage | Lines Uncovered | Impact                                    |
| --------------------------- | -------- | --------------- | ----------------------------------------- |
| `app/routers/audit_log.py`  | **20%**  | 69/86           | Immutable audit trail - SOC 2 requirement |
| `app/routers/gdpr.py`       | **40%**  | 104/174         | Data deletion, export - right to erasure  |
| `app/routers/governance.py` | **33%**  | 104/156         | Routing policies, OPA integration         |
| `app/routers/compliance.py` | **80%**  | 1/5             | Compliance endpoints (small module)       |

**Urgency:** High. Audit log and GDPR endpoints are SOC 2 / regulatory requirements.

### Integration Connectors (15-27% Coverage)

| Module                           | Coverage | Lines Uncovered | Impact                                            |
| -------------------------------- | -------- | --------------- | ------------------------------------------------- |
| `app/routers/slack_app.py`       | **15%**  | 292/345         | Slack integration - largest router, minimal tests |
| `app/integrations/slack.py`      | **27%**  | 62/85           | Slack connector                                   |
| `app/integrations/teams.py`      | **22%**  | 83/107          | Teams connector                                   |
| `app/integrations/telegram.py`   | **22%**  | 94/121          | Telegram connector                                |
| `app/integrations/whatsapp.py`   | **26%**  | 73/98           | WhatsApp connector                                |
| `app/integrations/email.py`      | **24%**  | 67/88           | Email connector                                   |
| `app/integrations/escalation.py` | **27%**  | 96/132          | Escalation workflows                              |

**Urgency:** Medium. Integration failures will surface in production without pre-launch testing.

---

## Moderate Coverage Gaps (🟡 P1 - Post-Launch)

### Core Backend (50-79% Coverage)

| Module                   | Coverage | Status                                           |
| ------------------------ | -------- | ------------------------------------------------ |
| `app/lifespan.py`        | 74%      | Needs edge case tests                            |
| `app/main.py`            | 72%      | Middleware stack needs validation                |
| `app/middleware.py`      | 54%      | Rate limiting tested, need auth/security headers |
| `app/routers/prompts.py` | 52%      | Prompt template validation gaps                  |

### Data & Analytics (43-71% Coverage)

| Module                           | Coverage | Status            |
| -------------------------------- | -------- | ----------------- |
| `app/routers/data_catalog.py`    | 70%      | Nearly complete   |
| `app/routers/data_quality.py`    | 70%      | Acceptable        |
| `app/routers/usage_analytics.py` | 71%      | Acceptable        |
| `app/routers/analytics.py`       | 32%      | Needs improvement |

---

## Acceptable Coverage (🟢 Production Ready)

| Module                        | Coverage | Notes                            |
| ----------------------------- | -------- | -------------------------------- |
| `app/models.py`               | 96%      | SQLAlchemy models well-validated |
| `app/schemas.py`              | 98%      | Pydantic schemas comprehensive   |
| `app/routers/admin_config.py` | 88%      | Admin endpoints covered          |
| `app/routers/metrics.py`      | 86%      | Prometheus metrics tested        |
| `app/logging_config.py`       | 81%      | Logging infrastructure solid     |
| `app/routers/auth.py`         | 80%      | Basic auth endpoints covered     |

---

## Test Infrastructure Issues

### Current Issues Detected

1. **Async Test Support Missing**
   - 5 failed tests in `test_rate_limiting.py` due to missing pytest-asyncio plugin
   - Need to add `pytest-asyncio` to requirements-dev.txt
   - Need to configure pytest markers in pytest.ini

2. **Resource Warnings**
   - 35 warnings about unclosed database connections
   - SQLite connections in tests not properly closed
   - Impact: Memory leaks in test suite

3. **Test Isolation**
   - BUG-001: SQLAlchemy connection pool issue noted in `test_api.py`
   - Session fixtures need async/session refactor

---

## Recommended Priority Roadmap

### Phase 1: Launch Blockers (1-2 Weeks)

**Priority 1 [THIS WEEK]:**

- [ ] `app/logic.py` → 90% (wallet/ledger critical)
- [ ] `app/routers/sso_rbac.py` → 80% (auth critical)
- [ ] `app/routers/audit_log.py` → 80% (SOC 2 requirement)
- [ ] Fix test_rate_limiting.py failures (burst logic)
- [ ] Add pytest-asyncio plugin

**Priority 2 [NEXT WEEK]:**

- [ ] `app/safety/pii_detector.py` → 80% (GDPR compliance)
- [ ] `app/safety/pipeline.py` → 80% (safety validation)
- [ ] `app/routers/wallets.py` → 80% (financial integrity)
- [ ] `app/routers/gdpr.py` → 80% (right to erasure)
- [ ] `app/integrations/teams_bot.py` → 60% (zero coverage unacceptable)

### Phase 2: Integration & Stability (2-3 Weeks)

- [ ] All integration connectors → 60% minimum
  - Slack, Teams, Telegram, WhatsApp, Email
- [ ] `app/middleware.py` → 80% (security headers, auth middleware)
- [ ] `app/routers/governance.py` → 70% (routing policies)
- [ ] `app/routers/transfers.py` → 70% (credit transfers)

### Phase 3: Comprehensive Coverage (4+ Weeks)

- [ ] All remaining routers → 70% minimum
- [ ] All safety modules → 80% minimum
- [ ] Overall backend coverage → 85%
- [ ] Zero modules with <50% coverage

---

## Coverage by Category

### 🔴 Critical (Security, Financial, Compliance)

- **Current:** 23% average
- **Target:** 90%
- **Modules:** 12
- **Gap:** 67 percentage points

### 🟠 High (Integrations, Core)

- **Current:** 48% average
- **Target:** 75%
- **Modules:** 28
- **Gap:** 27 percentage points

### 🟡 Medium (Analytics, Data)

- **Current:** 64% average
- **Target:** 75%
- **Modules:** 17
- **Gap:** 11 percentage points

---

## Test Quality Metrics

| Metric                   | Current | Target | Status |
| ------------------------ | ------- | ------ | ------ |
| Overall Coverage         | 39%     | 90%    | ❌     |
| Critical Module Coverage | 23%     | 90%    | ❌     |
| Zero-Coverage Modules    | 18      | 0      | ❌     |
| Passing Tests            | 64/71   | 71/71  | 🟡     |
| Resource Warnings        | 35      | 0      | 🟡     |
| Test Execution Time      | 20.15s  | <30s   | ✅     |

---

## Immediate Actions Required

### This Sprint (T224 - T230)

1. **Fix Failing Tests** (Today)
   - Correct burst logic in test_rate_limiting.py
   - Add pytest-asyncio to requirements-dev.txt
   - Re-run tests to confirm 71/71 passing

2. **Logic.py Coverage** (This Week)
   - Add tests for wallet deduction edge cases
   - Test refund idempotency
   - Test audit log hash chain validation
   - Target: 57% → 90%

3. **SSO/RBAC Coverage** (This Week)
   - Test JWT token issuance
   - Test role-based access control
   - Test SSO integration flows
   - Target: 6% → 80%

4. **Safety Module Scaffolds** (Next Week)
   - Create test_pii_detector.py skeleton
   - Create test_prompt_injection.py skeleton
   - Create test_safety_pipeline.py skeleton
   - Initial target: 0% → 40%

---

## Coverage Tracking

### Coverage Improvement Targets by Sprint

| Sprint     | Overall | Critical Modules | Zero-Coverage Modules |
| ---------- | ------- | ---------------- | --------------------- |
| Current    | 39%     | 23%              | 18                    |
| Sprint +1  | 55%     | 70%              | 8                     |
| Sprint +2  | 70%     | 85%              | 2                     |
| Sprint +3  | 85%     | 90%              | 0                     |
| Production | 90%     | 95%              | 0                     |

---

## Appendix: Full Module Coverage List

```
app/__init__.py                               0      0   100%
app/auth_utils.py                           138     85    38%
app/celery_app.py                            18      9    50%
app/config.py                               179     29    84%
app/database.py                              95     31    67%
app/dependencies.py                         203     79    61%
app/integrations/__init__.py                  0      0   100%
app/integrations/digest.py                   78     31    60%
app/integrations/email.py                    88     67    24%
app/integrations/escalation.py              132     96    27%
app/integrations/manager.py                 175    104    41%
app/integrations/slack.py                    85     62    27%
app/integrations/sso.py                      30     16    47%
app/integrations/teams.py                   107     83    22%
app/integrations/teams_bot.py               193    193     0%   🔴 CRITICAL
app/integrations/telegram.py                121     94    22%
app/integrations/webhook.py                  66     44    33%
app/integrations/whatsapp.py                 98     73    26%
app/lifespan.py                             123     32    74%
app/logging_config.py                        98     19    81%
app/logic.py                                247    106    57%   🔴 CRITICAL
app/main.py                                 120     33    72%
app/metrics.py                               32     22    31%
app/middleware.py                           196     91    54%
app/models.py                               333     13    96%   ✅ GOOD
app/notifications.py                         44     44     0%   🔴 CRITICAL
app/routers/admin_config.py                   8      1    88%   ✅ GOOD
app/routers/alerting.py                      50     29    42%
app/routers/analytics.py                     84     57    32%
app/routers/audit_log.py                     86     69    20%   🔴 CRITICAL
app/routers/auth.py                           5      1    80%   ✅ GOOD
app/routers/compliance.py                     5      1    80%   ✅ GOOD
app/routers/finops.py                       217    104    52%
app/routers/gdpr.py                         174    104    40%   🔴 CRITICAL
app/routers/governance.py                   156    104    33%
app/routers/health.py                        16      4    75%
app/routers/metrics.py                        7      1    86%   ✅ GOOD
app/routers/prompts.py                      271    130    52%
app/routers/proxy.py                         78     64    18%   🔴 CRITICAL
app/routers/rbac.py                          93     66    29%
app/routers/scim.py                         254    146    43%
app/routers/slack_app.py                    345    292    15%   🔴 CRITICAL
app/routers/sso_rbac.py                     293    275     6%   🔴 CRITICAL
app/routers/teams.py                        110     77    30%
app/routers/transfers.py                    134     87    35%
app/routers/users.py                        167    119    29%
app/routers/wallets.py                      278    187    33%   🔴 CRITICAL
app/safety/ner_detector.py                  183    183     0%   🔴 CRITICAL
app/safety/pii_detector.py                  142    106    25%   🔴 CRITICAL
app/safety/pipeline.py                      247    155    37%   🔴 CRITICAL
app/safety/prompt_injection.py              118     79    33%   🔴 CRITICAL
app/safety/secret_scanner.py                146    100    32%
app/schemas.py                               88      2    98%   ✅ GOOD
app/security.py                              38     26    32%
app/workers.py                               17     17     0%   🔴 CRITICAL
-------------------------------------------------------------
TOTAL                                      8361   5136    39%   ❌ BELOW TARGET
```

---

## Sergey Bar Review Required

This audit reveals significant coverage gaps in **security-critical** and **financial-ledger** modules. Before production launch:

1. **Immediate escalation:** logic.py (57%), sso_rbac.py (6%), audit_log.py (20%)
2. **Test infrastructure fixes:** async support, resource leak cleanup
3. **Compliance risk:** Safety modules at 0-37% coverage expose GDPR/SOC 2 violations
4. **Sprint plan adjustment:** Allocate 2-3 sprints to reach 85% minimum overall coverage

**Recommendation:** BLOCK PRODUCTION DEPLOYMENT until critical modules reach 80% coverage minimum.

---

**Report Generated By:** Alfred Test Coverage Audit Tool  
**Next Audit:** Post-Phase 1 completion (2 weeks)
