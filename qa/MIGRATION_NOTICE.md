# ⚠️ MIGRATION NOTICE: Tests Moved to `tests/` Directory

**Date:** 2026-02-19  
**Status:** ✅ MIGRATION COMPLETE

---

## 📢 Important: Test Structure Consolidated

All tests have been **moved from `qa/` to `tests/`** to create a unified testing structure.

### What Changed

| Old Location              | New Location                 |
| ------------------------- | ---------------------------- |
| `qa/Backend/Unit/`        | `tests/unit/backend/`        |
| `qa/Backend/Integration/` | `tests/integration/backend/` |
| `qa/Backend/Performance/` | `tests/performance/backend/` |
| `qa/Backend/Security/`    | `tests/security/backend/`    |
| `qa/Frontend/Unit/`       | `tests/unit/frontend/`       |
| `qa/E2E/`                 | `tests/e2e/javascript/`      |
| `qa/E2E_Python/`          | `tests/e2e/python/`          |
| `qa/Performance/`         | `tests/performance/`         |
| `qa/results/`             | `tests/results/`             |
| `qa/scripts/`             | `tests/scripts/`             |
| `qa/*.md`                 | `tests/*.md`                 |

### Running Tests

**Old command (deprecated):**

```bash
pytest qa/Backend/Unit/ -v
```

**New command:**

```bash
pytest tests/unit/backend/ -v
```

### Why This Change?

1. **Eliminated Redundancy:** Both `qa/` and `tests/` existed with overlapping content
2. **Improved Organization:** Clear test type separation (unit, integration, e2e, performance, security)
3. **Better Discoverability:** Single source of truth for all tests
4. **Industry Standard:** Most projects use `tests/` as the canonical testing directory

### Documentation

See comprehensive testing documentation: [`tests/README.md`](../tests/README.md)

---

## ⏳ Deprecation Timeline

- **2026-02-19:** Tests consolidated to `tests/` directory
- **2026-03-01:** `qa/` directory will be archived
- **2026-04-01:** `qa/` directory will be removed

### Action Required

**For Developers:**

- Update local scripts to use `tests/` instead of `qa/`
- Update bookmarks/aliases pointing to old test locations
- Review and update any documentation referencing `qa/`

**For CI/CD:**

- Updated `pytest.ini` to point to `tests/` only
- GitHub Actions workflows updated to use new paths
- Coverage reports now generated from `tests/` directory

---

## 🔗 Quick Links

- **New Test Structure:** [`tests/`](../tests/)
- **Test Documentation:** [`tests/README.md`](../tests/README.md)
- **Test Inventory:** [`tests/TEST_INVENTORY.md`](../tests/TEST_INVENTORY.md)
- **Coverage Reports:** [`tests/results/`](../tests/results/)

---

**Questions?** Contact QA Lead or see `tests/README.md`

---

_This directory (`qa/`) is deprecated and will be removed in April 2026._
