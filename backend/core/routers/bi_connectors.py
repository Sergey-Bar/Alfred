# """
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Implements BI Tools Integration API for managing connectors to Power BI, Tableau, and Looker. Provides endpoints to add, list, get, and remove BI connectors, and simulate connection tests. Supports storing connector configs and metadata.
# Why: Enables integration with external BI tools for analytics/reporting.
# Root Cause: No API for managing or testing BI tool connectors.
# Context: Used by backend for connector management, and by frontend for admin/config UI. Future: extend for OAuth, live sync, and connector health monitoring.
# Model Suitability: GPT-4.1 is suitable for FastAPI integration APIs; for advanced connector logic, consider Claude 3 or Gemini 1.5.
# """

import uuid

from fastapi import APIRouter, Body, Depends, HTTPException

from ..dependencies import require_admin

router = APIRouter(prefix="/v1/bi_connectors", tags=["BI Tools Integration"])


# --- In-memory connector store (for demo) ---
class BIConnector:
    def __init__(self, id, tool, name, config, created_by):
        self.id = id
        self.tool = tool  # "powerbi", "tableau", "looker"
        self.name = name
        self.config = config  # dict with connection/config info
        self.created_by = created_by


BI_CONNECTORS = {}


# --- API Endpoints ---
@router.post("/", dependencies=[Depends(require_admin)])
async def add_connector(
    tool: str = Body(...),
    name: str = Body(...),
    config: dict = Body(...),
    created_by: str = Body(...),
):
    connector_id = str(uuid.uuid4())
    connector = BIConnector(connector_id, tool, name, config, created_by)
    BI_CONNECTORS[connector_id] = connector
    return {"id": connector_id, "tool": tool, "name": name}


@router.get("/", dependencies=[Depends(require_admin)])
async def list_connectors():
    return [
        {"id": c.id, "tool": c.tool, "name": c.name, "created_by": c.created_by}
        for c in BI_CONNECTORS.values()
    ]


@router.get("/{connector_id}", dependencies=[Depends(require_admin)])
async def get_connector(connector_id: str):
    connector = BI_CONNECTORS.get(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found.")
    return {
        "id": connector.id,
        "tool": connector.tool,
        "name": connector.name,
        "config": connector.config,
        "created_by": connector.created_by,
    }


@router.delete("/{connector_id}", dependencies=[Depends(require_admin)])
async def remove_connector(connector_id: str):
    if connector_id not in BI_CONNECTORS:
        raise HTTPException(status_code=404, detail="Connector not found.")
    del BI_CONNECTORS[connector_id]
    return {"message": "Connector removed."}


@router.post("/test_connection", dependencies=[Depends(require_admin)])
async def test_connection(
    tool: str = Body(...),
    config: dict = Body(...),
):
    # Simulate connection test (always success for demo)
    return {"success": True, "tool": tool}
