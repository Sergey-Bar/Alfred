# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Documents the Data Catalog & Metadata Management API, usage, and future improvements.
# Why: Roadmap item 23 requires a searchable catalog of datasets/fields for discoverability and governance.
# Root Cause: No documentation existed for the new API or frontend integration.
# Context: This doc explains API endpoints, example requests, and future plans. Future: add persistent storage, advanced search, and metadata versioning. For advanced catalog features, consider using a more advanced model (Claude Opus).

---

# Data Catalog & Metadata Management API & Integration Guide

## Overview
This guide documents the Data Catalog & Metadata Management API and frontend integration for registering, listing, and searching datasets and their metadata.

## API Endpoints
- `POST /api/data-catalog/datasets` — Register a new dataset
- `GET /api/data-catalog/datasets` — List all datasets
- `GET /api/data-catalog/search` — Search datasets by name or field

## Example: Registering a Dataset
```json
{
  "id": 1,
  "name": "users",
  "description": "User profile data",
  "fields": ["id", "name", "email"],
  "owner": "alice",
  "created_at": "2026-02-15T12:00:00Z",
  "tags": ["PII", "core"]
}
```

## Frontend Integration
- Use `src/frontend/src/services/dataCatalog.js` to interact with the API
- Display dataset catalog and search results in the dashboard

## Future Improvements
- Add persistent storage (PostgreSQL)
- Support advanced search and filtering
- Add metadata versioning and audit trails

---

For questions, contact the Data Engineering team or see the #data-catalog channel in Slack.
