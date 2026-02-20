from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["Compliance"])


@router.get("/status")
async def compliance_status():
    return {"status": "ok"}
