from typing import Dict, List

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/analytics/usage", response_model=List[Dict])
def get_usage_analytics(period: str = Query("7d", enum=["7d", "30d", "90d"])):
    # Example: Dummy data for usage analytics
    data = [
        {"date": "2026-02-15", "dataset": "users", "views": 120, "unique_users": 30},
        {"date": "2026-02-15", "dataset": "transactions", "views": 80, "unique_users": 22},
        {"date": "2026-02-14", "dataset": "users", "views": 110, "unique_users": 28},
    ]
    return data


# To use: include_router(usage_analytics.router) in main.py
