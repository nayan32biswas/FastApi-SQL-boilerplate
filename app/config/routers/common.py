from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/")
async def get_home():
    response = {"message": "Home Page..."}

    if settings.ENV != "prod":
        response["docs"] = f"{settings.API_HOST}/docs"
        response["redoc"] = f"{settings.API_HOST}/redoc"

    return response
