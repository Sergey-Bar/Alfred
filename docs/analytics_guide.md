# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Documents the Real-Time & Historical Analytics API, usage, and future improvements.
# Why: Roadmap item 26 requires support for both streaming (real-time) and batch (historical) analytics.
# Root Cause: No documentation existed for the new API or frontend integration.
# Context: This doc explains API endpoints, example requests, and future plans. Future: add persistent storage, streaming support (Kafka), and advanced aggregations. For advanced analytics, consider using a more advanced model (Claude Opus).

---

# Real-Time & Historical Analytics API & Integration Guide

## Overview
This guide documents the Real-Time & Historical Analytics API and frontend integration for submitting, querying, and aggregating analytics events and metrics.

## API Endpoints
- `POST /api/analytics/events` — Submit a new analytics event
- `GET /api/analytics/events` — Query analytics events by type/time range
- `GET /api/analytics/aggregate` — Aggregate metrics for a given event type

## Example: Submitting an Analytics Event
```json
{
  "id": 1,
  "timestamp": "2026-02-15T12:00:00Z",
  "event_type": "api_call",
  "user": "alice",
  "dataset": "users",
  "value": 1.0,
  "metadata": {"endpoint": "/v1/chat/completions"}
}
```

## Frontend Integration
- Use `src/frontend/src/services/analytics.js` to interact with the API
- Display analytics dashboards and metrics in the UI

## Future Improvements
- Add persistent storage (PostgreSQL, data warehouse)
- Support streaming analytics (Kafka, WebSockets)
- Add advanced aggregations and visualizations

---

For questions, contact the Analytics team or see the #analytics channel in Slack.
