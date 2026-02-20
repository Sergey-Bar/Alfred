from fastapi import APIRouter

router = APIRouter()


@router.get("/auth")
async def auth_root():
    return {"message": "Auth Router"}
