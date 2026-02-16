# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Scaffold a FastAPI router for Data Enrichment Pipelines, providing endpoints to register, run, and monitor enrichment jobs integrating external data sources.
# Why: Roadmap item 24 requires integration of external data sources for data enrichment.
# Root Cause: No API existed for managing or executing enrichment pipelines.
# Context: This router provides endpoints for registering pipelines, running jobs, and checking job status. Future: integrate with persistent storage, add scheduling, and support custom connectors. For advanced enrichment orchestration, consider using a more advanced model (Claude Opus).

from typing import List, Optional

# [AI GENERATED]
# Model: GitHub Copilot (GPT-5 mini)
# Logic: Replace in-memory stores with persistent SQLModel-backed tables for enrichment pipelines and jobs.
# Why: Prevents data loss on restart and enables auditability and querying in production.
# Root Cause: Demo in-memory lists were not durable; production requires DB persistence.
# Context: Uses `get_session` dependency; ensure DB migrations are applied (alembic) to create new tables.
from app.dependencies import get_session
from app.models import EnrichmentJobDB, EnrichmentPipelineDB
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlmodel import Session, select

router = APIRouter()


class EnrichmentPipeline(BaseModel):
    name: str
    description: Optional[str] = None
    source: str  # e.g., 'external_api', 'csv_upload'
    target_dataset: str
    config: Optional[dict] = None


class EnrichmentJob(BaseModel):
    pipeline_id: int
    status: str = "pending"


@router.post("/data-enrichment/pipelines", status_code=status.HTTP_201_CREATED)
def register_pipeline(pipeline: EnrichmentPipeline, session: Session = Depends(get_session)):
    db_obj = EnrichmentPipelineDB(
        name=pipeline.name,
        description=pipeline.description,
        source=pipeline.source,
        target_dataset=pipeline.target_dataset,
        config=pipeline.config,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return {"message": "Pipeline registered", "pipeline_id": db_obj.id}


@router.get("/data-enrichment/pipelines", response_model=List[EnrichmentPipeline])
def list_pipelines(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: Session = Depends(get_session)
):
    stmt = select(EnrichmentPipelineDB).offset(skip).limit(limit)
    rows = session.exec(stmt).all()
    return [EnrichmentPipeline(**r.dict(exclude={"id", "created_at"})) for r in rows]


@router.post("/data-enrichment/jobs", status_code=status.HTTP_201_CREATED)
def run_enrichment_job(job: EnrichmentJob, session: Session = Depends(get_session)):
    # Verify pipeline exists
    pipeline = session.get(EnrichmentPipelineDB, job.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    db_job = EnrichmentJobDB(pipeline_id=job.pipeline_id, status=job.status)
    session.add(db_job)
    session.commit()
    session.refresh(db_job)
    return {"message": "Job started", "job_id": db_job.id}


@router.get("/data-enrichment/jobs", response_model=List[EnrichmentJob])
def list_jobs(
    pipeline_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=2000),
    session: Session = Depends(get_session),
):
    stmt = select(EnrichmentJobDB).offset(skip).limit(limit)
    if pipeline_id:
        stmt = stmt.where(EnrichmentJobDB.pipeline_id == pipeline_id)
    rows = session.exec(stmt).all()
    return [EnrichmentJob(pipeline_id=r.pipeline_id, status=r.status) for r in rows]
