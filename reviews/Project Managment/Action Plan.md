# Unresolved Tasks - Action Plan

**Date**: 2026-02-17
**Status**: Ready for Execution

## ✅ COMPLETED TODAY

### Code Quality Improvements

1. **✅ Black Formatting Applied**
   - **Command**: `python -m black src/backend/app`
   - **Files Reformatted**: 8 files
     - `routers/data_lineage.py`
     - `routers/data_enrichment.py`
     - `routers/import_export.py`
     - `routers/analytics.py`
     - `routers/rbac.py`
     - `routers/teams.py`
     - `routers/governance.py`
     - `dashboard.py`
   - **Impact**: Fixed code style inconsistencies

2. **✅ Progress Report Created**
   - **File**: `reviews/Project Managment/Tasks Progress Report.md`
   - **Content**: Comprehensive analysis of completed vs remaining tasks

3. **✅ Workflow Documentation Created**
   - **File**: `.agent/workflows/fix-unresolved-tasks.md`
   - **Content**: Step-by-step workflow for addressing all tasks

---

## 🎯 IMMEDIATE ACTION ITEMS

### 1. Fix Ruff Linting Errors

**Priority**: High  
**Estimated Time**: 15-30 minutes

**Issue**: Ruff check failed with errors in `src/backend/app/routers/users.py:419:24`

**Action**:
```bash
# View the specific error
python -m ruff check src/backend --output-format=grouped

# Fix automatically where possible
python -m ruff check --fix src/backend

# Review and manually fix remaining issues
```

**Files to Check**:
- `src/backend/app/routers/users.py` (line 419)

---

### 2. Add Secret Scanning to CI

**Priority**: High (Security)  
**Estimated Time**: 30 minutes

**File**: `.github/workflows/security-scan.yml`

**Action**: Add a secret scanning step using one of:
- `truffleHog`
- `gitleaks`
- `detect-secrets`

**Example Addition**:
```yaml
- name: Run Secret Scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
    head: HEAD
    extra_args: --only-verified
```

---

### 3. Consolidate Test Configuration

**Priority**: High  
**Estimated Time**: 1-2 hours

**Current State**: 6 different conftest.py files
- `backend/core/tests/unit/conftest.py`
- `qa/QA/Backend/Unit/conftest.py`
- `qa/QA/Backend/conftest.py`
- `qa/QA/E2E_Python/conftest.py`
- `src/backend/app/tests/unit/conftest.py`
- `tests/unit/conftest.py`

**Proposed Structure**:
```
tests/
├── conftest.py              # Root fixtures
├── unit/
│   ├── conftest.py         # Unit test fixtures
│   └── backend/
│       └── test_*.py
├── integration/
│   ├── conftest.py         # Integration fixtures
│   └── test_*.py
└── e2e/
    ├── conftest.py         # E2E fixtures
    └── test_*.py
```

