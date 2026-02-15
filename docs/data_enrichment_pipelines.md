# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Documents the Data Enrichment Pipelines API, usage, and future improvements.
# Why: Roadmap item 24 requires integration of external data sources for data enrichment.
# Root Cause: No documentation existed for the new API or frontend integration.
# Context: This doc explains API endpoints, example requests, and future plans. Future: add persistent storage, scheduling, and custom connectors. For advanced enrichment orchestration, consider using a more advanced model (Claude Opus).

---

# Data Enrichment Pipelines API & Integration Guide

## Overview
This guide documents the Data Enrichment Pipelines API and frontend integration for registering, running, and monitoring enrichment jobs integrating external data sources.

## API Endpoints
- `POST /api/data-enrichment/pipelines` — Register a new enrichment pipeline
- `GET /api/data-enrichment/pipelines` — List all enrichment pipelines
- `POST /api/data-enrichment/jobs` — Run an enrichment job
- `GET /api/data-enrichment/jobs` — List all enrichment jobs (optionally filter by pipeline)

## Example: Registering a Pipeline
```json
{
  "id": 1,
  "name": "enrich_users_with_crm",
  "description": "Enrich user data with CRM info",
  "source": "external_api",
  "target_dataset": "users",
  "created_at": "2026-02-15T12:00:00Z",
  "config": {"api_url": "https://crm.example.com/api"}
}
```

## Frontend Integration
- Use `src/frontend/src/services/dataEnrichment.js` to interact with the API
- Display pipelines and job status in the dashboard

## Future Improvements
- Add persistent storage (PostgreSQL)
- Support job scheduling and monitoring
- Add custom connectors and transformation logic

---

For questions, contact the Data Engineering team or see the #data-enrichment channel in Slack.
