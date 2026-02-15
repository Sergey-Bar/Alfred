"""
[AI GENERATED]
Model: GitHub Copilot (GPT-4.1)
Logic: Implements API router for custom analytics/reporting: create, list, run, schedule, and export custom reports (CSV/PDF/Excel). Admin-only endpoints. Uses in-memory store for demo; extend with DB and async workers for production.
Why: Enables advanced analytics, ad-hoc reporting, and scheduled exports for admins.
Root Cause: No unified API for custom/scheduled/exportable reports.
Context: Used by frontend custom report builder and scheduler. Future: add BI integration, permission checks, and audit logging.
Model Suitability: For REST API and prototyping, GPT-4.1 is sufficient; for advanced analytics, consider Claude 3 or Gemini 1.5.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List
from datetime import datetime
from uuid import uuid4
from ..schemas import (
    CustomReportCreate, CustomReportResponse, CustomReportRunRequest, CustomReportRunResult, ReportFormat
)
from ..dependencies import require_admin

router = APIRouter(prefix="/v1/reports", tags=["Custom Reports"])

# In-memory store for demo (replace with DB in production)
REPORTS = {}
RUNS = {}

@router.post("/", response_model=CustomReportResponse, dependencies=[Depends(require_admin)])
def create_report(report: CustomReportCreate):
    rid = str(uuid4())
    now = datetime.utcnow()
    REPORTS[rid] = {
        "id": rid,
        "name": report.name,
        "description": report.description,
        "query": report.query,
        "schedule": report.schedule,
        "format": report.format,
        "recipients": report.recipients,
        "created_at": now,
        "last_run": None,
        "status": "idle"
    }
    return CustomReportResponse(**REPORTS[rid])

@router.get("/", response_model=List[CustomReportResponse], dependencies=[Depends(require_admin)])
def list_reports():
    return [CustomReportResponse(**r) for r in REPORTS.values()]

@router.post("/{report_id}/run", response_model=CustomReportRunResult, dependencies=[Depends(require_admin)])
def run_report(report_id: str, req: CustomReportRunRequest):
    if report_id not in REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    run_id = str(uuid4())
    now = datetime.utcnow()
    # Simulate report execution (replace with real logic)
    output_url = f"/static/reports/{report_id}_{run_id}.{req.format or REPORTS[report_id]['format']}"
    RUNS[run_id] = {
        "report_id": report_id,
        "run_id": run_id,
        "status": "completed",
        "output_url": output_url,
        "started_at": now,
        "finished_at": now,
        "error": None
    }
    REPORTS[report_id]["last_run"] = now
    return CustomReportRunResult(**RUNS[run_id])

@router.get("/{report_id}", response_model=CustomReportResponse, dependencies=[Depends(require_admin)])
def get_report(report_id: str):
    if report_id not in REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    return CustomReportResponse(**REPORTS[report_id])

@router.delete("/{report_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_report(report_id: str):
    if report_id in REPORTS:
        del REPORTS[report_id]
    return Response(status_code=204)

@router.get("/{report_id}/runs", response_model=List[CustomReportRunResult], dependencies=[Depends(require_admin)])
def list_report_runs(report_id: str):
    return [CustomReportRunResult(**r) for r in RUNS.values() if r["report_id"] == report_id]
