from typing import Dict, List

from fastapi import APIRouter

router = APIRouter()

# Example: Predefined KPI definitions
PREDEFINED_KPIS = [
    {
        "id": "user_growth",
        "name": "User Growth",
        "description": "Year-over-year user growth rate",
        "formula": "(users_this_year - users_last_year) / users_last_year * 100",
    },
    {
        "id": "retention",
        "name": "Enterprise Retention",
        "description": "Annual enterprise retention rate",
        "formula": "retained_enterprises / total_enterprises * 100",
    },
    {
        "id": "uptime",
        "name": "Platform Uptime",
        "description": "Platform uptime percentage",
        "formula": "(total_time - downtime) / total_time * 100",
    },
]


@router.get("/metrics/kpis", response_model=List[Dict])
def get_kpis():
    """Return all predefined KPIs and their metadata."""
    return PREDEFINED_KPIS


# To use: include_router(metrics.router) in main.py
