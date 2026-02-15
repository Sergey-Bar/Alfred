
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Adds a backend API endpoint to expose quotas, API keys, and LLM endpoint config for the admin settings panel.
# Why: Enables the frontend to fetch and display current quota policy, API keys, and LLM endpoints for admin review and configuration.
# Root Cause: No unified API existed for surfacing these settings to the frontend.
# Context: This router should be registered in main.py. Future: add PATCH/PUT for admin config updates.
# Model Suitability: For REST API patterns, GPT-4.1 is sufficient; for advanced config management, a more advanced model may be preferred.

from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..dependencies import get_session, require_admin
from ..config import settings

router = APIRouter(prefix="/v1", tags=["Admin Config"])

@router.get("/admin/config", dependencies=[Depends(require_admin)])
async def get_admin_config(session: Session = Depends(get_session)):
    """
    Returns quotas, API keys, and LLM endpoint config for admin settings panel.
    """
    return {
        "default_personal_quota": settings.default_personal_quota,
        "default_team_pool": settings.default_team_pool,
        "vacation_share_percentage": settings.vacation_share_percentage,
        "openai_api_key": bool(settings.openai_api_key),
        "anthropic_api_key": bool(settings.anthropic_api_key),
        "google_api_key": bool(settings.google_api_key),
        "azure_api_key": bool(settings.azure_api_key),
        "azure_api_base": settings.azure_api_base,
        "azure_api_version": settings.azure_api_version,
        "aws_access_key_id": bool(settings.aws_access_key_id),
        "aws_region": settings.aws_region,
        "vllm_api_base": settings.vllm_api_base,
        "tgi_api_base": settings.tgi_api_base,
        "ollama_api_base": settings.ollama_api_base,
    }
