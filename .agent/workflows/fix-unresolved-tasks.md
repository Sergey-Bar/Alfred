---
description: Fix all unresolved tasks from project management review
---

# Fix Unresolved Tasks Workflow

This workflow addresses all tasks identified in `reviews/Project Managment/Unresolved tasks.md`.

## Phase 1: High-Priority Backend Defects

### 1.1 Remove Duplicate FastAPI App Instantiation
- **File**: `src/backend/app/main.py`
- **Issue**: Lines 132-137 contain comments about redundant app instantiation
- **Action**: Verify no duplicate code exists, remove if found

### 1.2 Fix Debug Print Statements
- **Files**: `src/backend/app/integrations/manager.py`
- **Issue**: Lines 53 and 134 contain debug print() statements
- **Action**: Replace with proper logger calls

### 1.3 Consolidate Test Configuration
- **Files**: Multiple conftest.py files in different locations
- **Issue**: Path confusion due to scattered test directories
- **Action**: 
  - Review all conftest.py files
  - Consolidate into a single test structure
  - Update pyproject.toml pytest configuration

### 1.4 Update Dependencies
- **File**: Check for requirements.txt or pyproject.toml dependencies
- **Action**: Update outdated packages (rq, pytest-asyncio, pytest-cov)

### 1.5 Router Stubs Persistence
- **Files**: `routers/data_enrichment.py`, `routers/data_lineage.py`
- **Action**: Either implement persistence or remove stubs

### 1.6 Database Query Optimization
- **Action**: Find and optimize quota logic queries to use joins instead of multiple selects

### 1.7 Implement Lazy Router Loading
- **File**: `src/backend/app/main.py`
- **Status**: Already implemented! (lines 33-45)
- **Action**: Verify it's working correctly

### 1.8 Add Missing Logging
- **Action**: Review modules and add consistent logging

### 1.9 Fix Code Style Issues
- **Action**: Run ruff/black to fix tabs/spaces, trailing whitespace, import ordering

## Phase 2: Frontend Defects

### 2.1 Fix exportCSV.js
- **File**: Find and fix `exportCSV.js`
- **Actions**:
  - Add user feedback for no-data scenarios
  - Handle file errors
  - Validate CSV compatibility

### 2.2 Add Error Handling to Analytics Files
- **Files**: `usageAnalytics.js`, `metrics.js`, `dataQuality.js`, `dataLineage.js`
- **Actions**:
  - Add robust API error handling
  - Add input validation
  - Add pagination where appropriate

## Phase 3: DevOps/CI/Security

### 3.1 Remove Placeholder Credentials
- **Files**: CI workflows, docker-compose files
- **Action**: Search for and replace any placeholder credentials with secrets

### 3.2 Add Secret Scanning
- **File**: `.github/workflows/security-scan.yml` (if exists)
- **Action**: Add CI secret-scan step

### 3.3 Fix Docker Healthchecks
- **Files**: Docker compose files
- **Action**: Replace network calls with TCP checks or retry wrappers

## Phase 4: Tests & QA

### 4.1 Consolidate Test Directories
- **Current**: `qa/Backend`, `qa/QA/Backend`, `tests/`
- **Action**: Merge into single structure

### 4.2 Centralize Test Credentials
- **Action**: Move all test credentials to fixtures

### 4.3 Remove Debug Prints from Tests
- **Action**: Search and replace with logger calls

## Execution Order

1. Start with Phase 1 (Backend) - highest impact
2. Then Phase 3 (Security) - critical for production
3. Then Phase 4 (Tests) - improves development workflow
4. Finally Phase 2 (Frontend) - user-facing improvements

## Notes

- Each phase can be done incrementally
- Run tests after each major change
- Commit frequently with clear messages
- Update changelog as tasks are completed
