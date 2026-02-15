# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Provides a backend structure for a KPI/metric library with predefined and customizable metrics.
# Why: Enables standardized, extensible business metric definitions for analytics and reporting.
# Root Cause: No central place for metric logic or API exposure.
# Context: Extend this module with more metrics and business logic as needed. Integrate with DB for dynamic metrics.
# Model Suitability: For advanced metric computation, consider GPT-4 Turbo or Claude Sonnet.

from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

# Example: Predefined KPI definitions
PREDEFINED_KPIS = [
    {"id": "user_growth", "name": "User Growth", "description": "Year-over-year user growth rate", "formula": "(users_this_year - users_last_year) / users_last_year * 100"},
    {"id": "retention", "name": "Enterprise Retention", "description": "Annual enterprise retention rate", "formula": "retained_enterprises / total_enterprises * 100"},
    {"id": "uptime", "name": "Platform Uptime", "description": "Platform uptime percentage", "formula": "(total_time - downtime) / total_time * 100"},
]

@router.get("/metrics/kpis", response_model=List[Dict])
def get_kpis():
    """Return all predefined KPIs and their metadata."""
    return PREDEFINED_KPIS

# To use: include_router(metrics.router) in main.py
