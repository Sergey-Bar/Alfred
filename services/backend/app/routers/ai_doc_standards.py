from typing import List

from fastapi import APIRouter

router = APIRouter()


@router.post("/docs/lint")
def lint_ai_docs(files: List[str]):
    # TODO: Run automated linting/review on AI-generated docs/code
    # - Check for required headers, rationale, and context
    return {"message": "Linting started", "files": files}


@router.get("/docs/lint/status")
def get_lint_status():
    # TODO: Return linting results and open issues
    return {"results": [], "open_issues": []}


# --- Future: Integrate with CI, doc generators, and review bots ---
