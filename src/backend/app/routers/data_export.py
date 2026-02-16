# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Provides a backend FastAPI router for exporting analytics data via API (CSV, JSON, etc.).
# Why: Enables programmatic access to analytics data for external tools and partners.
# Root Cause: No API endpoint for data export existed.
# Context: Extend this with authentication, filtering, and export formats as needed.
# Model Suitability: For advanced export logic, consider GPT-4 Turbo or Claude Sonnet.

import csv
import io
from typing import Optional

from fastapi import APIRouter, Query, Response

router = APIRouter()


@router.get("/export/analytics")
def export_analytics(format: Optional[str] = Query("csv", enum=["csv", "json"])):
    # Example: Dummy data for export
    data = [
        {"date": "2026-02-15", "users": 100, "tokens": 5000},
        {"date": "2026-02-14", "users": 95, "tokens": 4800},
    ]
    if format == "json":
        return data
    # Default: CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return Response(content=output.getvalue(), media_type="text/csv")


# To use: include_router(data_export.router) in main.py
