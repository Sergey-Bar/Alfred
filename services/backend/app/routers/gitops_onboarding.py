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
