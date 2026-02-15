# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Adds documentation for test file naming conventions and frontend API service file documentation.
# Why: Ensures consistency and clarity in test and service file structure.
# Root Cause: Previous files lacked clear naming/documentation standards.
# Context: Update as new conventions or services are added. For advanced doc automation, consider Claude Sonnet or GPT-5.1-Codex.

## Test File Naming Conventions
- Backend: `test_*.py` (unit, integration, performance)
- Frontend: `*.test.jsx` (unit), `*.spec.js` (E2E)
- E2E: `*.spec.js` (Playwright)

> All test files must follow these patterns for discoverability and CI/CD integration.

## Frontend API Service File Documentation
- Each service file should include:
  - Purpose and endpoints covered
  - Example usage
  - Error handling and retry logic
  - AI-generated code comment header if applicable

> Add docstrings or JSDoc comments to all service files for clarity.
