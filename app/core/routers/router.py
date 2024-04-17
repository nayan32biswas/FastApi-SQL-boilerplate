from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_home():
    return {"message": "Home Page..."}
