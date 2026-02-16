# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Adds a backend endpoint to serve the GitOps onboarding documentation for programmatic access or frontend integration.
# Why: Enables the frontend or automation tools to fetch onboarding docs directly from the backend, supporting unified onboarding flows.
# Root Cause: No API existed to serve onboarding documentation; only static markdown was available.
# Context: This endpoint reads the docs/gitops_onboarding.md file and returns its content as plain text. Future: Add HTML/JSON rendering or versioning. For advanced doc rendering, consider GPT-4 Turbo or Claude Sonnet.

import os

from fastapi import APIRouter, Response, status

router = APIRouter()


@router.get("/onboarding/gitops", response_class=Response, status_code=status.HTTP_200_OK)
def get_gitops_onboarding():
    """Returns the GitOps onboarding documentation as plain text."""
    doc_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "..",
        "..",
        "docs",
        "gitops_onboarding.md",
    )
    doc_path = os.path.abspath(doc_path)
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content, media_type="text/markdown")
    except Exception as e:
        return Response(f"Error loading documentation: {e}", status_code=500)