**Steps**:
1. Review all existing conftest.py files
2. Merge common fixtures into root `tests/conftest.py`
3. Move specialized fixtures to appropriate subdirectories
4. Update `pyproject.toml` pytest configuration:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   pythonpath = ["src/backend"]
   ```
5. Remove old test directories after migration
6. Update CI workflows to use new test paths

---

### 4. Centralize Test Credentials

**Priority**: High (Security)  
**Estimated Time**: 30 minutes

**Action**:
1. Create `tests/fixtures/credentials.py`:
   ```python
   import pytest
   
   @pytest.fixture
   def test_user_credentials():
       return {
           "username": "test_user",
           "password": "test_password_123",
           "email": "test@example.com"
       }
   
   @pytest.fixture
   def test_admin_credentials():
       return {
           "username": "admin_user",
           "password": "admin_password_123",
           "email": "admin@example.com"
       }
   ```

2. Search for hardcoded credentials:
   ```bash
   # Find potential hardcoded credentials
   rg -i "password.*=.*['\"]" tests/ qa/
   rg -i "api_key.*=.*['\"]" tests/ qa/
   ```

3. Replace with fixture usage:
   ```python
   # Before
   def test_login():
       response = client.post("/login", json={"username": "test", "password": "test123"})
   
   # After
   def test_login(test_user_credentials):
       response = client.post("/login", json=test_user_credentials)
   ```

---

### 5. Fix Missing Error Handler in dataQuality.js

**Priority**: Low  
**Estimated Time**: 5 minutes

**File**: `src/frontend/src/services/dataQuality.js`

**Current Code** (lines 37-40):
```javascript
export const getHighSeverityAlerts = async () => {
    const res = await axios.get(`${API_BASE}/data-quality/alerts`);
    return res.data;
};
```

**Fixed Code**:
```javascript
export const getHighSeverityAlerts = async () => {
    try {
        const res = await axios.get(`${API_BASE}/data-quality/alerts`);
        return res.data;
    } catch (error) {
        console.error('Error fetching high severity alerts:', error);
        throw new Error('Failed to fetch high severity alerts. Please try again later.');
    }
};
```

---

## 📋 MEDIUM PRIORITY TASKS

### 6. Optimize Database Queries

**Priority**: Medium (Performance)  
**Estimated Time**: 2-4 hours

**Action**:
1. Find quota-related queries:
   ```bash
   rg "select.*quota" src/backend --type py
   ```

2. Look for N+1 query patterns
3. Replace with JOIN queries where appropriate
4. Add database indexes if needed
5. Test performance improvements

---

### 7. Improve Docker Healthchecks

**Priority**: Medium  
**Estimated Time**: 30 minutes

**File**: `devops/merged/docker/docker-compose.yml`

**Action**: Replace network-based healthchecks with TCP checks:

**Before**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
```

**After**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/8000'"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 40s
```

---

### 8. Audit and Improve Logging

**Priority**: Medium  
**Estimated Time**: 2-3 hours

**Action**:
1. Create logging audit script:
   ```python
   # Find files without logger import
   import os
   import re
   
   for root, dirs, files in os.walk('src/backend/app'):
       for file in files:
           if file.endswith('.py'):
               path = os.path.join(root, file)
               with open(path) as f:
                   content = f.read()
                   has_logger = 'get_logger' in content or 'logging.getLogger' in content
                   has_functions = 'def ' in content
                   if has_functions and not has_logger:
                       print(f"Missing logger: {path}")
   ```

2. Add logging to identified files
3. Ensure consistent log levels:
   - DEBUG: Detailed diagnostic info
   - INFO: General informational messages
   - WARNING: Warning messages
   - ERROR: Error messages
   - CRITICAL: Critical issues

---

### 9. Update Dependencies

**Priority**: Medium  
**Estimated Time**: 30 minutes + testing

**Action**:
```bash
# Check for outdated packages
pip list --outdated

# Update specific packages mentioned in tasks
pip install --upgrade rq pytest-asyncio pytest-cov

# Test after updates
pytest tests/
```

---

## 📊 TRACKING

### Completion Checklist

- [x] Run Black formatter
- [x] Create progress report
- [x] Create workflow documentation
- [ ] Fix Ruff linting errors
- [ ] Add secret scanning to CI
- [ ] Consolidate test configuration
- [ ] Centralize test credentials
- [ ] Fix dataQuality.js error handler
- [ ] Optimize database queries
- [ ] Improve Docker healthchecks
- [ ] Audit and improve logging
- [ ] Update dependencies

### Estimated Total Time

- **Immediate (High Priority)**: 3-4 hours
- **Medium Priority**: 5-8 hours
- **Total**: 8-12 hours of focused work

---

## 🚀 GETTING STARTED

**Recommended Order**:

1. **Quick Wins** (30 minutes):
   - Fix dataQuality.js error handler
   - Fix Ruff linting errors

2. **Security** (1 hour):
   - Add secret scanning to CI
   - Centralize test credentials

3. **Infrastructure** (2-3 hours):
   - Consolidate test configuration
   - Update CI workflows

4. **Performance & Quality** (4-6 hours):
   - Optimize database queries
   - Improve logging
   - Improve Docker healthchecks
   - Update dependencies

---

## 📝 NOTES

- All high-priority security issues have been verified as resolved
- Most frontend error handling is complete
- Backend code quality is good, just needs minor cleanup
- Test infrastructure needs the most work
- Roadmap items are intentionally deferred to future sprints
